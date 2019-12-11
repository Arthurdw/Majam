class Majam(Exception):
    """Base exception class for Majam"""
    pass


class UnknownError(Majam):
    """When an unknown exception occurs, this should never happen!"""
    pass

