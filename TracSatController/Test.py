from time import sleep

from TracSatController.Core.Utility import Subsystem, Requires


class TestSubsystem(Subsystem):

    def __init__(self):
        super().__init__("TestSubsystem")
        Requires.register("network.start")

    def initialize(self):
        print("Checking for network.start target...")
        Requires.target("network.start")
        print("Reached target!")
        return True

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

    def on_resume(self):
        pass


if __name__ == '__main__':
    x = TestSubsystem()
    x.start()
    sleep(5)
    Requires.reach_target("network.start")
    sleep(5)
    # sleep(5)
    # x.shutdown()
    # sleep(3)
