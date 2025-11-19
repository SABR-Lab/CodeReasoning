import shutil
import re
from pathlib import Path
import subprocess
import json
import time
import random
import csv
from datetime import datetime
import multiprocessing
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import xml.etree.ElementTree as ET
from collections import defaultdict
#first run in terminal export PATH=$PATH:"/Users/quibliss/research/defects4j_codes/defects4j"/framework/bin

# --- Configuration ---
DEFECTS4J_EXECUTABLE = "defects4j"
MAX_WORKERS = 10  # Number of parallel processes

projects = ["Math", "Lang", "Time", "Chart", "Closure", "Mockito", "Codec", "Compress", "Csv", "Gson", "JacksonCore", "JacksonDatabind", "JacksonXml", "Jsoup", "JxPath"]

BUGS_TO_PROCESS = [
    # Math project
    ("Math", "1"),
    ("Math", "2"),
    ("Math", "3"),
    ("Math", "4"),
    ("Math", "5"),
    ("Math", "6"),
    ("Math", "7"),
    ("Math", "8"),
    ("Math", "9"),
    ("Math", "10"),
    ("Math", "11"),
    ("Math", "12"),
    ("Math", "13"),
    ("Math", "14"),
    ("Math", "15"),
    ("Math", "16"),
    ("Math", "17"),
    ("Math", "18"),
    ("Math", "19"),
    ("Math", "20"),
    ("Math", "21"),
    ("Math", "22"),
    ("Math", "23"),
    ("Math", "24"),
    ("Math", "25"),
    ("Math", "26"),
    ("Math", "27"),
    ("Math", "28"),
    ("Math", "29"),
    ("Math", "30"),
    ("Math", "31"),
    ("Math", "32"),
    ("Math", "33"),
    ("Math", "34"),
    ("Math", "35"),
    ("Math", "36"),
    ("Math", "37"),
    ("Math", "38"),
    ("Math", "39"),
    ("Math", "40"),
    ("Math", "41"),
    ("Math", "42"),
    ("Math", "43"),
    ("Math", "44"),
    ("Math", "45"),
    ("Math", "46"),
    ("Math", "47"),
    ("Math", "48"),
    ("Math", "49"),
    ("Math", "50"),
    ("Math", "51"),
    ("Math", "52"),
    ("Math", "53"),
    ("Math", "54"),
    ("Math", "55"),
    ("Math", "56"),
    ("Math", "57"),
    ("Math", "58"),
    ("Math", "59"),
    ("Math", "60"),
    ("Math", "61"),
    ("Math", "62"),
    ("Math", "63"),
    ("Math", "64"),
    ("Math", "65"),
    ("Math", "66"),
    ("Math", "67"),
    ("Math", "68"),
    ("Math", "69"),
    ("Math", "70"),
    ("Math", "71"),
    ("Math", "72"),
    ("Math", "73"),
    ("Math", "74"),
    ("Math", "75"),
    ("Math", "76"),
    ("Math", "77"),
    ("Math", "78"),
    ("Math", "79"),
    ("Math", "80"),
    ("Math", "81"),
    ("Math", "82"),
    ("Math", "83"),
    ("Math", "84"),
    ("Math", "85"),
    ("Math", "86"),
    ("Math", "87"),
    ("Math", "88"),
    ("Math", "89"),
    ("Math", "90"),
    ("Math", "91"),
    ("Math", "92"),
    ("Math", "93"),
    ("Math", "94"),
    ("Math", "95"),
    ("Math", "96"),
    ("Math", "97"),
    ("Math", "98"),
    ("Math", "99"),
    ("Math", "100"),
    ("Math", "101"),
    ("Math", "102"),
    ("Math", "103"),
    ("Math", "104"),
    ("Math", "105"),
    ("Math", "106"),

    # Lang project
    ("Lang", "1"),
    ("Lang", "3"),
    ("Lang", "4"),
    ("Lang", "5"),
    ("Lang", "6"),
    ("Lang", "7"),
    ("Lang", "8"),
    ("Lang", "9"),
    ("Lang", "10"),
    ("Lang", "11"),
    ("Lang", "12"),
    ("Lang", "13"),
    ("Lang", "14"),
    ("Lang", "15"),
    ("Lang", "16"),
    ("Lang", "17"),
    ("Lang", "19"),
    ("Lang", "20"),
    ("Lang", "21"),
    ("Lang", "22"),
    ("Lang", "23"),
    ("Lang", "24"),
    ("Lang", "26"),
    ("Lang", "27"),
    ("Lang", "28"),
    ("Lang", "29"),
    ("Lang", "30"),
    ("Lang", "31"),
    ("Lang", "32"),
    ("Lang", "33"),
    ("Lang", "34"),
    ("Lang", "35"),
    ("Lang", "36"),
    ("Lang", "37"),
    ("Lang", "38"),
    ("Lang", "39"),
    ("Lang", "40"),
    ("Lang", "41"),
    ("Lang", "42"),
    ("Lang", "43"),
    ("Lang", "44"),
    ("Lang", "45"),
    ("Lang", "46"),
    ("Lang", "47"),
    ("Lang", "49"),
    ("Lang", "50"),
    ("Lang", "51"),
    ("Lang", "52"),
    ("Lang", "53"),
    ("Lang", "54"),
    ("Lang", "55"),
    ("Lang", "56"),
    ("Lang", "57"),
    ("Lang", "58"),
    ("Lang", "59"),
    ("Lang", "60"),
    ("Lang", "61"),
    ("Lang", "62"),
    ("Lang", "63"),
    ("Lang", "64"),
    ("Lang", "65"),

    # Time project
    ("Time", "1"),
    ("Time", "2"),
    ("Time", "3"),
    ("Time", "4"),
    ("Time", "5"),
    ("Time", "6"),
    ("Time", "7"),
    ("Time", "8"),
    ("Time", "9"),
    ("Time", "10"),
    ("Time", "11"),
    ("Time", "12"),
    ("Time", "13"),
    ("Time", "14"),
    ("Time", "15"),
    ("Time", "16"),
    ("Time", "17"),
    ("Time", "18"),
    ("Time", "19"),
    ("Time", "20"),
    ("Time", "22"),
    ("Time", "23"),
    ("Time", "24"),
    ("Time", "25"),
    ("Time", "26"),
    ("Time", "27"),

    # Chart project
    ("Chart", "1"),
    ("Chart", "2"),
    ("Chart", "3"),
    ("Chart", "4"),
    ("Chart", "5"),
    ("Chart", "6"),
    ("Chart", "7"),
    ("Chart", "8"),
    ("Chart", "9"),
    ("Chart", "10"),
    ("Chart", "11"),
    ("Chart", "12"),
    ("Chart", "13"),
    ("Chart", "14"),
    ("Chart", "15"),
    ("Chart", "16"),
    ("Chart", "17"),
    ("Chart", "18"),
    ("Chart", "19"),
    ("Chart", "20"),
    ("Chart", "21"),
    ("Chart", "22"),
    ("Chart", "23"),
    ("Chart", "24"),
    ("Chart", "25"),
    ("Chart", "26"),

    # Closure project
    ("Closure", "1"),
    ("Closure", "2"),
    ("Closure", "3"),
    ("Closure", "4"),
    ("Closure", "5"),
    ("Closure", "6"),
    ("Closure", "7"),
    ("Closure", "8"),
    ("Closure", "9"),
    ("Closure", "10"),
    ("Closure", "11"),
    ("Closure", "12"),
    ("Closure", "13"),
    ("Closure", "14"),
    ("Closure", "15"),
    ("Closure", "16"),
    ("Closure", "17"),
    ("Closure", "18"),
    ("Closure", "19"),
    ("Closure", "20"),
    ("Closure", "21"),
    ("Closure", "22"),
    ("Closure", "23"),
    ("Closure", "24"),
    ("Closure", "25"),
    ("Closure", "26"),
    ("Closure", "27"),
    ("Closure", "28"),
    ("Closure", "29"),
    ("Closure", "30"),
    ("Closure", "31"),
    ("Closure", "32"),
    ("Closure", "33"),
    ("Closure", "34"),
    ("Closure", "35"),
    ("Closure", "36"),
    ("Closure", "37"),
    ("Closure", "38"),
    ("Closure", "39"),
    ("Closure", "40"),
    ("Closure", "41"),
    ("Closure", "42"),
    ("Closure", "43"),
    ("Closure", "44"),
    ("Closure", "45"),
    ("Closure", "46"),
    ("Closure", "47"),
    ("Closure", "48"),
    ("Closure", "49"),
    ("Closure", "50"),
    ("Closure", "51"),
    ("Closure", "52"),
    ("Closure", "53"),
    ("Closure", "54"),
    ("Closure", "55"),
    ("Closure", "56"),
    ("Closure", "57"),
    ("Closure", "58"),
    ("Closure", "59"),
    ("Closure", "60"),
    ("Closure", "61"),
    ("Closure", "62"),
    ("Closure", "64"),
    ("Closure", "65"),
    ("Closure", "66"),
    ("Closure", "67"),
    ("Closure", "68"),
    ("Closure", "69"),
    ("Closure", "70"),
    ("Closure", "71"),
    ("Closure", "72"),
    ("Closure", "73"),
    ("Closure", "74"),
    ("Closure", "75"),
    ("Closure", "76"),
    ("Closure", "77"),
    ("Closure", "78"),
    ("Closure", "79"),
    ("Closure", "80"),
    ("Closure", "81"),
    ("Closure", "82"),
    ("Closure", "83"),
    ("Closure", "84"),
    ("Closure", "85"),
    ("Closure", "86"),
    ("Closure", "87"),
    ("Closure", "88"),
    ("Closure", "89"),
    ("Closure", "90"),
    ("Closure", "91"),
    ("Closure", "92"),
    ("Closure", "94"),
    ("Closure", "95"),
    ("Closure", "96"),
    ("Closure", "97"),
    ("Closure", "98"),
    ("Closure", "99"),
    ("Closure", "100"),
    ("Closure", "101"),
    ("Closure", "102"),
    ("Closure", "103"),
    ("Closure", "104"),
    ("Closure", "105"),
    ("Closure", "106"),
    ("Closure", "107"),
    ("Closure", "108"),
    ("Closure", "109"),
    ("Closure", "110"),
    ("Closure", "111"),
    ("Closure", "112"),
    ("Closure", "113"),
    ("Closure", "114"),
    ("Closure", "115"),
    ("Closure", "116"),
    ("Closure", "117"),
    ("Closure", "118"),
    ("Closure", "119"),
    ("Closure", "120"),
    ("Closure", "121"),
    ("Closure", "122"),
    ("Closure", "123"),
    ("Closure", "124"),
    ("Closure", "125"),
    ("Closure", "126"),
    ("Closure", "127"),
    ("Closure", "128"),
    ("Closure", "129"),
    ("Closure", "130"),
    ("Closure", "131"),
    ("Closure", "132"),
    ("Closure", "133"),
    ("Closure", "134"),
    ("Closure", "135"),
    ("Closure", "136"),
    ("Closure", "137"),
    ("Closure", "138"),
    ("Closure", "139"),
    ("Closure", "140"),
    ("Closure", "141"),
    ("Closure", "142"),
    ("Closure", "143"),
    ("Closure", "144"),
    ("Closure", "145"),
    ("Closure", "146"),
    ("Closure", "147"),
    ("Closure", "148"),
    ("Closure", "149"),
    ("Closure", "150"),
    ("Closure", "151"),
    ("Closure", "152"),
    ("Closure", "153"),
    ("Closure", "154"),
    ("Closure", "155"),
    ("Closure", "156"),
    ("Closure", "157"),
    ("Closure", "158"),
    ("Closure", "159"),
    ("Closure", "160"),
    ("Closure", "161"),
    ("Closure", "162"),
    ("Closure", "163"),
    ("Closure", "164"),
    ("Closure", "165"),
    ("Closure", "166"),
    ("Closure", "167"),
    ("Closure", "168"),
    ("Closure", "169"),
    ("Closure", "170"),
    ("Closure", "171"),
    ("Closure", "172"),
    ("Closure", "173"),
    ("Closure", "174"),
    ("Closure", "175"),
    ("Closure", "176"),
    ("Closure", "177"),
    ("Closure", "178"),
    ("Closure", "179"),
    ("Closure", "180"),
    ("Closure", "181"),
    ("Closure", "182"),
    ("Closure", "183"),
    ("Closure", "184"),
    ("Closure", "185"),
    ("Closure", "186"),
    ("Closure", "187"),
    ("Closure", "188"),
    ("Closure", "189"),
    ("Closure", "190"),
    ("Closure", "191"),
    ("Closure", "192"),
    ("Closure", "193"),
    ("Closure", "194"),

    # Mockito project
    ("Mockito", "1"),
    ("Mockito", "2"),
    ("Mockito", "3"),
    ("Mockito", "4"),
    ("Mockito", "5"),
    ("Mockito", "6"),
    ("Mockito", "7"),
    ("Mockito", "8"),
    ("Mockito", "9"),
    ("Mockito", "10"),
    ("Mockito", "11"),
    ("Mockito", "12"),
    ("Mockito", "13"),
    ("Mockito", "14"),
    ("Mockito", "15"),
    ("Mockito", "16"),
    ("Mockito", "17"),
    ("Mockito", "18"),
    ("Mockito", "19"),
    ("Mockito", "20"),
    ("Mockito", "21"),
    ("Mockito", "22"),
    ("Mockito", "23"),
    ("Mockito", "24"),
    ("Mockito", "25"),
    ("Mockito", "26"),
    ("Mockito", "27"),
    ("Mockito", "28"),
    ("Mockito", "29"),
    ("Mockito", "30"),
    ("Mockito", "31"),
    ("Mockito", "32"),
    ("Mockito", "33"),
    ("Mockito", "34"),
    ("Mockito", "35"),
    ("Mockito", "36"),
    ("Mockito", "37"),
    ("Mockito", "38"),

    # Codec project
    ("Codec", "1"),
    ("Codec", "2"),
    ("Codec", "3"),
    ("Codec", "4"),
    ("Codec", "5"),
    ("Codec", "6"),
    ("Codec", "7"),
    ("Codec", "8"),
    ("Codec", "9"),
    ("Codec", "10"),
    ("Codec", "11"),
    ("Codec", "12"),
    ("Codec", "13"),
    ("Codec", "14"),
    ("Codec", "15"),
    ("Codec", "16"),
    ("Codec", "17"),
    ("Codec", "18"),

    # Compress project
    ("Compress", "1"),
    ("Compress", "2"),
    ("Compress", "3"),
    ("Compress", "4"),
    ("Compress", "5"),
    ("Compress", "6"),
    ("Compress", "7"),
    ("Compress", "8"),
    ("Compress", "9"),
    ("Compress", "10"),
    ("Compress", "11"),
    ("Compress", "12"),
    ("Compress", "13"),
    ("Compress", "14"),
    ("Compress", "15"),
    ("Compress", "16"),
    ("Compress", "17"),
    ("Compress", "18"),
    ("Compress", "19"),
    ("Compress", "20"),
    ("Compress", "21"),
    ("Compress", "22"),
    ("Compress", "23"),
    ("Compress", "24"),
    ("Compress", "25"),
    ("Compress", "26"),
    ("Compress", "27"),
    ("Compress", "28"),
    ("Compress", "29"),
    ("Compress", "30"),
    ("Compress", "31"),
    ("Compress", "32"),
    ("Compress", "33"),
    ("Compress", "34"),
    ("Compress", "35"),
    ("Compress", "36"),
    ("Compress", "37"),
    ("Compress", "38"),
    ("Compress", "39"),
    ("Compress", "40"),
    ("Compress", "41"),
    ("Compress", "42"),
    ("Compress", "43"),
    ("Compress", "44"),
    ("Compress", "45"),
    ("Compress", "46"),
    ("Compress", "47"),

    # Csv project
    ("Csv", "1"),
    ("Csv", "2"),
    ("Csv", "3"),
    ("Csv", "4"),
    ("Csv", "5"),
    ("Csv", "6"),
    ("Csv", "7"),
    ("Csv", "8"),
    ("Csv", "9"),
    ("Csv", "10"),
    ("Csv", "11"),
    ("Csv", "12"),
    ("Csv", "13"),
    ("Csv", "14"),
    ("Csv", "15"),
    ("Csv", "16"),

    # Gson project
    ("Gson", "1"),
    ("Gson", "2"),
    ("Gson", "3"),
    ("Gson", "4"),
    ("Gson", "5"),
    ("Gson", "6"),
    ("Gson", "7"),
    ("Gson", "8"),
    ("Gson", "9"),
    ("Gson", "10"),
    ("Gson", "11"),
    ("Gson", "12"),
    ("Gson", "13"),
    ("Gson", "14"),
    ("Gson", "15"),
    ("Gson", "16"),
    ("Gson", "17"),
    ("Gson", "18"),

    # JacksonCore project
    ("JacksonCore", "1"),
    ("JacksonCore", "2"),
    ("JacksonCore", "3"),
    ("JacksonCore", "4"),
    ("JacksonCore", "5"),
    ("JacksonCore", "6"),
    ("JacksonCore", "7"),
    ("JacksonCore", "8"),
    ("JacksonCore", "9"),
    ("JacksonCore", "10"),
    ("JacksonCore", "11"),
    ("JacksonCore", "12"),
    ("JacksonCore", "13"),
    ("JacksonCore", "14"),
    ("JacksonCore", "15"),
    ("JacksonCore", "16"),
    ("JacksonCore", "17"),
    ("JacksonCore", "18"),
    ("JacksonCore", "19"),
    ("JacksonCore", "20"),
    ("JacksonCore", "21"),
    ("JacksonCore", "22"),
    ("JacksonCore", "23"),
    ("JacksonCore", "24"),
    ("JacksonCore", "25"),
    ("JacksonCore", "26"),

    # JacksonDatabind project
    ("JacksonDatabind", "1"),
    ("JacksonDatabind", "2"),
    ("JacksonDatabind", "3"),
    ("JacksonDatabind", "4"),
    ("JacksonDatabind", "5"),
    ("JacksonDatabind", "6"),
    ("JacksonDatabind", "7"),
    ("JacksonDatabind", "8"),
    ("JacksonDatabind", "9"),
    ("JacksonDatabind", "10"),
    ("JacksonDatabind", "11"),
    ("JacksonDatabind", "12"),
    ("JacksonDatabind", "13"),
    ("JacksonDatabind", "14"),
    ("JacksonDatabind", "15"),
    ("JacksonDatabind", "16"),
    ("JacksonDatabind", "17"),
    ("JacksonDatabind", "18"),
    ("JacksonDatabind", "19"),
    ("JacksonDatabind", "20"),
    ("JacksonDatabind", "21"),
    ("JacksonDatabind", "22"),
    ("JacksonDatabind", "23"),
    ("JacksonDatabind", "24"),
    ("JacksonDatabind", "25"),
    ("JacksonDatabind", "26"),
    ("JacksonDatabind", "27"),
    ("JacksonDatabind", "28"),
    ("JacksonDatabind", "29"),
    ("JacksonDatabind", "30"),
    ("JacksonDatabind", "31"),
    ("JacksonDatabind", "32"),
    ("JacksonDatabind", "33"),
    ("JacksonDatabind", "34"),
    ("JacksonDatabind", "35"),
    ("JacksonDatabind", "36"),
    ("JacksonDatabind", "37"),
    ("JacksonDatabind", "38"),
    ("JacksonDatabind", "39"),
    ("JacksonDatabind", "40"),
    ("JacksonDatabind", "41"),
    ("JacksonDatabind", "42"),
    ("JacksonDatabind", "43"),
    ("JacksonDatabind", "44"),
    ("JacksonDatabind", "45"),
    ("JacksonDatabind", "46"),
    ("JacksonDatabind", "47"),
    ("JacksonDatabind", "48"),
    ("JacksonDatabind", "49"),
    ("JacksonDatabind", "50"),
    ("JacksonDatabind", "51"),
    ("JacksonDatabind", "52"),
    ("JacksonDatabind", "53"),
    ("JacksonDatabind", "54"),
    ("JacksonDatabind", "55"),
    ("JacksonDatabind", "56"),
    ("JacksonDatabind", "57"),
    ("JacksonDatabind", "58"),
    ("JacksonDatabind", "59"),
    ("JacksonDatabind", "60"),
    ("JacksonDatabind", "61"),
    ("JacksonDatabind", "62"),
    ("JacksonDatabind", "63"),
    ("JacksonDatabind", "64"),
    ("JacksonDatabind", "66"),
    ("JacksonDatabind", "67"),
    ("JacksonDatabind", "68"),
    ("JacksonDatabind", "69"),
    ("JacksonDatabind", "70"),
    ("JacksonDatabind", "71"),
    ("JacksonDatabind", "72"),
    ("JacksonDatabind", "73"),
    ("JacksonDatabind", "74"),
    ("JacksonDatabind", "75"),
    ("JacksonDatabind", "76"),
    ("JacksonDatabind", "77"),
    ("JacksonDatabind", "78"),
    ("JacksonDatabind", "79"),
    ("JacksonDatabind", "80"),
    ("JacksonDatabind", "81"),
    ("JacksonDatabind", "82"),
    ("JacksonDatabind", "83"),
    ("JacksonDatabind", "84"),
    ("JacksonDatabind", "85"),
    ("JacksonDatabind", "86"),
    ("JacksonDatabind", "87"),
    ("JacksonDatabind", "88"),
    ("JacksonDatabind", "90"),
    ("JacksonDatabind", "91"),
    ("JacksonDatabind", "92"),
    ("JacksonDatabind", "93"),
    ("JacksonDatabind", "94"),
    ("JacksonDatabind", "95"),
    ("JacksonDatabind", "96"),
    ("JacksonDatabind", "97"),
    ("JacksonDatabind", "98"),
    ("JacksonDatabind", "99"),
    ("JacksonDatabind", "100"),
    ("JacksonDatabind", "101"),
    ("JacksonDatabind", "102"),
    ("JacksonDatabind", "103"),
    ("JacksonDatabind", "104"),
    ("JacksonDatabind", "105"),
    ("JacksonDatabind", "106"),
    ("JacksonDatabind", "107"),
    ("JacksonDatabind", "108"),
    ("JacksonDatabind", "109"),
    ("JacksonDatabind", "110"),
    ("JacksonDatabind", "111"),
    ("JacksonDatabind", "112"),
    ("JacksonDatabind", "113"),

    # JacksonXml project
    ("JacksonXml", "1"),
    ("JacksonXml", "2"),
    ("JacksonXml", "3"),
    ("JacksonXml", "4"),
    ("JacksonXml", "5"),
    ("JacksonXml", "6"),

    # Jsoup project
    ("Jsoup", "1"),
    ("Jsoup", "2"),
    ("Jsoup", "3"),
    ("Jsoup", "4"),
    ("Jsoup", "5"),
    ("Jsoup", "6"),
    ("Jsoup", "7"),
    ("Jsoup", "8"),
    ("Jsoup", "9"),
    ("Jsoup", "10"),
    ("Jsoup", "11"),
    ("Jsoup", "12"),
    ("Jsoup", "13"),
    ("Jsoup", "14"),
    ("Jsoup", "15"),
    ("Jsoup", "16"),
    ("Jsoup", "17"),
    ("Jsoup", "18"),
    ("Jsoup", "19"),
    ("Jsoup", "20"),
    ("Jsoup", "21"),
    ("Jsoup", "22"),
    ("Jsoup", "23"),
    ("Jsoup", "24"),
    ("Jsoup", "25"),
    ("Jsoup", "26"),
    ("Jsoup", "27"),
    ("Jsoup", "28"),
    ("Jsoup", "29"),
    ("Jsoup", "30"),
    ("Jsoup", "31"),
    ("Jsoup", "32"),
    ("Jsoup", "33"),
    ("Jsoup", "34"),
    ("Jsoup", "35"),
    ("Jsoup", "36"),
    ("Jsoup", "37"),
    ("Jsoup", "38"),
    ("Jsoup", "39"),
    ("Jsoup", "40"),
    ("Jsoup", "41"),
    ("Jsoup", "42"),
    ("Jsoup", "43"),
    ("Jsoup", "44"),
    ("Jsoup", "45"),
    ("Jsoup", "46"),
    ("Jsoup", "47"),
    ("Jsoup", "48"),
    ("Jsoup", "49"),
    ("Jsoup", "50"),
    ("Jsoup", "51"),
    ("Jsoup", "52"),
    ("Jsoup", "53"),
    ("Jsoup", "54"),
    ("Jsoup", "55"),
    ("Jsoup", "56"),
    ("Jsoup", "57"),
    ("Jsoup", "58"),
    ("Jsoup", "59"),
    ("Jsoup", "60"),
    ("Jsoup", "61"),
    ("Jsoup", "62"),
    ("Jsoup", "63"),
    ("Jsoup", "64"),
    ("Jsoup", "65"),
    ("Jsoup", "66"),
    ("Jsoup", "67"),
    ("Jsoup", "68"),
    ("Jsoup", "69"),
    ("Jsoup", "70"),
    ("Jsoup", "71"),
    ("Jsoup", "72"),
    ("Jsoup", "73"),
    ("Jsoup", "74"),
    ("Jsoup", "75"),
    ("Jsoup", "76"),
    ("Jsoup", "77"),
    ("Jsoup", "78"),
    ("Jsoup", "79"),
    ("Jsoup", "80"),
    ("Jsoup", "81"),
    ("Jsoup", "82"),
    ("Jsoup", "83"),
    ("Jsoup", "84"),
    ("Jsoup", "85"),
    ("Jsoup", "86"),
    ("Jsoup", "87"),
    ("Jsoup", "88"),
    ("Jsoup", "89"),
    ("Jsoup", "90"),
    ("Jsoup", "91"),
    ("Jsoup", "92"),
    ("Jsoup", "93"),

    # JxPath project
    ("JxPath", "1"),
    ("JxPath", "2"),
    ("JxPath", "3"),
    ("JxPath", "4"),
    ("JxPath", "5"),
    ("JxPath", "6"),
    ("JxPath", "7"),
    ("JxPath", "8"),
    ("JxPath", "9"),
    ("JxPath", "10"),
    ("JxPath", "11"),
    ("JxPath", "12"),
    ("JxPath", "13"),
    ("JxPath", "14"),
    ("JxPath", "15"),
    ("JxPath", "16"),
    ("JxPath", "17"),
    ("JxPath", "18"),
    ("JxPath", "19"),
    ("JxPath", "20"),
    ("JxPath", "21"),
    ("JxPath", "22"),
]

