from logging import getLogger, StreamHandler, DEBUG, WARNING

class Logging:

    def __init__(self, verbose):
        self.logger = getLogger(__name__)
        handler = StreamHandler()
        level = WARNING
        if verbose:
            level = DEBUG
        handler.setLevel(level)
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.propagate = False
        return logger