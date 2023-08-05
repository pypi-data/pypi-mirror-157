class ACLTestError(Exception):
    pass


class CommandExecError(ACLTestError):
    pass


class ACLCheckError(ACLTestError):
    pass


class ACLNoCheckAttributeError(ACLTestError):
    pass
