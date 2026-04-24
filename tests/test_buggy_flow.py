"""Tests for fixed->buggy checkout flow."""

from pathlib import Path

from main import MutantGenerator


class _StubProjectManager:
    def __init__(self):
        self.calls = []

    def checkout_project_version(self, project_id: str, bug_id: str, version: str,
                                 work_dir: Path, compile_project: bool = True) -> bool:
        self.calls.append((
            "checkout",
            project_id,
            bug_id,
            version,
            work_dir,
            compile_project,
        ))
        return True

    def run_mutation_testing(self, work_dir: Path, test_name: str = "") -> bool:
        self.calls.append(("mutation", work_dir, test_name))
        return True

    def get_target_test(self, project_id: str, bug_id: str) -> str:
        return "org.example.Test::testSomething"


def test_setup_project_fixed_then_buggy(tmp_path):
    """Ensure fixed checkout + mutation testing precedes buggy checkout."""
    gen = MutantGenerator(max_workers=1, random_seed=1)
    stub_pm = _StubProjectManager()
    gen.project_manager = stub_pm

    fixed_dir = tmp_path / "Math_5f"
    buggy_dir = tmp_path / "Math_5b"

    ok = gen._setup_project("Math", "5", fixed_dir, buggy_dir)
    assert ok is True

    assert stub_pm.calls[0] == (
        "checkout",
        "Math",
        "5",
        "f",
        fixed_dir,
        True,
    )
    assert stub_pm.calls[1] == ("mutation", fixed_dir, "org.example.Test::testSomething")
    assert stub_pm.calls[2] == (
        "checkout",
        "Math",
        "5",
        "b",
        buggy_dir,
        False,
    )
