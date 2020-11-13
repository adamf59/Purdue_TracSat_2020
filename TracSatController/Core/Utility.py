"""
Utility defines all of our abstract or object-oriented classes
"""
__author__ = "Adam Frank"
__version__ = 1.0

from abc import abstractmethod
from threading import Thread, Event

from TracSatController.Core import Logging
from TracSatController.Core.TracSatError import SubsystemInitializationFailure, TargetNonExistentError, \
    TargetAlreadyReachedError


class Subsystem:
    """
    A dynamic, abstract class that can be used for

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
        self._is_halted = False
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
        pass

    @abstractmethod
    def after_halt(self):
        """
        Executes after the subsystem has been halted by the halt() function, or any internal caller.
        """
        pass

    @abstractmethod
    def on_halt(self):
        """
        Executes when the subsystem is halted. This function will run BEFORE the subsystem has fully stopped normal
        execution. It is called when the halt() function is called.
        """
        pass

    @abstractmethod
    def after_shutdown(self):
        """
        Executes after the subsystem has been shutdown and the execution function is no longer running.
        """
        pass

    @abstractmethod
    def on_shutdown(self):
        """
        Executes immediately when the shutdown() method is called. Keep in mind that the execution loop may still have
        one iteration left at the time of execution.
        """
        pass

    @abstractmethod
    def on_resume(self):
        """
        Executes immediately before the subsystem is resumed after being halted.
        """

    def shutdown(self):
        """
        Commands this subsystem to shutdown. A shutdown subsystem CANNOT be restarted.
        """
        self._is_shutdown = True
        self._is_halted = True  # Not entirely necessary, but a shutdown subsystem is also halted.

    def halt(self):
        """
        Halt the subsystem in it's current state. A halted subsystem can be restarted with resume()

        """
        self._is_halted = True
        self.on_halt()

    def resume(self):
        """
        Resume the subsystem if it is currently halted.
        :return:
        """
        self._is_halted = False
        self.on_resume

    def start(self):
        """
        Starts the subsystem's execution cycle (the execution function loop). Can only be called once
        :return:
        """
        if not self._subsystem_startup_did_occur:
            self.__initialize_worker_thread(with_name=self.subsystem_name)
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

    def __worker(self):
        """
        Internal function for handling the execution worker states. Do not call.
        """
        if not self.initialize():
            raise SubsystemInitializationFailure(self.subsystem_name)

        while not self._is_shutdown:
            if not self._is_halted:
                self.execute()

    def __initialize_worker_thread(self, with_name=None, with_daemon=True):
        """
        Internal function for initializing the worker process and event/interrupt handlers. Do not call.
        :param with_name: The name of the worker thread
        :param with_daemon: Whether this worker thread should act as a daemon to the master thread
        :return: Nothing :)
        """
        self._worker_thread = Thread(name=with_name, daemon=with_daemon, target=self.__worker)


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
