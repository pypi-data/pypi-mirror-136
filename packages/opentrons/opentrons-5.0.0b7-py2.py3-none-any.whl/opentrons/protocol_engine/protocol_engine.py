"""ProtocolEngine class definition."""
from typing import Optional, Callable
from asyncio import create_task, Task

from opentrons.hardware_control.types import HardwareEvent
from opentrons.protocols.models import LabwareDefinition
from opentrons.hardware_control import HardwareControlAPI
from opentrons.thread_async_queue import ThreadAsyncQueue, QueueClosed

from .resources import ModelUtils
from .commands import (
    Command,
    CommandCreate,
)
from .types import LabwareOffset, LabwareOffsetCreate
from .execution import QueueWorker, create_queue_worker, HardwareStopper
from .state import StateStore, StateView
from .plugins import AbstractPlugin, PluginStarter
from .actions import (
    ActionDispatcher,
    PlayAction,
    PauseAction,
    PauseSource,
    StopAction,
    FinishAction,
    FinishErrorDetails,
    QueueCommandAction,
    AddLabwareOffsetAction,
    AddLabwareDefinitionAction,
    HardwareStoppedAction,
    HardwareEventAction,
)


class ProtocolEngine:
    """Main ProtocolEngine class.

    A ProtocolEngine instance holds the state of a protocol as it executes,
    and manages calls to a command executor that actually implements the logic
    of the commands themselves.
    """

    def __init__(
        self,
        hardware_api: HardwareControlAPI,
        state_store: StateStore,
        action_dispatcher: Optional[ActionDispatcher] = None,
        plugin_starter: Optional[PluginStarter] = None,
        queue_worker: Optional[QueueWorker] = None,
        model_utils: Optional[ModelUtils] = None,
        hardware_stopper: Optional[HardwareStopper] = None,
    ) -> None:
        """Initialize a ProtocolEngine instance.

        This constructor does not inject provider implementations. Prefer the
        ProtocolEngine.create factory classmethod.
        """
        self._state_store = state_store
        self._model_utils = model_utils or ModelUtils()

        self._action_dispatcher = action_dispatcher or ActionDispatcher(
            sink=self._state_store
        )
        self._plugin_starter = plugin_starter or PluginStarter(
            state=self._state_store,
            action_dispatcher=self._action_dispatcher,
        )
        self._queue_worker = queue_worker or create_queue_worker(
            hardware_api=hardware_api,
            state_store=self._state_store,
            action_dispatcher=self._action_dispatcher,
        )
        self._hardware_stopper = hardware_stopper or HardwareStopper(
            hardware_api=hardware_api, state_store=state_store
        )
        self._hw_event_watcher: Optional[
            Callable[[], None]
        ] = hardware_api.register_callback(self.hardware_event_handler)

        # TODO: The constructor isn't the best place to spawn background tasks
        #  like this (async queue) one since if a part of this init fails,
        #  then the background task needs to be cleaned up.. but, it will need to happen
        #  in an async method, which the init function isn't.
        self._hw_actions_to_dispatch = ThreadAsyncQueue[HardwareEventAction]()
        self._hw_action_dispatching_task: Task[None] = create_task(
            self._dispatch_all_actions()
        )
        self._queue_worker.start()

    @property
    def state_view(self) -> StateView:
        """Get an interface to retrieve calculated state values."""
        return self._state_store

    def add_plugin(self, plugin: AbstractPlugin) -> None:
        """Add a plugin to the engine to customize behavior."""
        self._plugin_starter.start(plugin)

    def hardware_event_handler(self, hw_event: HardwareEvent) -> None:
        """Update the runner on hardware events."""
        action = HardwareEventAction(event=hw_event)
        # todo: Instead of using a queue, use something
        # blocking, like anyio.from_thread_run_sync().
        # That way, we won't have to manage a background task,
        # and deterministic unit testing will be easier.
        self._hw_actions_to_dispatch.put(action)

    def _remove_hardware_event_watcher(self) -> None:
        if self._hw_event_watcher and callable(self._hw_event_watcher):
            self._hw_event_watcher()
            self._hw_event_watcher = None

    def play(self) -> None:
        """Start or resume executing commands in the queue."""
        # TODO(mc, 2021-08-05): if starting, ensure plungers motors are
        # homed if necessary
        action = PlayAction()
        self._state_store.commands.raise_if_paused_by_blocking_door()
        self._state_store.commands.raise_if_stop_requested()
        self._action_dispatcher.dispatch(action)
        self._queue_worker.start()

    def pause(self) -> None:
        """Pause executing commands in the queue."""
        action = PauseAction(source=PauseSource.CLIENT)
        self._state_store.commands.raise_if_stop_requested()
        self._action_dispatcher.dispatch(action)

    def add_command(self, request: CommandCreate) -> Command:
        """Add a command to the `ProtocolEngine`'s queue.

        Arguments:
            request: The command type and payload data used to construct
                the command in state.

        Returns:
            The full, newly queued command.
        """
        command_id = self._model_utils.generate_id()
        action = QueueCommandAction(
            request=request,
            command_id=command_id,
            # TODO(mc, 2021-12-13): generate a command key from params and state
            # https://github.com/Opentrons/opentrons/issues/8986
            command_key=command_id,
            created_at=self._model_utils.get_timestamp(),
        )
        self._action_dispatcher.dispatch(action)
        return self._state_store.commands.get(command_id)

    async def add_and_execute_command(self, request: CommandCreate) -> Command:
        """Add a command to the queue and wait for it to complete.

        The engine must be started by calling `play` before the command will
        execute. You only need to call `play` once.

        Arguments:
            request: The command type and payload data used to construct
                the command in state.

        Returns:
            The completed command, whether it succeeded or failed.
        """
        command = self.add_command(request)
        await self._state_store.wait_for(
            condition=self._state_store.commands.get_is_complete,
            command_id=command.id,
        )
        return self._state_store.commands.get(command.id)

    async def stop(self) -> None:
        """Stop execution immediately, halting all motion and cancelling future commands.

        After an engine has been `stop`'ed, it cannot be restarted.

        After a `stop`, you must still call `finish` to give the engine a chance
        to clean up resources and propagate errors.
        """
        self._state_store.commands.raise_if_stop_requested()
        self._action_dispatcher.dispatch(StopAction())
        self._queue_worker.cancel()
        await self._hardware_stopper.do_halt()

    # TODO(mc, 2021-12-27): commands.get_all_complete not yet implemented
    async def wait_until_complete(self) -> None:
        """Wait until there are no more commands to execute.

        This will happen if all commands are executed or if one command fails.
        """
        await self._state_store.wait_for(
            condition=self._state_store.commands.get_all_complete
        )

    async def finish(
        self,
        error: Optional[Exception] = None,
        drop_tips_and_home: bool = True,
    ) -> None:
        """Gracefully finish using the ProtocolEngine, waiting for it to become idle.

        The engine will finish executing its current command (if any),
        and then shut down. After an engine has been `finished`'ed, it cannot
        be restarted.

        This method should not raise, but if any exceptions happen during
        execution that are not properly caught by the CommandExecutor, they
        will be raised here.

        Arguments:
            error: An error that caused the stop, if applicable.
            drop_tips_and_home: Whether to home and drop tips as part of cleanup.
        """
        if error:
            error_details: Optional[FinishErrorDetails] = FinishErrorDetails(
                error_id=self._model_utils.generate_id(),
                created_at=self._model_utils.get_timestamp(),
                error=error,
            )
        else:
            error_details = None

        self._action_dispatcher.dispatch(FinishAction(error_details=error_details))

        try:
            await self._queue_worker.join()

        finally:
            # TODO: We should use something like contextlib.AsyncExitStack so that we
            #  can handle resource cleanups gracefully instead of needing to use nested
            #  try excepts for multiple resources.
            await self._hardware_stopper.do_stop_and_recover(drop_tips_and_home)
            self._action_dispatcher.dispatch(HardwareStoppedAction())
            try:
                self._hw_actions_to_dispatch.done_putting()
            except QueueClosed:
                # Accounting for finish being called twice.
                pass

            # While we are awaiting the action dispatching task to finish, it might
            # still be dispatching hw actions, so it could affect the engine state..
            # BUT, since for now it is only handling door event action which
            # only sets the Queue to inactive, we are OK. If in the future we add more
            # actions that could be disruptive to the engine even after it is stopped
            # then we will need to rethink how to handle this shutdown.
            await self._hw_action_dispatching_task
            self._remove_hardware_event_watcher()
            await self._plugin_starter.stop()

    def add_labware_offset(self, request: LabwareOffsetCreate) -> LabwareOffset:
        """Add a new labware offset and return it.

        The added offset will apply to subsequent `LoadLabwareCommand`s.

        To retrieve offsets later, see `.state_view.labware`.
        """
        labware_offset_id = self._model_utils.generate_id()
        created_at = self._model_utils.get_timestamp()
        self._action_dispatcher.dispatch(
            AddLabwareOffsetAction(
                labware_offset_id=labware_offset_id,
                created_at=created_at,
                request=request,
            )
        )
        return self.state_view.labware.get_labware_offset(
            labware_offset_id=labware_offset_id
        )

    def add_labware_definition(self, definition: LabwareDefinition) -> None:
        """Add a labware definition to the state for subsequent labware loads."""
        self._action_dispatcher.dispatch(
            AddLabwareDefinitionAction(definition=definition)
        )

    async def _dispatch_all_actions(self) -> None:
        """Dispatch all actions to the `ProtocolEngine`.

        Exits only when `self._actions_to_dispatch` is closed
        (or an unexpected exception is raised).
        """
        async for action in self._hw_actions_to_dispatch.get_async_until_closed():
            self._action_dispatcher.dispatch(action)
