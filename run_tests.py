#!/usr/bin/env python3
"""
Simple test runner script for Contextinator.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --coverage   # Run with coverage report
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list, description: str) -> int:
    """Run a command and return exit code."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run Contextinator tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--file", type=str, help="Run specific test file")
    parser.add_argument("--fast", action="store_true", help="Stop at first failure")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add stop-on-failure
    if args.fast:
        cmd.append("-x")
    
    # Add coverage
    if args.coverage or args.html:
        cmd.extend([
            "--cov=src/contextinator",
            "--cov-report=term"
        ])
        if args.html:
            cmd.append("--cov-report=html")
    
    # Add test selection
    if args.file:
        cmd.append(args.file)
    elif args.unit:
        cmd.extend(["tests/", "-m", "not integration"])
    elif args.integration:
        cmd.extend(["tests/integration/", "-m", "integration"])
    else:
        cmd.append("tests/")
    
    # Run tests
    exit_code = run_command(cmd, "Running Contextinator Tests")
    
    # Print coverage report location
    if args.html:
        print(f"\n{'='*60}")
        print("  Coverage HTML report generated!")
        print(f"  Open: {Path.cwd()}/htmlcov/index.html")
        print(f"{'='*60}\n")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
