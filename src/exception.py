# ============================================================
# exception.py — Custom Exception Handler for ReturnShield AI
# ============================================================
#
# YEH FILE KYA KARTI HAI?
# ────────────────────────
# Jab bhi koi error aaye, toh yeh batata hai:
#   1. Kaunsi file mein error aaya
#   2. Kaunsi line number pe aaya
#   3. Kya error message hai
#
# Normal Python error:  "FileNotFoundError: file not found"
# Humara custom error:  "Error in [model_training.py] at line [45]: file not found"
#
# Industry mein kyun zaroori?
# - Large projects mein 50+ files hoti hain, bina file/line info ke
#   dhundhna mushkil hota hai
# - Logging ke saath combine karo toh debugging bahut fast hoti hai
#
# KAISE USE KARNA HAI?
# ────────────────────
#   try:
#       risky_code()
#   except Exception as e:
#       raise CustomException(e, sys)
# ============================================================

import sys  # sys module se error ki detailed info milti hai


def error_message_detail(error, error_detail: sys):
    """
    Yeh function error ki puri detail nikalti hai.
    
    sys.exc_info() se 3 cheezein milti hain:
      - exc_type:  Error ka type (FileNotFoundError, ValueError, etc.)
      - exc_value: Error ka message
      - exc_tb:    Traceback — isme file name aur line number hota hai
    
    Hum exc_tb se file name aur line number nikalte hain.
    """
    _, _, exc_tb = error_detail.exc_info()
    
    # Kaunsi file mein error aaya
    file_name = exc_tb.tb_frame.f_code.co_filename
    
    # Kaunsi line pe error aaya
    line_number = exc_tb.tb_lineno
    
    # Proper error message banao
    error_message = (
        f"Error occurred in script: [{file_name}] "
        f"at line number: [{line_number}] "
        f"error message: [{str(error)}]"
    )
    
    return error_message


class CustomException(Exception):
    """
    Custom Exception class.
    
    Jab bhi 'raise CustomException(e, sys)' karo:
      - Yeh error ka file name, line number aur message capture karega
      - Logger ke saath use karo toh log file mein bhi save hoga
    
    Example:
        try:
            data = pd.read_csv("nonexistent.csv")
        except Exception as e:
            logger.error(str(CustomException(e, sys)))
            raise CustomException(e, sys)
    """
    
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(
            error_message, error_detail=error_detail
        )
    
    def __str__(self):
        return self.error_message