BASE_CHECKOUT_DIR = Path("/tmp/mutated_codes")

def run_command(command, working_dir, step_name="Command"):
    """Runs a shell command and returns True on success, False on failure."""
    print(f"    Running: {' '.join(command)}")
    result = subprocess.run(
        command, check=True, capture_output=True, text=True, cwd=working_dir
    )
    return result 

def get_source_directories(work_dir):
    """Get all possible source directories from Defects4J - handle different project structures"""
    print("   Finding source directories...")
    
    source_dirs = []
    
    # Common source directory patterns in Defects4J projects
    possible_dirs = [
        work_dir / "src",
        work_dir / "src/main/java",  # Maven structure
        work_dir / "src/java",
        work_dir / "source",
        work_dir / "Source",
    ]
    
    # Also try to get from Defects4J export
    try:
        proc = subprocess.run(
            [DEFECTS4J_EXECUTABLE, "export", "-p", "dir.src.classes"],
            capture_output=True, text=True, check=True, cwd=work_dir
        )
        def_src_dir = work_dir / proc.stdout.strip()
        if def_src_dir.exists():
            source_dirs.append(def_src_dir)
            print(f"   Defects4J source dir: {def_src_dir}")
    except:
        pass
    
    # Check all possible directories
    for dir_path in possible_dirs:
        if dir_path.exists():
            source_dirs.append(dir_path)
            print(f"   Found source dir: {dir_path}")
    
    # Search for Java files to find source directories
    java_dirs = set()
    for java_file in work_dir.rglob("*.java"):
        java_dirs.add(java_file.parent)
    
    # Add directories that contain Java files and look like source directories
    for java_dir in java_dirs:
        if any(pattern in str(java_dir) for pattern in ['src', 'java', 'source']):
            if java_dir not in source_dirs:
                source_dirs.append(java_dir)
    
    print(f"   Total source directories found: {len(source_dirs)}")
    return source_dirs

