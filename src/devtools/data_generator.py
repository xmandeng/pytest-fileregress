"""
Data generator utility for testing the pytest-fileregress plugin.

This module creates test data with controlled differences between two directories.
It helps in verifying the functionality of the plugin in a controlled environment.
"""

import argparse
import os
import random
import string


def create_random_file(filepath, size_kb=1):
    """Create a file with random content of specified size."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Generate random content
    size_bytes = size_kb * 1024
    content = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(size_bytes)
    )

    # Write to file
    with open(filepath, "w") as f:
        f.write(content)


def copy_with_modifications(source_path, dest_path, modify_percent=20):
    """Copy a file with potential modifications."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # Read source file
    with open(source_path, "r") as f:
        content = f.read()

    # Randomly decide whether to modify this file
    if random.randint(1, 100) <= modify_percent:
        # Simple modification: change a random character
        if content:
            pos = random.randint(0, len(content) - 1)
            chars = list(content)
            chars[pos] = random.choice(string.ascii_letters)
            content = "".join(chars)

    # Write to destination
    with open(dest_path, "w") as f:
        f.write(content)


def generate_test_data(
    base_folder, test_folder, num_files=20, max_depth=2, modify_percent=20, missing_percent=10
):
    """Generate test data structure with controlled differences."""
    # Ensure folders exist
    os.makedirs(base_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Generate random folder structure and files
    for i in range(num_files):
        # Create random subfolder path
        depth = random.randint(0, max_depth)
        subfolder_parts = [random.choice(string.ascii_lowercase) for _ in range(depth)]
        subfolder = os.path.join(*subfolder_parts) if subfolder_parts else ""

        # Create random filename
        filename = f"file_{i}_{random.randint(1000, 9999)}.txt"

        # Full paths
        base_path = os.path.join(base_folder, subfolder, filename)
        test_path = os.path.join(test_folder, subfolder, filename)

        # Create file in base folder
        create_random_file(base_path, random.randint(1, 5))

        # Randomly decide whether to include in test folder
        if random.randint(1, 100) > missing_percent:
            copy_with_modifications(base_path, test_path, modify_percent)

    # Add some files only in test folder
    extra_files = random.randint(1, int(num_files * 0.2))
    for i in range(extra_files):
        # Create random subfolder path
        depth = random.randint(0, max_depth)
        subfolder_parts = [random.choice(string.ascii_lowercase) for _ in range(depth)]
        subfolder = os.path.join(*subfolder_parts) if subfolder_parts else ""

        # Create random filename
        filename = f"extra_file_{i}_{random.randint(1000, 9999)}.txt"

        # Full path in test folder only
        test_path = os.path.join(test_folder, subfolder, filename)

        # Create file in test folder
        create_random_file(test_path, random.randint(1, 5))

    print(f"Created {num_files} files in base folder")
    print(f"Added {extra_files} extra files in test folder")
    print(f"Modified approximately {modify_percent}% of files")
    print(f"Omitted approximately {missing_percent}% of files from test folder")


def main():
    """Main entry point for data generator."""
    parser = argparse.ArgumentParser(description="Generate test data for file comparison")
    parser.add_argument(
        "--base_folder", default="./base_data", help="Base folder to generate files in"
    )
    parser.add_argument(
        "--test_folder", default="./test_data", help="Test folder to generate files in"
    )
    parser.add_argument("--num_files", type=int, default=20, help="Number of files to generate")
    parser.add_argument("--max_depth", type=int, default=2, help="Maximum subfolder depth")
    parser.add_argument(
        "--modify_percent", type=int, default=20, help="Percentage of files to modify"
    )
    parser.add_argument(
        "--missing_percent",
        type=int,
        default=10,
        help="Percentage of files to omit from test folder",
    )

    args = parser.parse_args()

    generate_test_data(
        args.base_folder,
        args.test_folder,
        args.num_files,
        args.max_depth,
        args.modify_percent,
        args.missing_percent,
    )


if __name__ == "__main__":
    main()
