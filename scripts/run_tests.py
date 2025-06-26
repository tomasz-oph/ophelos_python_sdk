#!/usr/bin/env python3
"""
Test runner script for Ophelos SDK.

This script provides convenient ways to run different types of tests.
"""

import argparse
import subprocess
import sys


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(description="Run Ophelos SDK tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests (default)")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests including integration")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage report")
    parser.add_argument("--fast", action="store_true", help="Run tests without coverage for faster execution")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Base command
    cmd = ["python", "-m", "pytest"]

    # Determine which tests to run
    if args.integration:
        cmd.extend(["-m", "integration"])
    elif args.all:
        pass  # Run all tests
    else:
        # Default: run unit tests only (exclude integration)
        cmd.extend(["-m", "not integration"])

    # Add coverage options
    if args.coverage or not args.fast:
        cmd.extend(["--cov=ophelos", "--cov-report=term-missing", "--cov-report=html"])

    # Add verbosity
    if args.verbose:
        cmd.append("-v")

    # Fast mode - minimal output
    if args.fast:
        cmd.extend(["--tb=line", "-q"])
    else:
        cmd.append("--tb=short")

    # Run the tests
    exit_code = run_command(cmd)

    if exit_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage or not args.fast:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