def find_mutants_log(work_dir):
    """Find the mutants.log file"""
    print("   Searching for mutants.log...")
    
    # Search recursively
    log_files = list(work_dir.rglob("mutants.log"))
    if log_files:
        print(f"   Found mutants.log: {log_files[0]}")
        return log_files[0]
    
    print("   No mutants.log file found")
    return None

def parse_mutants_log(line):
    """
    Corrected parsing of mutants.log lines using the specified parsing logic
    Format: ID:MUTATOR:SIG_ORIG:SIG_MUT:CLASS@METHOD:LINE:CODE_ORIG |==> CODE_MUT
    """
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    
    try:
        # Split by colon to get main parts
        parts = line.split(':')
        if len(parts) < 8:
            return None
        
        mutant_id = parts[0]
        mutator = parts[1]
        original_sig = parts[2]
        mutated_sig = parts[3]
        class_method = parts[4]
        line_num = parts[5]  
        garbage = parts[6]
        code = parts[7]
        
        # Extract code change
        if '|==>' in code:
            original_code, mutated_code = code.split('|==>', 1)
            original_code = original_code.strip()
            mutated_code = mutated_code.strip()
            
            # Handle <NO-OP> mutations - keep operation empty
            if mutated_code == '<NO-OP>':
                mutated_code = "pass"
        else:
            original_code = code.strip()
            mutated_code = ""
        
        # Extract class name from class@method
        if '@' in class_method:
            class_name = class_method.split('@')[0]
            method_name = class_method.split('@')[1]
        else:
            class_name = class_method
            method_name = ""
        
        # Convert line number to integer
        try:
            line_number = int(line_num)
        except ValueError:
            return None
        
        mutant_info = {
            'mutant_id': mutant_id,
            'mutator': mutator,
            'original_signature': original_sig,
            'mutated_signature': mutated_sig,
            'class_name': class_name,
            'method_name': method_name,
            'line_number': line_number,
            'original_code': original_code,
            'mutated_code': mutated_code,
            'raw_line': line
        }
        
        return mutant_info
        
    except Exception as e:
        return None

