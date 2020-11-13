"""
Utility defines all of our abstract or object-oriented classes
"""
__author__ = "Adam Frank"
__version__ = 1.0

from abc import abstractmethod
from threading import Thread


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
    def on_initialize(self):
        """
        The on_initialize function will be run when the subsystem initialization is complete, and before the execution
        function is started.
        """
        pass

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
        :return:
        """
        pass

    def shutdown(self):
        """
        Commands this subsystem to shutdown. A shutdown subsystem CANNOT be restarted.

        """
        pass

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

    def start(self):
        """
        Starts the subsystem's execution cycle (the execution function loop). Can only be called once
        :return:
        """
        if not self._subsystem_startup_did_occur:
            self.__initialize_worker_thread()
            self._subsystem_startup_did_occur = True
            self._worker_thread.start()

        else:
            return False

    def aquire_lock(self):
        """
        Block the thread this function is called from on this subsystem's worker, thus, the block will not be released
        until this subsystem has been shutdown.
        """
        self._worker_thread.join()

    def __worker(self):
        """
        Internal function for handling the execution worker states. Do not call.
        """
        while not self._is_shutdown:

            while not self._is_halted:

                self.execute()

    def __initialize_worker_thread(self, with_name=None, with_daemon=True):
        """
        Internal function for intializing the worker process and event/interrupt handlers. Do not call.
        :param with_name: The name of the worker thread
        :param with_daemon: Whether this worker thread should act as a daemon to the master thread
        :return: Nothing :)
        """
        self._worker_thread = Thread(name=with_name, daemon=with_daemon, target=self.__worker)
