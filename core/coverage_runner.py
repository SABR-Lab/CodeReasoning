"""Runs coverage analysis and test execution"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Tuple, List

from config.settings import DEFECTS4J_EXECUTABLE, COVERAGE_TIMEOUT


class CoverageRunner:
    """Handles coverage analysis and test execution"""
    
    def __init__(self):
        self.defects4j_cmd = DEFECTS4J_EXECUTABLE
    
    def run_command(self, command: List[str], working_dir: Path, step_name: str = "Command"):
        """Run a shell command with proper error handling"""
        print(f"    Running: {' '.join(command)}")
        try:
            result = subprocess.run(
                command, check=True, capture_output=True, text=True, cwd=working_dir
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"    Command failed: {e}")
            return None
    
    def compile_mutant(self, mutant_dir: Path) -> bool:
        """Compile the mutant"""
        return bool(self.run_command([self.defects4j_cmd, "compile"], mutant_dir, "Compile mutant"))
    
    def parse_coverage_xml(self, xml_file: Path) -> Tuple[float, Dict[str, List[str]]]:
        """Parse coverage.xml and extract method coverage data"""
        method_data = {}
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            total_lines = covered_lines = 0
            
            for cls in root.findall('.//class'):
                class_name = cls.get('name')
                
                for method in cls.findall('.//method'):
                    method_name = method.get('name')
                    method_signature = method.get('signature', '')
                    
                    full_method_name = f"{class_name}.{method_name}{method_signature}"
                    line_numbers = []
                    
                    for line in method.findall('.//line'):
                        line_number = line.get('number')
                        if line_number:
                            line_numbers.append(line_number)
                        
                        total_lines += 1
                        if line.get('hits') != '0':
                            covered_lines += 1
                    
                    method_data[full_method_name] = line_numbers
            
            coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            return coverage_percentage, method_data
            
        except Exception as e:
            print(f"Error parsing {xml_file}: {e}")
            return 0, {}
    
    def parse_failing_tests(self, mutant_dir: Path) -> List[str]:
        """Parse failing tests from failing_tests file"""
        failing_tests_file = mutant_dir / "failing_tests"
        failed_tests = []
        
        if failing_tests_file.exists():
            try:
                with open(failing_tests_file, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        stripped_line = line.strip()
                        if stripped_line.startswith('--- '):
                            test_name = stripped_line[4:].strip()
                            if test_name:
                                failed_tests.append(test_name)
            except Exception as e:
                print(f"Error reading failing tests: {e}")
        
        return failed_tests
    
    def read_all_tests(self, mutant_dir: Path) -> List[str]:
        """Read all tests from all_tests file"""
        all_tests_file = mutant_dir / "all_tests"
        all_tests = []
        
        if all_tests_file.exists():
            try:
                with open(all_tests_file, 'r') as f:
                    all_tests = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error reading all_tests: {e}")
        
        return all_tests
    
    def run_coverage_analysis(self, mutant_dir: Path, project_id: str, bug_id: str) -> Dict:
        """Run comprehensive coverage analysis on mutant"""
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
            # Compile mutant first
            if not self.compile_mutant(mutant_dir):
                return coverage_result
            
            # Run coverage
            print("   Running defects4j coverage...")
            coverage_process = subprocess.run(
                [self.defects4j_cmd, "coverage", "-r"],
                capture_output=True, text=True, cwd=mutant_dir,
                timeout=COVERAGE_TIMEOUT
            )
            
            coverage_result['coverage_output'] = coverage_process.stdout + coverage_process.stderr
            coverage_result['coverage_success'] = (coverage_process.returncode == 0)
            
            # Parse coverage XML
            coverage_xml_file = mutant_dir / "coverage.xml"
            if coverage_xml_file.exists():
                coverage_percentage, method_data = self.parse_coverage_xml(coverage_xml_file)
                coverage_result['coverage_percentage'] = coverage_percentage
                coverage_result['method_coverage'] = method_data
                print(f"   Line coverage: {coverage_percentage:.2f}%")
            
            # Parse test results
            coverage_result['failed_tests'] = self.parse_failing_tests(mutant_dir)
            coverage_result['failed_count'] = len(coverage_result['failed_tests'])
            coverage_result['all_tests'] = self.read_all_tests(mutant_dir)
            coverage_result['total_tests'] = len(coverage_result['all_tests'])
            
            print(f"   Coverage completed - {coverage_result['failed_count']}/{coverage_result['total_tests']} tests failed")
            
        except subprocess.TimeoutExpired:
            print("   Coverage command timed out")
            coverage_result['coverage_output'] = "TIMEOUT"
        except Exception as e:
            print(f"   Error running coverage: {e}")
            coverage_result['coverage_output'] = f"ERROR: {str(e)}"
        
        return coverage_result