def find_java_file_by_class(class_name, source_dirs):
    """Find Java file by class name across all source directories"""
    # Convert class name to file path
    file_rel_path = class_name.replace('.', '/') + '.java'
    
    for src_dir in source_dirs:
        # Try direct path
        direct_path = src_dir / file_rel_path
        if direct_path.exists():
            return direct_path
        
        # Try with src/main/java prefix (common in Maven projects)
        maven_path = src_dir / "src/main/java" / file_rel_path
        if maven_path.exists():
            return maven_path
        
        # Try with src/java prefix
        src_java_path = src_dir / "src/java" / file_rel_path
        if src_java_path.exists():
            return src_java_path
    
    return None

def apply_mutation_to_file(source_file, line_number, original_code, mutated_code):
    """Apply mutation to a specific file"""
    try:
        if not source_file.exists():
            return False
        
        # Read the file
        with open(source_file, 'r') as f:
            lines = f.readlines()
        
        # Check line number
        if line_number < 1 or line_number > len(lines):
            return False
        
        target_line_index = line_number - 1
        original_line = lines[target_line_index]
        
        # Try exact replacement
        if original_code in original_line:
            mutated_line = original_line.replace(original_code, mutated_code)
            lines[target_line_index] = mutated_line
        
        # Try with stripped whitespace
        elif original_code.strip() in original_line.strip():
            # Find the exact position and preserve formatting
            stripped_original = original_code.strip()
            stripped_line = original_line.strip()
            
            if stripped_original in stripped_line:
                start_idx = original_line.find(stripped_original)
                if start_idx != -1:
                    end_idx = start_idx + len(stripped_original)
                    before = original_line[:start_idx]
                    after = original_line[end_idx:]
                    mutated_line = before + mutated_code + after
                    lines[target_line_index] = mutated_line
        else:
            return False
        
        # Write the modified content back
        with open(source_file, 'w') as f:
            f.writelines(lines)
        
        return True
        
    except Exception as e:
        return False

