class FastANIException(Exception):
    def __init__(self, message=''):
        Exception.__init__(self, message)


class FastANIVersionUnknown(FastANIException):
    def __init__(self, message=''):
        FastANIException.__init__(self, message)


class FastANIParametersInvalid(FastANIException):
    def __init__(self, message=''):
        FastANIException.__init__(self, message)


class FastANIFileNotFound(FastANIException):
    def __init__(self, message=''):
        FastANIException.__init__(self, message)
