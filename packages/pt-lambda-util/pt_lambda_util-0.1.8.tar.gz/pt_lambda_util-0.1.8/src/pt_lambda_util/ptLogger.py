import logging

root_logger = logging.getLogger()
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
logging.basicConfig(format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s', level=logging.INFO)


class PTLogger(object):
    def __init__(self, name):
        self.name = name

    def get_logger(self):
        return logging.getLogger(self.name)
