from time import sleep

from TracSatController.Core.Foundation import ContinuousSubsystem, Requires


class TestSubsystem(ContinuousSubsystem):

    def __init__(self):
        super().__init__("TestSubsystem")
        # Put targets here

    def initialize(self):
        return True

    def execute(self):
        pass

    def after_halt(self):
        print("after halt")

    def on_halt(self):
        print("on halt")

    def after_shutdown(self):
        pass

    def on_shutdown(self):
        pass

    def on_resume(self):
        pass


if __name__ == '__main__':
    x = TestSubsystem()
    x.start()
    x.halt()
    sleep(1)
    x.resume()
    sleep(0.001)
    x.halt()
    sleep(2)