def create_full_project_copy(original_work_dir, copy_dir):
    """Create a full copy of the project"""
    print(f"   Creating full project copy: {copy_dir.name}")
    
    if copy_dir.exists():
        shutil.rmtree(copy_dir)
    
    # Copy the entire project
    shutil.copytree(original_work_dir, copy_dir)
    print(f"   Successfully created full project copy")
    return True

def parse_failing_tests_file(mutant_dir):
    """Parse failing tests from the failing_tests file - start from '----' until 'junit' or 'java'"""
    failing_tests_file = mutant_dir / "failing_tests"
    failed_tests = []
    
    if failing_tests_file.exists():
        try:
            with open(failing_tests_file, 'r', encoding='utf-8') as infile:
                for line in infile:
                # Strip leading/trailing whitespace from the line
                    stripped_line = line.strip()
                
                # Check if the line starts with '--- '
                    if stripped_line.startswith('--- '):
                    # Extract the part after '--- '
                        test_name = stripped_line[4:].strip()
                    
                    # Ensure it's a valid test name line (not just '---')
                        if test_name:
                            failed_tests.append(test_name)
        except FileNotFoundError:
            print(f"Error: The file '{failing_tests_file}' was not found.")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    return failed_tests

def read_all_tests_file(mutant_dir):
    """Read all tests from all_tests.txt file"""
    all_tests_file = mutant_dir / "all_tests"
    all_tests = []
    
    if all_tests_file.exists():
        try:
            with open(all_tests_file, 'r') as f:
                all_tests = [line.strip() for line in f if line.strip()]
            print(f"   Found {len(all_tests)} total tests in all_tests")
        except Exception as e:
            print(f"   Error reading all_tests: {e}")
    
    return all_tests

