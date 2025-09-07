from loguru import logger

def get_logger(name: str = "Shikshasamvad"):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level="INFO")
    return logger.bind(app=name)