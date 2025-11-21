"""File operations utilities - PLATFORM INDEPENDENT"""

import shutil
import os
import platform
from pathlib import Path
from typing import List


class FileOperations:
    """Utility class for file operations - PLATFORM INDEPENDENT"""
    
    def __init__(self):
        self.system = platform.system().lower()
    
    def clean_directory(self, directory: Path) -> bool:
        """Remove directory if it exists - PLATFORM INDEPENDENT"""
        if not directory.exists():
            return True
            
        try:
            shutil.rmtree(directory)
            return True
        except PermissionError:
            print(f"Permission error cleaning {directory}")
            if self.system == "windows":
                # Try alternative approach on Windows
                return self._clean_directory_windows(directory)
            return False
        except Exception as e:
            print(f"Error cleaning directory {directory}: {e}")
            return False
    
    def _clean_directory_windows(self, directory: Path) -> bool:
        """Windows-specific directory cleaning"""
        try:
            # Use Windows command for stubborn directories
            import subprocess
            subprocess.run(f'rmdir /S /Q "{directory}"', shell=True, check=True)
            return True
        except:
            return False
    
    def ensure_directory(self, directory: Path) -> bool:
        """Ensure directory exists - PLATFORM INDEPENDENT"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False
    
    def get_relative_paths(self, absolute_paths: List[Path], base_dir: Path) -> List[Path]:
        """Convert absolute paths to relative paths - PLATFORM INDEPENDENT"""
        try:
            return [path.relative_to(base_dir) for path in absolute_paths]
        except ValueError as e:
            print(f"Error converting paths to relative: {e}")
            return []
    
    def read_file_lines(self, file_path: Path) -> List[str]:
        """Read file lines with platform-independent line ending handling"""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                return f.readlines()
        except UnicodeDecodeError:
            # Fallback for different encodings
            with open(file_path, 'r', newline='', encoding='latin-1') as f:
                return f.readlines()
    
    def write_file_lines(self, file_path: Path, lines: List[str]) -> bool:
        """Write file lines with platform-appropriate line endings"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False