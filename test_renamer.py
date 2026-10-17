#!/usr/bin/env python3
"""Test cases cho renamer.py sử dụng pytest."""

import tempfile
from pathlib import Path

import renamer


def setup_test_files(tmp_path, count: int = 5):
    """Tạo file test với số từ 1 đến count."""
    for i in range(1, count + 1):
        (tmp_path / f"file_{i:03d}.txt").touch()
    return tmp_path


def test_rename_files_basic(tmp_path):
    """Test đổi tên cơ bản."""
    setup_test_files(tmp_path, 5)
    results = renamer.rename_files(tmp_path, "{n:03d}_{name}")
    assert (tmp_path / "001_file_1.txt").exists()
    assert (tmp_path / "002_file_2.txt").exists()
    assert (tmp_path / "003_file_3.txt").exists()
    assert (tmp_path / "004_file_4.txt").exists()
    assert (tmp_path / "005_file_5.txt").exists()


def test_dry_run_mode(tmp_path):
    """Test chế độ dry-run."""
    setup_test_files(tmp_path, 3)
    renamer.rename_files(tmp_path, "{n:03d}_{name}", dry_run=True)
    assert (tmp_path / "file_001.txt").exists()
    assert (tmp_path / "file_002.txt").exists()
    assert (tmp_path / "file_003.txt").exists()


def test_nonexistent_directory(tmp_path):
    """Test với thư mục không tồn tại."""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            renamer.rename_files(Path(tmp) / "nonexistent", "{n:03d}_{name}")
            assert False, "Nên raise FileNotFoundError"
        except FileNotFoundError:
            pass


def test_invalid_pattern(tmp_path):
    """Test với mẫu chứa biến không hợp lệ."""
    setup_test_files(tmp_path, 2)
    with pytest.raises(ValueError, match="biến không hợp lệ"):
        renamer.rename_files(tmp_path, "{n:03d}_{name}_{invalid}")


def test_file_without_number(tmp_path):
    """Test file không có số."""
    (tmp_path / "no_number.txt").touch()
    (tmp_path / "file_001.txt").touch()
    results = renamer.rename_files(tmp_path, "{n:03d}_{name}")
    assert (tmp_path / "001_no_number.txt").exists()
    assert (tmp_path / "002_file_1.txt").exists()


def test_duplicate_name_error(tmp_path):
    """Test lỗi khi tên mới trùng file hiện có."""
    setup_test_files(tmp_path, 3)
    # Tạo file có tên giống sẽ sinh ra
    (tmp_path / "001_file_1.txt").touch()
    with pytest.raises(FileExistsError, match="trùng"):
        renamer.rename_files(tmp_path, "{n:03d}_{name}")


def test_only_files_not_recursive(tmp_path):
    """Test chỉ đổi tên file, không đệ quy."""
    setup_test_files(tmp_path, 2)
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file_001.txt").touch()
    results = renamer.rename_files(tmp_path, "{n:03d}_{name}")
    # Chỉ file trong thư mục gốc được đổi tên
    assert (tmp_path / "001_file_1.txt").exists()
    assert not (subdir / "001_file_1.txt").exists()


if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
