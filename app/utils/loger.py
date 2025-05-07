from pathlib import Path
import logging


def get_logger(log_dir: Path, name: str = "scraper") -> logging.Logger:
    """
    Creates and configures a logger instance with file and console output.
    
    Args:
        log_dir: Directory to store log files
        name: Logger name (default: "scraper")
    
    Returns:
        Configured logging.Logger instance
    """
    log_dir.mkdir(exist_ok=True, parents=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    
    if logger.handlers:
        return logger
    
 
    file_handler = logging.FileHandler(
        filename=log_dir / 'scraper_errors.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)
    
    return logger