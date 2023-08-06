import logging

from milla_tdf.config import TradingFrameWorkConfig


def initLoad():
    
    logging.getLogger('selenium').setLevel('ERROR')
    logging.getLogger('urllib3').setLevel('ERROR')
    logging.basicConfig(
        level=TradingFrameWorkConfig.log_level, format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

    logging.addLevelName(
        logging.INFO, "\033[1;36m%s\033[1;0m" % logging.getLevelName(logging.INFO))

    logging.addLevelName(
        logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))

    logging.addLevelName(
        logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
