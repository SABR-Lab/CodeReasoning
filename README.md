# Defects4J Parallel Mutant Generator

A parallel mutant generator for Defects4J dataset projects that creates unique mutants with configurable mutation combinations and does comprehensive coverage analysis.

## 🚀 Features

- **Parallel Processing**: Generate multiple mutants simultaneously (configurable workers)
- **Configurable Mutant Generation**: 
  - Percentage-based mutant selection (0-100%)
  - Multiple mutations per mutant (1-4 mutations)
  - Unique mutant combinations (no duplicates)
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Reproducible Results**: Deterministic mutant generation with random seeds
- **Comprehensive Analysis**:
  - Line coverage percentage
  - Method-level coverage details
  - Test failure analysis
  - CSV output with all metrics
- **Flexible Project Selection**: Process specific bugs or entire projects

## Prerequisites

### System Requirements

- Python 3.8 or higher
- Java 8 or higher
- Defects4J installed and in PATH

## Usage
```bash
git clone https://github.com/SABR-Lab/CodeReasoning.git
cd CodeReasoning

# Generate mutants for Math bug 1
python main.py --project "Math-1" --percentage 50 --max-mutations 2

# Results are saved in:
ls ~/defects4j_mutants/
```

## Command Line Arguments Understanding

| Argument | Description | Default | Example |
| :--- | :--- | :---: | :--- |
| `--project` | Project(s) to process | **Required** | `"Math-all"`, `"Math-1"`, `"Math-1,Math-2"` |
| `--percentage` | Percentage of mutants to create (0-100) | `50` | `--percentage 75` |
| `--max-mutations` | Maximum mutations per mutant (1-4) | `4` | `--max-mutations 2` |
| `--workers` | Number of parallel workers | `10` | `--workers 8` |

## Project Selection Formats

- Single bug: "Math-1"
- Multiple bugs: "Math-1,Math-2,Lang-1"
- All bugs in project: "Math-all"
- Multiple projects: "Math-1,Lang-1,Time-1"

## 📊 Output

The generator creates the following output structure:

```
/tmp/mutated_codes/
├── Math_1f/                 # Original project checkout
├── Math_1_mutants/          # Mutant results directory
│   └── Math_1_mutant_coverage.csv  # Comprehensive results
├── Math_2f/
├── Math_2_mutants/
│   └── Math_2_mutant_coverage.csv
└── Math_All_Bugs_Merged.csv # Merged results for all Math bugs
```

## CSV Output Columns

- Mutant: Unique mutant identifier
- Line Coverage %: Overall line coverage percentage
- Mutator: Mutation operator(s) applied
- Class Name: Target class
- Line Number: Modified line number(s)
- Target File: Source file path
- Test Counts: Total tests, failed tests
- Test Lists: All tests and failing tests
- Method Coverage: Line numbers covered per method
