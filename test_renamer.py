#!/usr/bin/env python3
"""
Test cases cho renamer.py sử dụng pytest.
"""

import os
import tempfile
import shutil
from pathlib import Path

# Import từ renamer.py
import renamer


def setup_test_directory():
    """Tạo thư mục test với các file mẫu."""
    test_dir = Path(tempfile.mkdtemp())
    
    # Tạo các file test với số thứ tự
    for i in range(1, 6):
        (test_dir / f"image_{i:03d}.jpg").touch()
    
    # Tạo file không có số
    (test_dir / "no_number.jpg").touch()
    
    return test_dir


def teardown_test_directory(test_dir):
    """Xóa thư mục test."""
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_rename_with_number_pattern():
    """Test đổi tên với mẫu có số."""
    test_dir = setup_test_directory()
    try:
        # Test rename pattern {n:03d}_{name}
        results = renamer.rename_files(test_dir, "{n:03d}_{name}")
        
        assert len(results) == 5
        assert all(r["action"] == "renamed" for r in results)
        
        # Kiểm tra kết quả
        expected_names = {
            "image_001.jpg": "image_001_image_001.jpg",
            "image_002.jpg": "image_002_image_002.jpg",
            "image_003.jpg": "image_003_image_003.jpg",
            "image_004.jpg": "image_004_image_004.jpg",
            "image_005.jpg": "image_005_image_005.jpg",
        }
        
        for result in results:
            expected_name = expected_names[os.path.basename(result["old"])]
            assert expected_name in result["new"], f"Expected {expected_name} in {result['new']}"
        
        print("✓ Test rename_with_number_pattern: PASSED")
    finally:
        teardown_test_directory(test_dir)


def test_dry_run_mode():
    """Test chế độ dry-run."""
    test_dir = setup_test_directory()
    try:
        results = renamer.rename_files(test_dir, "{n:03d}_{name}", dry_run=True)
        
        assert len(results) == 5
        assert all(r["action"] == "dry_run" for r in results)
        
        # Kiểm tra file vẫn còn nguyên
        assert (test_dir / "image_001.jpg").exists()
        assert (test_dir / "image_002.jpg").exists()
        
        print("✓ Test dry_run_mode: PASSED")
    finally:
        teardown_test_directory(test_dir)


def test_nonexistent_directory():
    """Test với thư mục không tồn tại."""
    try:
        test_dir = Path("/nonexistent/directory")
        results = renamer.rename_files(test_dir, "{n:03d}_{name}")
        
        assert False, "Nên raise FileNotFoundError"
    except FileNotFoundError:
        print("✓ Test nonexistent_directory: PASSED")


def test_invalid_pattern():
    """Test với mẫu không hợp lệ."""
    test_dir = setup_test_directory()
    try:
        try:
            results = renamer.rename_files(test_dir, "{invalid}pattern")
            assert False, "Nên raise ValueError"
        except ValueError as e:
            assert "Lỗi với mẫu" in str(e)
        
        print("✓ Test invalid_pattern: PASSED")
    finally:
        teardown_test_directory(test_dir)


def test_file_without_number():
    """Test file không có số."""
    test_dir = setup_test_directory()
    try:
        results = renamer.rename_files(test_dir, "{n:03d}_{name}")
        
        # File không có số nên không được đổi tên
        no_number_results = [r for r in results if "no_number" in r["old"]]
        assert len(no_number_results) == 1
        assert no_number_results[0]["action"] == "failed" or "Không khớp mẫu" in str(no_number_results[0])
        
        print("✓ Test file_without_number: PASSED")
    finally:
        teardown_test_directory(test_dir)


def test_duplicate_names_handling():
    """Test xử lý tên trùng lặp."""
    test_dir = setup_test_directory()
    try:
        # Tạo thêm file để gây ra tên trùng
        (test_dir / "image_001_backup.jpg").touch()
        
        results = renamer.rename_files(test_dir, "{n:03d}_{name}")
        
        # Tất cả file nên được đổi tên thành công
        successful = [r for r in results if r["action"] == "renamed"]
        assert len(successful) >= 5  # Ít nhất 5 file thành công
        
        print("✓ Test duplicate_names_handling: PASSED")
    finally:
        teardown_test_directory(test_dir)


def test_sort_order():
    """Test thứ tự sắp xếp file."""
    test_dir = setup_test_directory()
    try:
        # Kiểm tra thứ tự file sau khi sort
        files = list(test_dir.iterdir())
        files = [f for f in files if f.is_file()]
        
        def sort_key(f):
            return renamer.get_file_number(f, f.suffix)
        
        sorted_files = sorted(files, key=sort_key)
        
        assert sorted_files[0].name == "image_001.jpg"
        assert sorted_files[1].name == "image_002.jpg"
        assert sorted_files[4].name == "image_005.jpg"
        
        print("✓ Test sort_order: PASSED")
    finally:
        teardown_test_directory(test_dir)


def run_all_tests():
    """Chạy tất cả test cases."""
    print("=" * 60)
    print("Chạy các test cho renamer.py")
    print("=" * 60)
    
    tests = [
        test_rename_with_number_pattern,
        test_dry_run_mode,
        test_nonexistent_directory,
        test_invalid_pattern,
        test_file_without_number,
        test_duplicate_names_handling,
        test_sort_order,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: FAILED - {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Kết quả: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
