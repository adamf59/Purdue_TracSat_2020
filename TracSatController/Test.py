from time import sleep

from TracSatController.Core.Utility import Subsystem

class TestSubsystem(Subsystem):

    def __init__(self):
        super().__init__("TestSubsystem")

    def on_initialize(self):
        pass

    def execute(self):
        print("hello")
        sleep(1)

    def after_halt(self):
        pass

    def on_halt(self):
        pass

    def after_shutdown(self):
        pass

    def on_shutdown(self):
        pass


if __name__ == '__main__':
    x = TestSubsystem()
    x.start()
    x.aquire_lock()
