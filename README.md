# pytest-fileregress

A pytest plugin for parameterized file comparison between directories that makes regression testing of file outputs easy and efficient.

## Features

- Parameterized testing of files across directories
- Automatic detection of file differences
- Support for excluding files using glob patterns
- Detailed reporting of missing, modified, and extra files
- Command-line interface for standalone usage

## Installation

```bash
# Install from PyPI (once published)
pip install pytest-fileregress

# For development installation
git clone https://github.com/YOUR_USERNAME/pytest-fileregress.git
cd pytest-fileregress
poetry install
```

## Basic Usage

### As a pytest plugin

```python
# test_my_reports.py
import pytest

def test_report_outputs(base_folder, test_folder, file_path):
    """This test will be run once for each file found in either folder."""
    # The plugin handles the comparisons automatically
    pass
```

Run with:

```bash
pytest -v test_my_reports.py --base_folder=./reference_data --test_folder=./current_data
```

### As a standalone tool

```bash
python -m pytest_fileregress --base_folder=./reference_data --test_folder=./current_data
```

## How It Works

The plugin uses pytest's powerful parameterization feature to dynamically create test cases for each file found in the base and test directories. When you run your tests, it:

1. Inventories all files in both directories
2. Compares files that exist in both locations
3. Reports any missing, additional, or modified files

This approach is especially useful for regression testing, where you want to ensure that changes to your code don't unexpectedly affect output files.

## Advanced Usage

### Excluding files

You can exclude files using glob patterns:

```bash
pytest -v test_my_reports.py --base_folder=./reference_data --test_folder=./current_data --exclude="*.log,temp/*"
```

### Creating test data

For development and testing, you can use the included data generator:

```bash
python -m pytest_fileregress.data_generator --base_folder=./base_data --test_folder=./test_data --num_files=30
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
