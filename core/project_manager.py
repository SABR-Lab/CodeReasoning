"""Manages Defects4J project operations - PLATFORM INDEPENDENT"""

import shutil
import subprocess
import os
import platform
from pathlib import Path
from typing import List

from config.settings import DEFECTS4J_EXECUTABLE, BASE_CHECKOUT_DIR


class ProjectManager:
    """Handles project checkout, compilation, and setup - PLATFORM INDEPENDENT"""
    
    def __init__(self, base_dir: Path = BASE_CHECKOUT_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(exist_ok=True)
        self.system = platform.system().lower()
        
    def _get_defects4j_command(self) -> str:
        """Get platform-appropriate Defects4J command"""
        if self.system == "windows":
            return f"{DEFECTS4J_EXECUTABLE}.bat"  # Windows batch file
        else:
            return DEFECTS4J_EXECUTABLE  # Unix shell script
    
    def _run_platform_command(self, command: List[str], work_dir: Path, 
                            timeout: int = 300) -> bool:
        """Run command with platform-specific considerations"""
        try:
            # Handle command formatting for different platforms
            if self.system == "windows":
                # On Windows, we might need to use shell=True for some commands
                result = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=work_dir,
                    timeout=timeout,
                    shell=True  # May be needed on Windows
                )
            else:
                # On Unix-like systems, shell=False is generally safer
                result = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=work_dir,
                    timeout=timeout,
                    shell=False
                )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}")
            return False
        except subprocess.TimeoutExpired:
            print("Command timed out")
            return False
        except FileNotFoundError:
            print(f"Command not found: {command[0]}")
            return False
    
    def checkout_project(self, project_id: str, bug_id: str, work_dir: Path) -> bool:
        """Checkout and compile a specific project version - PLATFORM INDEPENDENT"""
        if work_dir.exists():
            self._clean_directory(work_dir)
        
        defects4j_cmd = self._get_defects4j_command()
        
        checkout_cmd = [
            defects4j_cmd, "checkout", "-p", project_id, 
            "-v", f"{bug_id}f", "-w", str(work_dir)
        ]
        
        print(f"Checking out {project_id}-{bug_id}f using: {' '.join(checkout_cmd)}")
        
        try:
            result = subprocess.run(
                checkout_cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                cwd=self.base_dir, 
                timeout=300
            )
            print(f"✓ Checked out {project_id}-{bug_id}f")
            return self.compile_project(work_dir)
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to checkout project: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"✗ Defects4J command not found: {defects4j_cmd}")
            print("Please ensure Defects4J is installed and in your PATH")
            return False
    
    def _clean_directory(self, directory: Path):
        """Clean directory with platform-specific error handling"""
        if directory.exists():
            try:
                shutil.rmtree(directory)
            except PermissionError:
                print(f"Warning: Could not delete {directory} due to permission issues")
                # On Windows, files might be locked
                if self.system == "windows":
                    print("On Windows, try closing any open files or IDEs")
            except Exception as e:
                print(f"Warning: Could not clean directory {directory}: {e}")
    
    def compile_project(self, work_dir: Path) -> bool:
        """Compile the project"""
        try:
            result = subprocess.run(
                [DEFECTS4J_EXECUTABLE, "compile"],
                check=True, capture_output=True, text=True, cwd=work_dir,
                timeout=300
            )
            print("✓ Project compiled successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to compile project: {e}")
            return False
    
    def run_mutation_testing(self, work_dir: Path) -> bool:
        """Run mutation testing to generate mutants.log"""
        try:
            result = subprocess.run(
                [DEFECTS4J_EXECUTABLE, "mutation"],
                check=True, capture_output=True, text=True, cwd=work_dir,
                timeout=720
            )
            print("✓ Mutation testing completed")
            return True
        except Exception as e:
            print(f"✗ Mutation testing failed: {e}")
            return False
    
    def get_source_directories(self, work_dir: Path) -> List[Path]:
        """Find all source directories in the project"""
        source_dirs = []
        
        possible_dirs = [
            work_dir / "src",
            work_dir / "src/main/java",
            work_dir / "src/java",
            work_dir / "source",
            work_dir / "Source",
        ]
        
        # Check predefined directories
        for dir_path in possible_dirs:
            if dir_path.exists():
                source_dirs.append(dir_path)
        
        # Try Defects4J export
        try:
            proc = subprocess.run(
                [DEFECTS4J_EXECUTABLE, "export", "-p", "dir.src.classes"],
                capture_output=True, text=True, check=True, cwd=work_dir
            )
            def_src_dir = work_dir / proc.stdout.strip()
            if def_src_dir.exists() and def_src_dir not in source_dirs:
                source_dirs.append(def_src_dir)
        except:
            pass
        
        # Search for Java files
        java_dirs = set()
        for java_file in work_dir.rglob("*.java"):
            java_dirs.add(java_file.parent)
        
        for java_dir in java_dirs:
            if any(pattern in str(java_dir) for pattern in ['src', 'java', 'source']):
                if java_dir not in source_dirs:
                    source_dirs.append(java_dir)
        
        print(f"Found {len(source_dirs)} source directories")
        return source_dirs