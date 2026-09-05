# ============================================================
# logger.py — Enterprise Logging Setup for ReturnShield AI
# ============================================================
# Provides unified, timestamped file and console logging across
# data pipelines, model training, API services, and audit vault.
# ============================================================

import logging
import os
from datetime import datetime

# Generate unique timestamped log file per execution run
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Define directory path for application logs
logs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(logs_path, exist_ok=True)

# Full absolute path for target log file
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# Configure logging format and level
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Export standard logger instance for project-wide usage
logger = logging.getLogger("ReturnShieldAI")
