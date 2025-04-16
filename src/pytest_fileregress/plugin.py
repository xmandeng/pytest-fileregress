"""
pytest-fileregress: A pytest plugin for parameterized file comparison between directories.

This plugin provides functionality for comparing files between two directories.
It can be used to detect regressions in file outputs.
"""

import glob
import hashlib
import os
from typing import Dict, Optional

import pytest


def get_file_hash(filepath: str) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def inventory_files(folder: str, exclusions: Optional[str] = None) -> Dict[str, str]:
    """
    Inventory all files in a folder and calculate their hashes.

    Args:
        folder: Path to folder to inventory
        exclusions: Pattern to exclude (glob-style)

    Returns:
        Dict mapping relative file paths to their hash values
    """
    result = {}

    # Get all files in folder, including subdirectories
    all_files = glob.glob(os.path.join(folder, "**"), recursive=True)

    # Filter out directories and excluded files
    files = [f for f in all_files if os.path.isfile(f)]

    if exclusions:
        excluded = glob.glob(os.path.join(folder, exclusions), recursive=True)
        files = [f for f in files if f not in excluded]

    # Calculate relative paths and hashes
    for filepath in files:
        rel_path = os.path.relpath(filepath, folder)
        file_hash = get_file_hash(filepath)
        result[rel_path] = file_hash

    return result


def compare_files(base_path: str, test_path: str) -> bool:
    """
    Compare two files to check if they are identical.

    Args:
        base_path: Path to base file
        test_path: Path to test file

    Returns:
        True if files are identical, False otherwise
    """
    base_hash = get_file_hash(base_path)
    test_hash = get_file_hash(test_path)
    return base_hash == test_hash


# --- Pytest Configuration ---


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption("--base_folder", required=True, help="Base folder for comparison")
    parser.addoption("--test_folder", required=True, help="Test folder for comparison")
    parser.addoption("--exclude", default="", help="Glob pattern to exclude files")


# --- Pytest Fixtures ---


def pytest_configure(config):
    """Register the plugin with pytest."""
    config.addinivalue_line("markers", "fileregress: mark test as a file regression test")


def pytest_collect_file(parent, path):
    """Custom file collector for fileregress tests."""
    # This hook could be implemented to create a custom test collector
    # Currently not needed as we use parameterization
    return None


# --- Pytest Fixtures ---


def pytest_fixture_setup(fixturedef, request):
    """Setup fixtures for the plugin."""
    # This hook could be used for fixture setup if needed
    pass


@pytest.fixture
def base_folder(pytestconfig):
    """Get base folder path from command line arguments."""
    return pytestconfig.getoption("base_folder")


@pytest.fixture
def test_folder(pytestconfig):
    """Get test folder path from command line arguments."""
    return pytestconfig.getoption("test_folder")


@pytest.fixture
def exclude_pattern(pytestconfig):
    """Get exclusion pattern from command line arguments."""
    return pytestconfig.getoption("exclude")


@pytest.fixture
def base_files(base_folder, exclude_pattern):
    """Get inventory of files in base folder."""
    return inventory_files(base_folder, exclude_pattern)


@pytest.fixture
def test_files(test_folder, exclude_pattern):
    """Get inventory of files in test folder."""
    return inventory_files(test_folder, exclude_pattern)


# --- Test Generation ---


def pytest_generate_tests(metafunc):
    """Generate parameterized tests for each file."""
    if {"base_folder", "test_folder"}.issubset(set(metafunc.fixturenames)):
        # Get command line arguments
        base_folder = metafunc.config.getoption("base_folder")
        test_folder = metafunc.config.getoption("test_folder")
        exclude = metafunc.config.getoption("exclude")

        # Get file inventories
        base_files_dict = inventory_files(base_folder, exclude)
        test_files_dict = inventory_files(test_folder, exclude)

        # Combine file sets (properly this time!)
        all_files = set(base_files_dict) | set(test_files_dict)

        # Parametrize with the combined files
        if "file_path" in metafunc.fixturenames:
            metafunc.parametrize("file_path", all_files)


# --- Default Test Functions ---


@pytest.mark.fileregress
def test_file_exists_in_both(base_folder, test_folder, base_files, test_files, file_path):
    """Test that file exists in both folders."""
    assert file_path in base_files, f"File missing in base folder: {file_path}"
    assert file_path in test_files, f"File missing in test folder: {file_path}"


@pytest.mark.fileregress
def test_files_are_identical(base_folder, test_folder, base_files, test_files, file_path):
    """Test that files with the same name have identical content."""
    # Skip test if file doesn't exist in both folders
    if file_path not in base_files or file_path not in test_files:
        pytest.skip(f"File {file_path} not present in both folders")

    # Get full paths
    base_full_path = os.path.join(base_folder, file_path)
    test_full_path = os.path.join(test_folder, file_path)

    # Compare files
    assert compare_files(base_full_path, test_full_path), f"Files are different: {file_path}"


# --- Main function for standalone usage ---


def main():
    """Main function for standalone usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Compare files between two folders")
    parser.add_argument("--base_folder", required=True, help="Base folder for comparison")
    parser.add_argument("--test_folder", required=True, help="Test folder for comparison")
    parser.add_argument("--exclude", default="", help="Glob pattern to exclude files")
    args = parser.parse_args()

    # Get file inventories
    print(f"Analyzing files in {args.base_folder} and {args.test_folder}...")
    base_files = inventory_files(args.base_folder, args.exclude)
    test_files = inventory_files(args.test_folder, args.exclude)

    # Find all unique files
    all_files = set(base_files) | set(test_files)

    # Analyze and report
    print(f"Found {len(all_files)} unique files across both folders")
    print(f"Base folder has {len(base_files)} files")
    print(f"Test folder has {len(test_files)} files")

    # Check for missing files
    missing_in_base = [f for f in all_files if f not in base_files]
    missing_in_test = [f for f in all_files if f not in test_files]

    if missing_in_base:
        print(f"\nFiles missing in base folder ({len(missing_in_base)}):")
        for f in missing_in_base:
            print(f"  - {f}")

    if missing_in_test:
        print(f"\nFiles missing in test folder ({len(missing_in_test)}):")
        for f in missing_in_test:
            print(f"  - {f}")

    # Check for different content
    common_files = set(base_files) & set(test_files)
    different_files = []

    for file_path in common_files:
        if base_files[file_path] != test_files[file_path]:
            different_files.append(file_path)

    if different_files:
        print(f"\nFiles with different content ({len(different_files)}):")
        for f in different_files:
            print(f"  - {f}")

    # Summary
    total_issues = len(missing_in_base) + len(missing_in_test) + len(different_files)
    if total_issues == 0:
        print("\nAll files are identical across both folders!")
        return 0
    else:
        print(f"\nFound {total_issues} issues in total")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
    sys.exit(main())
