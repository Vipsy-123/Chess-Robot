import logging
import os

# Ensure the 'logs' directory exists
log_directory = './logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create file handler for logging to file
file_handler = logging.FileHandler(f'{log_directory}/debug.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add file handler to logger
logger.addHandler(file_handler)

# (Optional) Create console handler for logging to console (set level to INFO or higher)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Optional: Only log INFO and higher to console
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Log messages (emojis or any Unicode characters)
logger.debug("🎮 WELCOME TO CHESS ROBOT GAME 🎮")
logger.info("Game Started")
logger.warning("Low battery!")
logger.error("An error occurred.")
logger.critical("Critical error!")
