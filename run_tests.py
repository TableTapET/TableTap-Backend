#!/usr/bin/env python
"""
Test runner script for TableTap Backend
This script provides convenient ways to run different types of tests.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")

    try:
        subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"\n{description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{description} failed with exit code {e.returncode}")
        return False


def run_accounts_tests():
    """Run accounts tests"""
    command = "python -m pytest apps/accounts/tests/ -v --tb=short"
    return run_command(command, "Accounts Tests")


def run_all_tests():
    """Run all tests"""
    command = "python -m pytest apps/ -v --tb=short"
    return run_command(command, "All Tests")


def run_coverage_tests():
    """Run tests with coverage"""
    command = (
        "python -m pytest apps/ --cov=apps.accounts "
        "--cov-report=html --cov-report=term-missing"
    )
    return run_command(command, "Tests with Coverage")


def run_specific_test(test_path):
    """Run a specific test file or test function"""
    command = f"python -m pytest {test_path} -v --tb=short"
    return run_command(command, f"Specific Test: {test_path}")


def run_marked_tests(marker):
    """Run tests with specific markers"""
    command = f"python -m pytest apps/ -m {marker} -v --tb=short"
    return run_command(command, f"Tests with marker: {marker}")


def lint_tests():
    """Run linting on test files"""
    command = "python -m flake8 apps/*/tests/ --max-line-length=88 --ignore=E203,W503"
    return run_command(command, "Test Linting")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="TableTap Backend Test Runner")
    parser.add_argument("--accounts", action="store_true", help="Run account tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage"
    )
    parser.add_argument("--test", type=str, help="Run specific test file or function")
    parser.add_argument("--marker", type=str, help="Run tests with specific marker")
    parser.add_argument("--lint", action="store_true", help="Run linting on test files")
    parser.add_argument(
        "--quick", action="store_true", help="Run quick tests (no coverage)"
    )

    args = parser.parse_args()

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    print("TableTap Backend Test Runner")
    print("=" * 60)

    success = True

    if args.accounts:
        success &= run_accounts_tests()
    elif args.all:
        success &= run_all_tests()
    elif args.coverage:
        success &= run_coverage_tests()
    elif args.test:
        success &= run_specific_test(args.test)
    elif args.marker:
        success &= run_marked_tests(args.marker)
    elif args.lint:
        success &= lint_tests()
    elif args.quick:
        success &= run_all_tests()
    else:
        # Default: run all tests
        print("No specific option provided. Running all tests...")
        success &= run_all_tests()

    print(f"\n{'='*60}")
    if success:
        print("All tests completed successfully!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