def parse_coverage_xml(xml_file):
    """Parse coverage.xml and extract method names and their line numbers"""
    method_data = {}
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Calculate line coverage percentage
        total_lines = 0
        covered_lines = 0
        
        # Find all classes and their methods
        for cls in root.findall('.//class'):
            class_name = cls.get('name')
            
            for method in cls.findall('.//method'):
                method_name = method.get('name')
                method_signature = method.get('signature', '')
                
                # Create unique method identifier
                full_method_name = f"{class_name}.{method_name}{method_signature}"
                
                # Extract line numbers for this method
                line_numbers = []
                for line in method.findall('.//line'):
                    line_number = line.get('number')
                    if line_number:
                        line_numbers.append(line_number)
                    
                    # Count coverage
                    total_lines += 1
                    if line.get('hits') != '0':
                        covered_lines += 1
                
                method_data[full_method_name] = line_numbers
        
        # Calculate line coverage percentage
        coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        
        return coverage_percentage, method_data
        
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        return 0, {}

def run_coverage_and_tests(mutant_dir, project_id, bug_id):
    """Run coverage and tests on a mutant, return failed tests and coverage info"""
    print(f"   Running coverage and tests for mutant...")
    
    coverage_result = {
        'coverage_success': False,
        'failed_tests': [],
        'all_tests': [],
        'total_tests': 0,
        'failed_count': 0,
        'coverage_output': '',
        'coverage_percentage': 0,
        'method_coverage': {}
    }
    
    try:
        # First compile the mutant
        compile_result = run_command([DEFECTS4J_EXECUTABLE, "compile"], mutant_dir, "Compile mutant")
        if not compile_result:
            print("   Failed to compile mutant")
            return coverage_result
        
        # Run coverage
        print("   Running defects4j coverage...")
        coverage_process = subprocess.run(
            [DEFECTS4J_EXECUTABLE, "coverage", "-r"],
            capture_output=True, 
            text=True, 
            cwd=mutant_dir,
            timeout=720  # 12 minute timeout
        )
        
        coverage_result['coverage_output'] = coverage_process.stdout + coverage_process.stderr
        coverage_result['coverage_success'] = (coverage_process.returncode == 0)
        
        # Parse coverage.xml file if it exists
        coverage_xml_file = mutant_dir / "coverage.xml"
        if coverage_xml_file.exists():
            coverage_percentage, method_data = parse_coverage_xml(coverage_xml_file)
            coverage_result['coverage_percentage'] = coverage_percentage
            coverage_result['method_coverage'] = method_data
            print(f"   Parsed coverage.xml - Line coverage: {coverage_percentage:.2f}%")
        else:
            print(f"   Warning: coverage.xml not found in {mutant_dir}")
        
        # Parse failing tests from file using the new parsing method
        failed_tests = parse_failing_tests_file(mutant_dir)
        coverage_result['failed_tests'] = failed_tests
        coverage_result['failed_count'] = len(failed_tests)
        
        # Read all tests from all_tests.txt
        all_tests = read_all_tests_file(mutant_dir)
        coverage_result['all_tests'] = all_tests
        coverage_result['total_tests'] = len(all_tests)
        
        print("coverage created")
        print(f"   Coverage completed - {coverage_result['failed_count']}/{coverage_result['total_tests']} tests failed")
        
    except subprocess.TimeoutExpired:
        print("   Coverage command timed out after 10 minutes")
        coverage_result['coverage_output'] = "TIMEOUT: Coverage command took too long"
    except Exception as e:
        print(f"   Error running coverage: {e}")
        coverage_result['coverage_output'] = f"ERROR: {str(e)}"
    
    return coverage_result

def create_single_mutant_worker(args):
    """Worker function for creating a single mutant - to be used with multiprocessing"""
    original_work_dir, mutant_dir, mutation_info, project_id, bug_id = args
    
    print(f"   [Process {os.getpid()}] Creating mutant {mutant_dir.name}...")
    
    # Create full project copy
    if not create_full_project_copy(original_work_dir, mutant_dir):
        return None
    
    # Get source directories from the project copy
    source_dirs = get_source_directories(mutant_dir)
    if not source_dirs:
        print(f"   [Process {os.getpid()}] No source directories found in {mutant_dir}")
        return None
    
    # Find the target file
    class_name = mutation_info['class_name']
    target_file = find_java_file_by_class(class_name, source_dirs)
    
    if not target_file:
        print(f"   [Process {os.getpid()}] Could not find Java file for class: {class_name}")
        return None
    
    # Apply the single mutation
    success = apply_mutation_to_file(
        target_file,
        mutation_info['line_number'],
        mutation_info['original_code'],
        mutation_info['mutated_code']
    )
    
    if success:
        # Run coverage and tests on the mutant
        coverage_result = run_coverage_and_tests(mutant_dir, project_id, bug_id)
        
        result_info = {
            'mutant_id': mutation_info['mutant_id'],
            'mutant_directory': str(mutant_dir),
            'mutator': mutation_info['mutator'],
            'class_name': mutation_info['class_name'],
            'line_number': mutation_info['line_number'],
            'target_file': str(target_file.relative_to(mutant_dir)),
            'total_tests_count': coverage_result['total_tests'],
            'failed_test_count': coverage_result['failed_count'],
            'failed_tests': coverage_result['failed_tests'],
            'all_tests': coverage_result['all_tests'],  # Store all tests for CSV
            'coverage_success': coverage_result['coverage_success'],
            'coverage_output_file': str(mutant_dir / "coverage_output.log"),
            'coverage_percentage': coverage_result['coverage_percentage'],
            'method_coverage': coverage_result['method_coverage']  # Store method coverage data
        }
        
        # Save coverage output to file
        with open(mutant_dir / "coverage_output.log", 'w') as f:
            f.write(coverage_result['coverage_output'])
        
        print(f"   [Process {os.getpid()}] Successfully created mutant {mutant_dir.name}")
        return result_info
    else:
        print(f"   [Process {os.getpid()}] Failed to apply mutation to {mutant_dir.name}")
        # Clean up failed mutant
        if mutant_dir.exists():
            shutil.rmtree(mutant_dir)
        return None

