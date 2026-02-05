import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Tuple, List
import re

from config.settings import DEFECTS4J_EXECUTABLE, COVERAGE_TIMEOUT


class CoverageRunner:
    """Handles coverage analysis and test execution"""
    
    def __init__(self):
        self.defects4j_cmd = DEFECTS4J_EXECUTABLE

    def run_defects4j_test(self, mutant_dir: Path) -> dict:
        """Run defects4j test and parse failed test cases and their names."""
        result = {
            'failed_count': 0,
            'failed_tests': [],
            'all_tests': [],
            'test_output': ''
        }
        try:
            proc = subprocess.run([
                self.defects4j_cmd, "test"
            ], capture_output=True, text=True, cwd=mutant_dir, timeout=COVERAGE_TIMEOUT)
            output = proc.stdout + proc.stderr
            result['test_output'] = output
            failed_tests = []
            in_failed_section = False
            for line in output.splitlines():
                if line.strip().startswith("Failing tests:"):
                    in_failed_section = True
                    continue
                if in_failed_section:
                    if not line.strip() or not line.strip().startswith("-"):
                        # End of failing tests section
                        in_failed_section = False
                        continue
                    # Extract test name after '- '
                    test_name = line.strip()[2:].strip()
                    if test_name:
                        failed_tests.append(test_name)
            result['failed_tests'] = failed_tests
            result['failed_count'] = len(failed_tests)
        except subprocess.TimeoutExpired:
            result['test_output'] = 'TIMEOUT'
        except Exception as e:
            result['test_output'] = f'ERROR: {e}'
        return result
    
    def run_command(self, command: List[str], working_dir: Path, step_name: str = "Command"):
        """Run a shell command with proper error handling"""
        print(f"    Running: {' '.join(command)}")
        try:
            result = subprocess.run(
                command, check=True, capture_output=True, text=True, cwd=working_dir
            )
            return result
        except subprocess.CalledProcessError as e:
            # Print full stdout/stderr for easier debugging (e.g., missing tools or compile errors)
            print(f"    Command failed: {e}")
            if hasattr(e, 'stdout') and e.stdout:
                print(f"    stdout:\n{e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"    stderr:\n{e.stderr}")
            return None
    
    def compile_mutant(self, mutant_dir: Path) -> bool:
        """Compile the mutant"""
        return bool(self.run_command([self.defects4j_cmd, "compile"], mutant_dir, "Compile mutant"))
    
    def parse_coverage_xml(self, xml_file: Path) -> Tuple[float, float, Dict[str, List[str]]]:
        """Parse coverage.xml and extract line-rate, branch-rate, and method coverage data"""
        method_data = {}
        line_rate = 0.0
        branch_rate = 0.0
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            # Get line-rate and branch-rate from root attributes
            line_rate = float(root.attrib.get('line-rate', '0'))
            branch_rate = float(root.attrib.get('branch-rate', '0'))
            for cls in root.findall('.//class'):
                class_name = cls.get('name')
                for method in cls.findall('.//method'):
                    method_name = method.get('name')
                    method_signature = method.get('signature', '')
                    full_method_name = f"{class_name}.{method_name}{method_signature}"
                    line_numbers = []
                    for line in method.findall('.//line'):
                        line_number = line.get('number')
                        hit_count = line.get('hits')
                        branch = line.get('branch')
                        if line_number:
                            if branch == 'true':
                                conditions_covered = line.get('condition-coverage', '')
                                line_numbers.append(f"{line_number}|{hit_count}|{conditions_covered}")
                            else:
                                line_numbers.append(f"{line_number}|{hit_count}")
                    method_data[full_method_name] = line_numbers
            return line_rate, branch_rate, method_data
        except Exception as e:
            print(f"Error parsing {xml_file}: {e}")
            return 0.0, 0.0, {}
    
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
        print(all_tests)
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
            'method_coverage': {},
            'branch_coverage': 0,
        }
        
        try:
            # Compile mutant first
            '''if not self.compile_mutant(mutant_dir):
                return coverage_result'''
            
            # Optionally, still run coverage for line/method coverage
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
                line_rate, branch_coverage, method_data = self.parse_coverage_xml(coverage_xml_file)
                coverage_result['coverage_percentage'] = line_rate
                coverage_result['branch_coverage'] = branch_coverage
                coverage_result['method_coverage'] = method_data
                print(f"   Line-rate: {coverage_result['coverage_percentage']:.4f}, Branch-coverage: {coverage_result['branch_coverage']:.4f}")
            # Run defects4j test and parse results
            print("   Running defects4j test...")
            test_result = self.run_defects4j_test(mutant_dir)
            coverage_result['failed_tests'] = test_result['failed_tests']
            coverage_result['failed_count'] = test_result['failed_count']
            coverage_result['all_tests'] = test_result['all_tests']
            coverage_result['total_tests'] = len(test_result['all_tests']) if test_result['all_tests'] else 0
            coverage_result['test_output'] = test_result['test_output']

           

            print(f"   Test completed - {coverage_result['failed_count']} tests failed")

        except subprocess.TimeoutExpired:
            print("   Coverage or test command timed out")
            coverage_result['coverage_output'] = "TIMEOUT"
            try:
                self._kill_processes_for_path(mutant_dir)
                coverage_result['coverage_output'] += "; killed lingering processes"
            except Exception as e:
                coverage_result['coverage_output'] += f"; cleanup error: {e}"
        except Exception as e:
            print(f"   Error running coverage/test: {e}")
            coverage_result['coverage_output'] = f"ERROR: {str(e)}"

        return coverage_result

    def _kill_processes_for_path(self, path: Path, timeout: int = 5):
        """Kill processes whose command line references the given path (best-effort).

        Uses pgrep -f to find matching processes, sends SIGTERM then SIGKILL after a short wait.
        """
        import subprocess, os, signal, time
        try:
            cmd = ["pgrep", "-f", str(path)]
            out = subprocess.check_output(cmd, text=True).strip()
            if not out:
                return
            pids = [int(p) for p in out.splitlines() if p.strip().isdigit()]
        except subprocess.CalledProcessError:
            return

        for pid in pids:
            try:
                print(f"   [CLEANUP] Terminating PID {pid} for path {path}")
                os.kill(pid, signal.SIGTERM)
            except Exception:
                pass

        time.sleep(timeout)

        for pid in pids:
            try:
                os.kill(pid, 0)
            except OSError:
                continue
            try:
                print(f"   [CLEANUP] Killing PID {pid} (SIGKILL)")
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass