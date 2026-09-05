# ============================================================
# logger.py — Logging Setup for ReturnShield AI
# ============================================================
# 
# YEH FILE KYA KARTI HAI?
# ────────────────────────
# Jab bhi koi important cheez hoti hai (data load hua, model train hua,
# error aaya), toh yeh uska record ek .log file mein save karti hai.
#
# Industry mein kyun zaroori hai?
# - Production mein terminal nahi dikhta, logs se debug karte hain
# - Timestamp hota hai toh pata chalta hai kab kya hua
# - Hackathon mein dikhao toh judges impress hote hain
#
# KAISE USE KARNA HAI?
# ────────────────────
#   from src.logger import logger
#   logger.info("Data loaded successfully")
#   logger.error("File not found!")
# ============================================================

import logging    # Python ki built-in library hai logging ke liye
import os         # Folders create karne ke liye
from datetime import datetime  # Current date-time ke liye

# ── Log file ka naam banao (date-time ke saath) ──
# Har baar jab program run hoga, ek naya log file banega
# Example: "09_05_2026_15_30_45.log"
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# ── Logs folder ka path banao ──
# logs/ folder mein sab log files jayengi
logs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

# Agar logs/ folder exist nahi karta toh bana do
os.makedirs(logs_path, exist_ok=True)

# ── Full path of the log file ──
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# ── Logging ko configure karo ──
# basicConfig = ek baar setup karo, phir poore project mein kaam karega
logging.basicConfig(
    filename=LOG_FILE_PATH,           # Kahan save karna hai
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    # ↑ Format: [timestamp] line_number file_name - INFO/ERROR - message
    level=logging.INFO,               # INFO level aur usse upar sab log hoga
)

# ── Logger object banao jo poore project mein use hoga ──
logger = logging.getLogger("ReturnShieldAI")
