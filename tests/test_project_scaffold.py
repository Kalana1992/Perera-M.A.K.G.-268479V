from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_project_config_exists():
    assert (ROOT / "config" / "project.yaml").is_file()

def test_raw_data_directory_exists():
    assert (ROOT / "data" / "raw").is_dir()

def test_main_entry_point_exists():
    assert (ROOT / "src" / "main.py").is_file()
