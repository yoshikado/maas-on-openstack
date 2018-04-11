from logging import getLogger, StreamHandler, DEBUG, WARNING


class Logging:

    def __init__(self, name):
        self.logger = getLogger(name)
        self.handler = StreamHandler()
        self.logger.addHandler(self.handler)
        self.logger.propagate = False

    def SetLevel(self, level):
        if level == 'DEBUG':
            lv = DEBUG
        else:
            lv = WARNING
        self.handler.setLevel(lv)
        self.logger.setLevel(lv)

    def getLogger(self):
        return self.logger