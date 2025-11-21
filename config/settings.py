"""Configuration settings for the mutant generator"""
import os
import platform
from pathlib import Path
# Platform detection
SYSTEM = platform.system().lower()

# Path Configuration - Platform independent
if SYSTEM == "windows":
    BASE_CHECKOUT_DIR = Path(os.environ.get('TEMP', 'C:/temp')) / "mutated_codes"
else:
    BASE_CHECKOUT_DIR = Path("/tmp/mutated_codes")

# Command configuration
if SYSTEM == "windows":
    DEFECTS4J_EXECUTABLE = "defects4j.bat"
else:
    DEFECTS4J_EXECUTABLE = "defects4j"

# Project Configuration
PROJECTS = ["Math", "Lang", "Time", "Chart", "Closure", "Mockito", "Codec", 
           "Compress", "Csv", "Gson", "JacksonCore", "JacksonDatabind", 
           "JacksonXml", "Jsoup", "JxPath"]

# Timeout Configuration
COMPILE_TIMEOUT = 720
COVERAGE_TIMEOUT = 720
MUTATION_TIMEOUT = 720

# Default Configuration
DEFAULT_MUTANT_PERCENTAGE = 50
DEFAULT_MAX_MUTATIONS = 4

# Load bugs from external file or keep as is
BUGS_TO_PROCESS = [
    ("Math", "1"),
    ("Math", "2"),
    # ... rest of your bugs list
]
MAX_WORKERS = min(10, os.cpu_count() or 4)  # Adaptive worker count
