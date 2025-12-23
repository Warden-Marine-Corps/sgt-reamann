import logging

# ANSI-Farbcodes
RESET = "\033[0m"
BOLD = "\033[1m"
GRAY = "\033[90m"
CYAN = "\033[36m"

LEVEL_COLORS = {
    "DEBUG": "\033[32m",    # Grün
    "INFO": "\033[34m",     # Blau
    "WARNING": "\033[33m",  # Gelb
    "ERROR": "\033[31m",    # Rot
    "CRITICAL": "\033[41m", # Rot Hintergrund
}

class CustomColorFormatter(logging.Formatter):
    def format(self, record):
        # Datum grau
        asctime = f"{BOLD}{GRAY}{self.formatTime(record, self.datefmt)}{RESET}"
        # Level farbig
        levelname = f"{BOLD}{LEVEL_COLORS.get(record.levelname, RESET)}{record.levelname:<8}{RESET}"
        # Modul cyan
        name = f"{CYAN}{record.name}{RESET}"
        # Message normal
        message = record.getMessage()
        return f"{asctime} {levelname:<8} {name} | {message}"
    
class ServerFormatter(logging.Formatter):
    def format(self, record):
        asctime = f"{self.formatTime(record, self.datefmt)}"
        levelname = f"{record.levelname:<8}"
        name = f"{record.name}"
        # Message normal
        message = record.getMessage()
        return f"{levelname:<8} {name} | {message} " # ohne time {asctime}
    
# Formatter detailliert
class DetailedFormatter(logging.Formatter):
    def format(self, record):
        asctime = f"{BOLD}{GRAY}{self.formatTime(record, self.datefmt)}{RESET}"
        levelname = f"{BOLD}{LEVEL_COLORS.get(record.levelname, RESET)}{record.levelname:<8}{RESET}"
        name = f"{CYAN}{record.name}{RESET}"
        lineno = f"{record.lineno}"
        funcName = f"{record.funcName}"
        message = record.getMessage()
        return f"{asctime} {levelname} {f"{name}, line {lineno} in {funcName}()":<48} | {message}"
    

    