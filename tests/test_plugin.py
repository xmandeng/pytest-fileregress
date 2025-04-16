"""
Tests for the pytest-fileregress plugin.
"""

import os
import shutil
import tempfile

import pytest

from pytest_fileregress.data_generator import (
    copy_with_modifications,
    create_random_file,
    generate_test_data,
)

# Import from the package
from pytest_fileregress.plugin import compare_files, get_file_hash, inventory_files


@pytest.fixture
def temp_base_dir():
    """Create a temporary directory for base files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_get_file_hash(temp_base_dir):
    """Test the file hash function."""
    # Create a test file
    test_file = os.path.join(temp_base_dir, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("Test content")

    # Get the hash
    hash_value = get_file_hash(test_file)

    # Verify it's a valid hash
    assert isinstance(hash_value, str)
    assert len(hash_value) == 32  # MD5 hash is 32 characters


def test_inventory_files(temp_base_dir):
    """Test the file inventory function."""
    # Create some test files
    file1 = os.path.join(temp_base_dir, "file1.txt")
    file2 = os.path.join(temp_base_dir, "file2.txt")
    os.makedirs(os.path.join(temp_base_dir, "subdir"), exist_ok=True)
    file3 = os.path.join(temp_base_dir, "subdir", "file3.txt")

    # Write content to files
    for file_path in [file1, file2, file3]:
        with open(file_path, "w") as f:
            f.write(f"Content for {os.path.basename(file_path)}")

    # Get inventory
    inventory = inventory_files(temp_base_dir)

    # Verify inventory
    assert len(inventory) == 3
    assert "file1.txt" in inventory
    assert "file2.txt" in inventory
    assert os.path.join("subdir", "file3.txt") in inventory


def test_inventory_files_with_exclusions(temp_base_dir):
    """Test the file inventory function with exclusions."""
    # Create some test files
    file1 = os.path.join(temp_base_dir, "file1.txt")
    file2 = os.path.join(temp_base_dir, "file2.log")  # This will be excluded
    os.makedirs(os.path.join(temp_base_dir, "subdir"), exist_ok=True)
    file3 = os.path.join(temp_base_dir, "subdir", "file3.txt")

    # Write content to files
    for file_path in [file1, file2, file3]:
        with open(file_path, "w") as f:
            f.write(f"Content for {os.path.basename(file_path)}")

    # Get inventory with exclusions
    inventory = inventory_files(temp_base_dir, "*.log")

    # Verify inventory
    assert len(inventory) == 2
    assert "file1.txt" in inventory
    assert "file2.log" not in inventory
    assert os.path.join("subdir", "file3.txt") in inventory


def test_compare_files_identical(temp_base_dir, temp_test_dir):
    """Test the file comparison function with identical files."""
    # Create identical files in both directories
    file1 = os.path.join(temp_base_dir, "file1.txt")
    file2 = os.path.join(temp_test_dir, "file1.txt")

    content = "This is test content"
    for file_path in [file1, file2]:
        with open(file_path, "w") as f:
            f.write(content)

    # Compare files
    result = compare_files(file1, file2)

    # Verify result
    assert result is True


def test_compare_files_different(temp_base_dir, temp_test_dir):
    """Test the file comparison function with different files."""
    # Create different files in both directories
    file1 = os.path.join(temp_base_dir, "file1.txt")
    file2 = os.path.join(temp_test_dir, "file1.txt")

    with open(file1, "w") as f:
        f.write("This is test content")

    with open(file2, "w") as f:
        f.write("This is different content")

    # Compare files
    result = compare_files(file1, file2)

    # Verify result
    assert result is False


def test_create_random_file(temp_base_dir):
    """Test the random file creation function."""
    # Create a random file
    file_path = os.path.join(temp_base_dir, "random.txt")
    create_random_file(file_path, size_kb=1)

    # Verify the file exists and has content
    assert os.path.exists(file_path)
    with open(file_path, "r") as f:
        content = f.read()

    # File should be approximately 1KB
    assert len(content) >= 1000
    assert len(content) <= 1100


def test_copy_with_modifications(temp_base_dir, temp_test_dir):
    """Test the file copy with modifications function."""
    # Create a source file
    source_file = os.path.join(temp_base_dir, "source.txt")
    with open(source_file, "w") as f:
        f.write("Original content")

    # Copy with 100% modification rate to ensure it changes
    dest_file = os.path.join(temp_test_dir, "dest.txt")
    copy_with_modifications(source_file, dest_file, modify_percent=100)

    # Verify the destination file exists
    assert os.path.exists(dest_file)

    # Read content of both files
    with open(source_file, "r") as f:
        source_content = f.read()

    with open(dest_file, "r") as f:
        dest_content = f.read()

    # The destination should be different but same length
    assert len(source_content) == len(dest_content)
    assert source_content != dest_content


def test_generate_test_data(temp_base_dir, temp_test_dir):
    """Test the test data generation function."""
    # Generate test data
    generate_test_data(
        temp_base_dir,
        temp_test_dir,
        num_files=10,
        max_depth=1,
        modify_percent=50,
        missing_percent=20,
    )

    # Get inventory of both directories
    base_files = inventory_files(temp_base_dir)
    test_files = inventory_files(temp_test_dir)

    # Verify files were created
    assert len(base_files) > 0
    assert len(test_files) > 0

    # Some files should be only in the test directory
    only_in_test = [f for f in test_files if f not in base_files]
    assert len(only_in_test) > 0

    # Some files should be missing from the test directory
    only_in_base = [f for f in base_files if f not in test_files]
    assert len(only_in_base) > 0
    only_in_base = [f for f in base_files if f not in test_files]
    assert len(only_in_base) > 0