def parse_all_mutations(log_file):
    """Parse all mutations from mutants.log"""
    print(f"   Parsing all mutations from {log_file.name}...")
    
    all_mutations = []
    prevline = -1
    prevmut = -1
    try:
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip() and not line.strip().startswith('#'):
                    mutation_info = parse_mutants_log(line)
                    if mutation_info and mutation_info['line_number'] == prevline and mutation_info['mutator'] == prevmut:
                        prevline = mutation_info['line_number']
                        prevmut = mutation_info['mutator']
                        continue
                    prevline = mutation_info['line_number']
                    prevmut = mutation_info['mutator']
                    if mutation_info:
                        all_mutations.append(mutation_info)
    
    except Exception as e:
        print(f"   Error parsing log file: {e}")
    
    print(f"   Parsed {len(all_mutations)} total mutations")
    return all_mutations


def apply_mutation_and_coverage_worker(args):
    """Worker that only applies mutation and runs coverage (project already copied)"""
    work_dir, mutant_dir, mutation_info, project_id, bug_id, relative_source_dirs = args
    
    mutant_id = mutation_info['mutant_id']
    pid = os.getpid()
    
    try:
        print(f"   [Process {pid}] Starting Mutant {mutant_id}...")
        
        # 1. FAST COPY: Ignore git and other heavy artifacts to speed up copy
        # We copy from the Master dir which is already compiled, so we get .class files for free
        shutil.copytree(
            work_dir, 
            mutant_dir, 
            ignore=shutil.ignore_patterns('.git', 'mutants.log', '*.tar.gz')
        )
        
        # 2. Reconstruct source directory paths from relative paths passed in args
        source_dirs = [mutant_dir / rel_path for rel_path in relative_source_dirs]
        
        # 3. Find target file
        class_name = mutation_info['class_name']
        target_file = find_java_file_by_class(class_name, source_dirs)
        
        if not target_file:
            print(f"   [Process {pid}] File not found for {class_name}")
            return None

        # 4. Apply Mutation
        success = apply_mutation_to_file(
            target_file,
            mutation_info['line_number'],
            mutation_info['original_code'],
            mutation_info['mutated_code']
        )
        
        if not success:
            print(f"   [Process {pid}] Mutation application failed")
            return None
        
        # 5. Run Coverage
        coverage_result = run_coverage_and_tests(mutant_dir, project_id, bug_id)
        
        result_info = {
            'mutant_id': mutation_info['mutant_id'],
            'mutant_directory': str(mutant_dir),
            'mutator': mutation_info['mutator'],
            'class_name': mutation_info['class_name'],
            'line_number': mutation_info['line_number'],
            'target_file': str(target_file.relative_to(mutant_dir)),
            'total_tests_count': coverage_result['total_tests'],
            'failed_test_count': coverage_result['failed_count'],
            'failed_tests': coverage_result['failed_tests'],
            'all_tests': coverage_result['all_tests'],
            'coverage_success': coverage_result['coverage_success'],
            'coverage_percentage': coverage_result['coverage_percentage'],
            'method_coverage': coverage_result['method_coverage']
        }
        
        print(f"   [Process {pid}] Finished Mutant {mutant_id} (Cov: {coverage_result['coverage_percentage']:.2f}%)")
        return result_info

    except Exception as e:
        print(f"   [Process {pid}] Error: {e}")
        return None
        
    finally:
        # 6. CLEANUP: Remove the mutant directory to save disk space
        # If you want to KEEP the files, comment this out, but be warned of disk usage.
        if mutant_dir.exists():
             shutil.rmtree(mutant_dir)


def create_comprehensive_coverage_csv(successful_mutants, csv_file_path, project_id, bug_id):
    """Create a comprehensive CSV file with test results and coverage information"""
    print(f"   Creating comprehensive coverage CSV file: {csv_file_path}")
    
    # Collect all unique methods across all mutants for column headers
    all_methods = set()
    for mutant in successful_mutants:
        all_methods.update(mutant['method_coverage'].keys())
    
    sorted_methods = sorted(all_methods)
    
    with open(csv_file_path, 'w', newline='') as csvfile:
        # Create field names for the CSV
        fieldnames = [
            'Mutant',
            'Line Coverage %',
            'Mutator',
            'Class Name', 
            'Line Number',
            'Target File',
            'Total Tests Count',
            'Failed Test Count',
            'Failed Tests',
            'All Tests'
        ] + sorted_methods
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for mutant in successful_mutants:
            # Prepare row data
            row_data = {
                'Mutant': f"{project_id}_{bug_id}_mutant_{mutant['mutant_id']}",
                'Line Coverage %': f"{mutant['coverage_percentage']:.2f}",
                'Mutator': mutant['mutator'],
                'Class Name': mutant['class_name'],
                'Line Number': mutant['line_number'],
                'Target File': mutant['target_file'],
                'Total Tests Count': mutant['total_tests_count'],
                'Failed Test Count': mutant['failed_test_count'],
                'Failed Tests': '; '.join(mutant['failed_tests']),
                'All Tests': '; '.join(mutant['all_tests'])
            }
            
            # Add method coverage data
            for method in sorted_methods:
                line_numbers = mutant['method_coverage'].get(method, [])
                row_data[method] = ','.join(line_numbers)
            
            writer.writerow(row_data)
    
    print(f"   Comprehensive CSV file created with {len(successful_mutants)} entries")
    print(f"   Total methods found: {len(sorted_methods)}")

def run_mutation_testing(work_dir):
    """Run Defects4J mutation testing"""
    print("   Running mutation testing...")
    
    try:
        result = subprocess.run(
            [DEFECTS4J_EXECUTABLE, "mutation"],
            capture_output=True, 
            text=True, 
            cwd=work_dir,
            timeout=300
        )
        
        print(f"   Mutation testing completed (return code: {result.returncode})")
        return True
        
    except Exception as e:
        print(f"   Mutation testing error: {e}")
        return False

