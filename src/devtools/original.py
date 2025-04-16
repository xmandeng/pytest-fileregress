import mywork.reports as reports  # type: ignore
import pytest

# CLI Usage:
# pytest --no-cov -v regression__reports.py
#   --base_folder s3://bucket/prefix
#   --test_folder s3://bucket/prefix
#   --exclude rexeg

# Note: --exclude' supports regular expressions (regex) allowing you to get fancy


# Create parametrize file list using CLI arguments
def pytest_generate_tests(metafunc):
    if "base_folder" in metafunc.fixturenames and "test_folder" in metafunc.fixturenames:
        base_folder = metafunc.config.getoption("base_folder")
        test_folder = metafunc.config.getoption("test_folder")
        exclude = metafunc.config.getoption("exclude")
        base_files_dict = reports.inventory_folders(base_folder, exclusions=exclude)
        test_files_dict = reports.inventory_folders(test_folder, exclusions=exclude)

        metafunc.parametrize(
            "file",
            set(base_files_dict).union(test_files_dict),
        )


@pytest.fixture
def base_folder(pytestconfig):
    return pytestconfig.getoption("base_folder")


@pytest.fixture
def test_folder(pytestconfig):
    return pytestconfig.getoption("test_folder")


@pytest.fixture
def test_dict(test_folder):
    return reports.inventory_folders(test_folder)


@pytest.fixture
def base_dict(base_folder):
    return reports.inventory_folders(base_folder)


def test_compare_reports(test_dict, base_dict, file):
    if file not in test_dict:
        print(f"[FAIL] Missing file: {file}")
        assert False

    if file not in base_dict:
        print(f"[FAIL] Extra file: {file}")
        assert False

    if not reports.compare_reports(base_dict[file], test_dict[file]):
        print(f"[FAIL] Content changed: {file}")
        assert False

    assert True
