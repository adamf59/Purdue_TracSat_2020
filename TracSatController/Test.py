from time import sleep

from TracSatController.Core.Foundation import ContinuousSubsystem, Requires, SingleExecutionSubsystem


class TestSubsystem(SingleExecutionSubsystem):

    def __init__(self):
        super().__init__("TestSubsystem")
        # Put targets here

    def initialize(self):
        return True

    def execute(self):
        print("h")

    def after_shutdown(self):
        print("Shutdown Complete!")

    def on_shutdown(self):
        print("On Shutdown!")


if __name__ == '__main__':
    x = TestSubsystem()
    x.start()
    sleep(1)