def process_bug_for_mutants(project_id, bug_id):
    """Process a bug to create multiple mutants with single mutations and run coverage"""
    work_dir = BASE_CHECKOUT_DIR / f"{project_id}_{bug_id}f"
    mutants_output_dir = BASE_CHECKOUT_DIR / f"{project_id}_{bug_id}_mutants"
    
    print(f"This is the code for one mutant per project copy with parallel processing")
    
    # Clean up
    if work_dir.exists():
        shutil.rmtree(work_dir)
    if mutants_output_dir.exists():
        shutil.rmtree(mutants_output_dir)
    
    mutants_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Checkout and compile
    print("\n1.  Checking out and compiling project...")
    checkout_cmd = [DEFECTS4J_EXECUTABLE, "checkout", "-p", project_id, "-v", f"{bug_id}f", "-w", str(work_dir)]
    if not run_command(checkout_cmd, BASE_CHECKOUT_DIR, "Checkout"):
        return False
    
    if not run_command([DEFECTS4J_EXECUTABLE, "compile"], work_dir, "Compile"):
        return False
    
    # Step 2: Find source directories
    print("\n2.  Finding source directories...")
    abs_source_dirs = get_source_directories(work_dir)
    # Convert to relative paths so workers can reconstruct them in their own dirs
    relative_source_dirs = [p.relative_to(work_dir) for p in abs_source_dirs]
    
    if not abs_source_dirs:
        print("   No source directories found")
        return False
    
    # Step 3: Run mutation testing
    print("\n3.  Running mutation testing...")
    run_mutation_testing(work_dir)
    
    # Step 4: Find mutants.log
    print("\n4.  Finding mutants.log...")
    log_file = find_mutants_log(work_dir)
    if not log_file:
        print("   No mutants.log found")
        return False
    
    # Step 5: Parse all mutations
    print("\n5.  Parsing all mutations...")
    all_mutations = parse_all_mutations(log_file)
    if not all_mutations:
        print("   No mutations could be parsed")
        return False
    
    print("how many mutants do you want to create?")
    num_mutants = int(input())
    
    mutations_to_run = all_mutations[:num_mutants]
    
    print(f"\n5. Processing {len(mutations_to_run)} mutants with {MAX_WORKERS} workers...")
    
    successful_mutants = []
    failed_mutations = []
    
    worker_args = []
    for info in mutations_to_run:
        mutant_dir = BASE_CHECKOUT_DIR / f"{project_id}_{bug_id}_mutant_{info['mutant_id']}"
        # Pass the master dir, target dir, info, and RELATIVE source paths
        if mutant_dir.exists():
            shutil.rmtree(mutant_dir)
        worker_args.append((work_dir, mutant_dir, info, project_id, bug_id, relative_source_dirs))

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_mid = {executor.submit(apply_mutation_and_coverage_worker, arg): arg[2]['mutant_id'] for arg in worker_args}
        
        for future in as_completed(future_to_mid):
            mid = future_to_mid[future]
            try:
                result = future.result()
                if result:
                    successful_mutants.append(result)
                else:
                    failed_mutations.append(mid)
            except Exception as e:
                print(f"Worker Exception for {mid}: {e}")
                failed_mutations.append(mid)

  
    # Step 7: Create comprehensive coverage CSV file
    print("\n7.  Creating comprehensive coverage CSV file...")
    comprehensive_csv_file = mutants_output_dir / f"{project_id}_{bug_id}_mutant_coverage.csv"
    create_comprehensive_coverage_csv(successful_mutants, comprehensive_csv_file, project_id, bug_id)
    

def main():
    """Main function"""
    print(f" DEFECTS4J SINGLE MUTANT GENERATOR WITH PARALLEL PROCESSING")
    print(f"Creating mutants with one mutation per project copy and running coverage")
    print(f"Parallel workers: {MAX_WORKERS}")
    print("="*80)
    
    BASE_CHECKOUT_DIR.mkdir(exist_ok=True)
    prev_proj = "Math"

    for project, bug in BUGS_TO_PROCESS:
        if project != prev_proj:
            print("\n" + "="*80)
            print(" MERGING CSV FILES")
            print("="*80)

            # 1. Define output path
            merged_csv_path = BASE_CHECKOUT_DIR / f"{prev_proj}_All_Bugs_Merged.csv"
            
            # 2. Find all generated coverage CSV files recursively
            # We look for patterns like "Math_*_coverage.csv"
            print("   Scanning for CSV files...")
            all_csv_files = list(BASE_CHECKOUT_DIR.rglob(f"{prev_proj}_*_coverage.csv"))
            
            if not all_csv_files:
                print("   No CSV files found to merge.")
                return

            print(f"   Found {len(all_csv_files)} CSV files. Analyzing headers...")

            # 3. Pass 1: Collect ALL unique fieldnames (headers) from all files
            # This is necessary because Math-1 has different methods/columns than Math-50
            master_fieldnames = set()
            
            # These are the fixed columns that should appear first
            standard_columns = [
                'Mutant', 'Line Coverage %', 'Mutator', 'Class Name', 
                'Line Number', 'Target File', 'Total Tests Count', 
                'Failed Test Count', 'Failed Tests', 'All Tests'
            ]
            
            for csv_path in all_csv_files:
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        if reader.fieldnames:
                            master_fieldnames.update(reader.fieldnames)
                except Exception as e:
                    print(f"   Warning: Could not read headers from {csv_path.name}: {e}")

            # 4. Organize Headers: Standard columns first, then sorted dynamic method columns
            dynamic_columns = sorted([f for f in master_fieldnames if f not in standard_columns])
            final_header = standard_columns + dynamic_columns
            
            print(f"   Total unique columns: {len(final_header)}")
            print(f"   Merging data into {merged_csv_path}...")

            # 5. Pass 2: Write data to the master file
            total_rows = 0
            try:
                with open(merged_csv_path, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=final_header, extrasaction='ignore')
                    writer.writeheader()
                    
                    for csv_path in all_csv_files:
                        # print(f"   Merging {csv_path.name}...") # Optional: uncomment for verbose output
                        with open(csv_path, 'r', encoding='utf-8') as infile:
                            reader = csv.DictReader(infile)
                            for row in reader:
                                writer.writerow(row)
                                total_rows += 1
                                
                print(f"   SUCCESS: Merged {total_rows} rows from {len(all_csv_files)} files.")
                print(f"   Master CSV saved at: {merged_csv_path}")
                
            except Exception as e:
                print(f"   Error during merging: {e}")

            # --- MERGING CODE ENDS HERE ---

        print(f"\n{'='*80}")
        print(f" PROCESSING: {project}-{bug}")
        print(f"{'='*80}")
        
        success = process_bug_for_mutants(project, bug)
        status = " SUCCESS" if success else " FAILED"
        print(f"{status}: {project}-{bug}")
        prev_proj = project

    # MERGING ALL THE CSV
    


if __name__ == "__main__":
    main()