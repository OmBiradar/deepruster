import os
import logging

def setup_logger(log_file):
    #Delete the log file if it exists
    if os.path.exists(log_file):
        os.remove(log_file)

    # Create logger
    logger = logging.getLogger('custom_logger')
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(file_handler)
    
    return logger

def log_message(status, message):
    if status == 'INFO':
        logger.info(message)
    elif status == 'ERROR':
        logger.error(message)
    elif status == 'WARNING':
        logger.warning(message)
    else:
        logger.debug(message)

# Setup the logger
log_file = 'deepruster.log'
logger = setup_logger(log_file)

# Example usage
if __name__ == "__main__":
    log_message('INFO', 'This is an info log message.')
    log_message('ERROR', 'This is an error log message.')
    log_message('WARNING', 'This is a warning log message.')
    log_message('DEBUG', 'This is a debug log message.')