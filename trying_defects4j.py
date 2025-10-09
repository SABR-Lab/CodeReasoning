import subprocess
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

DEFECTS4J_EXECUTABLE = "defects4j"
#first run in terminal export PATH=$PATH:"/Users/quibliss/research/defects4j"/framework/bin
#try all bugs mainly math to understand
BUGS_TO_PROCESS = [
    ("Chart", "1"),
    ("Chart", "2"),
    ("Lang", "10"),
    ("Math", "5"),
]

BASE_CHECKOUT_DIR = Path("/Users/quibliss/research")


def run_command(command, working_dir, step_name="Command"):
    """just commands of terminal for convenience."""
    print(f" Running: {' '.join(command)}")
    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=working_dir
        )
        print(f" {step_name} successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error during {step_name}.")
        print(f"  --- STDERR ---\n{e.stderr}\n  --------------")
        return False
    except FileNotFoundError:
        print(f"   Error: The command '{command[0]}' was not found.")
        print(f"  Please check the path in the DEFECTS4J_EXECUTABLE variable.")
        return False

# --- NEW FUNCTION ---
def parse_coverage_xml(xml_file):
    """Parses Cobertura coverage.xml"""
    print(f"   Parsing Cobertura coverage file: {xml_file}")
    if not xml_file.exists():
        print("   Coverage file not found!")
        return

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Cobertura stores summary data as attributes in the root <coverage> tag
        lines_covered = int(root.get('lines-covered'))
        lines_valid = int(root.get('lines-valid')) # 'lines-valid' is the total
        
        if lines_valid > 0:
            missed_lines = lines_valid - lines_covered
            coverage_percent = (lines_covered / lines_valid) * 100
        else:
            missed_lines = 0
            coverage_percent = 0

        print("\n  --- Code Coverage Summary ---")
        print(f"  Covered Lines: {lines_covered}")
        print(f"  Missed Lines:  {missed_lines}")
        print(f"  Total Lines:   {lines_valid}")
        print(f"  Line Coverage: {coverage_percent:.2f}%")
        print("  ---------------------------\n")

    except ET.ParseError as e:
        print(f"   Error parsing XML file: {e}")
    except (TypeError, KeyError) as e:
          print(f"  Could not find coverage attributes in the XML report. It's possible no tests were run.")

'''def parse_coverage_xml(xml_file):
    """Parses the coverage.xml file to extract and print key metrics."""
    print(f"   Parsing coverage file: {xml_file}")
    if not xml_file.exists():
        print("  Coverage file not found!")
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Find the line coverage counter from the JaCoCo XML report
    line_counter = root.find("counter[@type='LINE']")
    
    if line_counter is not None:
        missed = int(line_counter.get('missed'))
        covered = int(line_counter.get('covered'))
        total = missed + covered
        percent = (covered / total) * 100 if total > 0 else 0
        
        print("\n  --- Code Coverage Summary ---")
        print(f"  Covered Lines: {covered}")
        print(f"  Missed Lines:  {missed}")
        print(f"  Total Lines:   {total}")
        print(f"  Line Coverage: {percent:.2f}%")
        print("  ---------------------------\n")
    else:
        print("  Could not find line coverage data in the XML report.")

'''

def process_bug(project_id, bug_id):

    work_dir = BASE_CHECKOUT_DIR / f"{project_id}_{bug_id}b"

    if work_dir.exists():
        shutil.rmtree(work_dir)
        
    checkout_cmd = [
        DEFECTS4J_EXECUTABLE, "checkout",
        "-p", project_id,
        "-v", f"{bug_id}b",
        "-w", str(work_dir)
    ]
    if not run_command(checkout_cmd, BASE_CHECKOUT_DIR, "Checkout"):
        return False

    compile_cmd = [DEFECTS4J_EXECUTABLE, "compile"]
    if not run_command(compile_cmd, work_dir, "Compile"):
        return False

    coverage_cmd = [DEFECTS4J_EXECUTABLE, "coverage"]
    if not run_command(coverage_cmd, work_dir, "Coverage"):
        return False
        
    coverage_file = work_dir / "coverage.xml"
    parse_coverage_xml(coverage_file)


    return True


def main():
   
    if "your/path" in DEFECTS4J_EXECUTABLE:
        print("  Warning: Please update the DEFECTS4J_EXECUTABLE variable in the script.")
        return

    print(f"Starting to process {len(BUGS_TO_PROCESS)} bugs...\n")
    BASE_CHECKOUT_DIR.mkdir(exist_ok=True)
    
    succeeded, failed = [], []
    
    for project, bug in BUGS_TO_PROCESS:
        bug_name = f"{project}-{bug}"
        print(f"--- Processing {bug_name} ---")
        if process_bug(project, bug):
            succeeded.append(bug_name)
        else:
            failed.append(bug_name)
        print("-" * (len(bug_name) + 16) + "\n")
        
    print("\n--- Final Summary ---")
    print(f"Succeeded: {len(succeeded)} ({', '.join(succeeded)})")
    print(f"Failed:    {len(failed)} ({', '.join(failed)})")
    print("----------------------")


if __name__ == "__main__":
    main()
