import logging
import colorlog
from config import LOGS_DIR

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # Console Handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File Handler
    file_handler = logging.FileHandler(LOGS_DIR / "agent.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # Formatters
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler.setFormatter(color_formatter)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = get_logger("ai_agent")
