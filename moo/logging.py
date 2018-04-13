from logging import getLogger, StreamHandler


class Logging:

    def __init__(self, name):
        self.logger = getLogger(name)
        self.handler = StreamHandler()
        self.logger.addHandler(self.handler)
        self.logger.propagate = False
        self.SetLevel("INFO")

    def SetLevel(self, lvl):
        if lvl != 'CRITICAL' and lvl != 'ERROR' and lvl != 'WARNING' and lvl != 'INFO' and lvl != 'DEBUG':
            self.logger.warning("Cannot set loglevel: %s" % lvl)
            self.logger.warning("loglevel set as INFO")
            lvl = 'INFO'
        self.handler.setLevel(lvl)
        self.logger.setLevel(lvl)

    def getLogger(self):
        return self.logger
