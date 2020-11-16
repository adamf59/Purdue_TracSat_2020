"""
Utility defines all of our abstract or object-oriented classes
"""
__author__ = "Adam Frank"
__version__ = 1.0

from abc import abstractmethod
from threading import Thread, Event
from time import sleep

from TracSatController.Core import Logging
from TracSatController.Core.TracSatError import SubsystemInitializationFailure, TargetNonExistentError, \
    TargetAlreadyReachedError


class SubsystemFoundation:
    """
    A dynamic, abstract class that can be used for small, independent systems that can interact with each other, while
    still being systematically separate (isolated processes).
    """

    def __init__(self, subsystem_name):
        """
        Create a new Subsystem using the given name. It is strongly recommended that this is unique. The sequence of
        events after starting a subsystem are as follows:

        1. Subsystem created and initial configuration.
        2. Subsystem on_intialize function called
        3. Execution worker starts (execute function)
        4. Subsystem responds to halt(), resume(), or shutdown().

        """
        self.subsystem_name = subsystem_name
        self._is_shutdown = False
        self._subsystem_startup_did_occur = False
        self._worker_thread = None  # type: Thread

    def get_subsystem_name(self) -> str:
        """
        Gets the name of this subsystem.

        :return: The name of this subsystem, as a string.
        """
        return self.subsystem_name

    @abstractmethod
    def initialize(self) -> bool:
        """
        The initialization function is designed to be run immediately before the subsystem begins looping the execute
        function. If your initialize function has determined that the subsystem should not be started, then leave
        the function early by returning False. If your initialization is successful, then return True.

        :return: True if the subsystem should begin execution, False if otherwise.
        """

    @abstractmethod
    def execute(self):
        """
        The execute function is responsible for being run continuously (a loop) while the subsystem has not been shut
        down and is not halted.
        :return:
        """

    def shutdown(self):
        """
        Commands this subsystem to shutdown. A shutdown subsystem CANNOT be restarted.
        """
        self.on_shutdown()
        self._is_shutdown = True

    @abstractmethod
    def on_shutdown(self):
        """
        Executes immediately when the shutdown() method is called. Keep in mind that the execution loop may still have
        one iteration left at the time of execution.
        """

    @abstractmethod
    def after_shutdown(self):
        """
        Executes after the subsystem has been shutdown and the execution function is no longer running. These will be
        the last instructions executed in the subsystem thread.
        """

    def start(self):
        """
        Starts the subsystem's execution cycle (the execution function loop). Can only be called once
        :return:
        """
        if not self._subsystem_startup_did_occur:
            self._initialize_worker_thread(with_name=self.subsystem_name)
            self._subsystem_startup_did_occur = True
            self._worker_thread.start()

        else:
            return False

    def acquire_lock(self):
        """
        Block the thread this function is called from on this subsystem's worker, thus, the block will not be released
        until this subsystem has been shutdown.
        """
        self._worker_thread.join()

    @abstractmethod
    def _worker(self):
        pass

    def _initialize_worker_thread(self, with_name=None, with_daemon=True):
        """
        Internal function for initializing the worker process and event/interrupt handlers. Do not call.
        :param with_name: The name of the worker thread
        :param with_daemon: Whether this worker thread should act as a daemon to the master thread
        :return: Nothing :)
        """
        self._worker_thread = Thread(name=with_name, daemon=with_daemon, target=self._worker)


class ContinuousSubsystem(SubsystemFoundation):
    """
    A dynamic, abstract class that can be used for small, independent systems that can interact with each other, while
    still being systematically separate (isolated processes). A continuous subsystem has a function that runs in a loop,
    useful for repetitive, reaction-based code, like feedback and control loops.
    """

    def __init__(self, subsystem_name):
        self._is_halted = False
        super().__init__(subsystem_name)

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def execute(self):
        pass

    def shutdown(self):
        self._is_halted = True  # Not entirely necessary, but a shutdown subsystem is also halted.
        super().shutdown()

    @abstractmethod
    def on_shutdown(self):
        pass

    @abstractmethod
    def after_shutdown(self):
        pass

    def halt(self):
        """
        Halt the subsystem in it's current state. A halted subsystem can be restarted with resume()
        """
        Requires.register(self.subsystem_name + ".halt")
        self.on_halt()
        self._is_halted = True
        Requires.target(self.subsystem_name + ".halt")
        Requires.clear_target(self.subsystem_name + ".halt")

        self.after_halt()

    @abstractmethod
    def on_halt(self):
        """
        Executes when the subsystem is halted. It is called when the halt() function is called.
        This function will run BEFORE the subsystem has fully stopped normal execution.
        The execution function WILL be running when this is executed.
        """
        pass

    @abstractmethod
    def after_halt(self):
        """
        Executes after the subsystem has been halted by the halt() function, or any internal caller. The execution
        function will NOT be running when this is executed.
        """
        pass

    def resume(self):
        """
        Resume the subsystem if it is currently halted.
        :return:
        """
        self.on_resume()
        self._is_halted = False

    @abstractmethod
    def on_resume(self):
        """
        Executes immediately before the subsystem is resumed after being halted.
        """
        pass

    def _worker(self):
        """
        Internal function for handling the execution worker states. Do not call.
        """
        halt_fulfilled = False

        if not self.initialize():
            raise SubsystemInitializationFailure(self.subsystem_name)

        while not self._is_shutdown:
            if not self._is_halted:
                if halt_fulfilled:
                    halt_fulfilled = False
                self.execute()
            else:
                if not halt_fulfilled:
                    Requires.reach_target(self.subsystem_name + ".halt")
                    halt_fulfilled = True
        self.shutdown()
        self.after_shutdown()


class SingleExecutionSubsystem(SubsystemFoundation):
    """
    A dynamic, abstract class that can be used for small, independent systems that can interact with each other, while
    still being systematically separate (isolated processes). A single execution subsystem will only have its execute
    method run once, after which it will shutdown.
    """
    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def on_shutdown(self):
        pass

    @abstractmethod
    def after_shutdown(self):
        pass

    def _worker(self):
        if not self.initialize():
            raise SubsystemInitializationFailure(self.subsystem_name)
        self.execute()
        self.shutdown()
        self.after_shutdown()


class Requires:
    _target_registry = []

    @classmethod
    def target(cls, target_name, wait=True) -> bool:

        for tgt in cls._target_registry:
            if type(tgt) == Target and tgt.target_name == target_name:
                if tgt.is_reached():
                    return True
                elif wait:
                    tgt.block()
                    return True
                else:
                    return False

        raise TargetNonExistentError(target_name)

    @classmethod
    def register(cls, target_name):
        # TODO Does not check for conflicting target names
        cls._target_registry.append(Target(target_name))

    @classmethod
    def reach_target(cls, target_name) -> bool:
        for tgt in cls._target_registry:
            if type(tgt) == Target and tgt.target_name == target_name:
                if tgt.is_reached():
                    raise TargetAlreadyReachedError(target_name)
                else:
                    tgt.reach()
                    return True

        raise TargetNonExistentError(target_name)

    @classmethod
    def clear_target(cls, target_name):
        for tgt in cls._target_registry:
            if type(tgt) == Target and tgt.target_name == target_name:
                cls._target_registry.remove(tgt)


class Target:

    def __init__(self, target_name):
        self.target_name = target_name
        self.target_lock = Event()

    def reach(self):
        Logging.log("[OK] Reached target: " + self.target_name)
        self.target_lock.set()

    def is_reached(self) -> bool:
        return self.target_lock.is_set()

    def block(self):
        self.target_lock.wait()
