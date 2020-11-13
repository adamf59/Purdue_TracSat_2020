class SubsystemInitializationFailure(Exception):
    def __init__(self, subsystem_name):
        super().__init__(subsystem_name + " failed to start due to a initialization condition not being met.")


class TargetNonExistentError(Exception):
    def __init__(self, target_name):
        super().__init__("A target with the name " + target_name + " does not exist. Did you forget to register it?")


class TargetAlreadyReachedError(Exception):
    def __init__(self, target_name):
        super().__init__("An attempt was made to reach the target " + target_name + " when it was already reached.")
