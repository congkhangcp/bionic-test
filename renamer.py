#!/usr/bin/env python3
"""
Công cụ đổi tên file: python renamer.py <thư_muc> --pattern "<mẫu>" [--dry-run]
Mẫu: {n:03d}_{name}.ext - {n} là số từ 1 theo thứ tự tên tăng dần, {name} là tên gốc không đuôi
"""

import argparse
from pathlib import Path


def parse_pattern(pattern: str) -> tuple[str, str]:
    """Kiểm tra và chuẩn bị mẫu đổi tên."""
    allowed_vars = {"n", "name", "year", "month", "day", "ext"}
    found_vars = {var for var in allowed_vars if f"{{{var}}}" in pattern}
    unknown_vars = found_vars - allowed_vars
    if unknown_vars:
        raise ValueError(f"Mẫu chứa biến không hợp lệ: {', '.join(sorted(unknown_vars))}")
    return pattern, pattern


def get_sort_key(filepath: Path) -> int:
    """Trả về số thứ tự của file (1, 2, 3...) hoặc 0 nếu không có số."""
    stem = filepath.stem
    match = stem.lstrip("0123456789")
    if not match:
        return 0
    try:
        return int(stem)
    except ValueError:
        return 0


def rename_files(directory: Path, pattern: str, dry_run: bool = False) -> bool:
    """Đổi tên các file trong thư mục."""
    if not directory.exists():
        raise FileNotFoundError(f"Thư mục không tồn tại: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Không phải thư mục: {directory}")

    files = list(directory.iterdir())
    files = [f for f in files if f.is_file()]

    # Sắp xếp theo số thứ tự tăng dần
    files.sort(key=get_sort_key)

    # Tạo danh sách tên mới
    new_names = {}
    for filepath in files:
        stem = filepath.stem
        suffix = filepath.suffix
        name_part = stem.lstrip("0123456789")
        number = get_sort_key(filepath)

        if number == 0:
            number = 1
        else:
            number += 1  # Bắt đầu từ 1 theo thứ tự

        new_name = pattern.replace("{n}", f"{number:03d}")
        new_name = new_name.replace("{name}", name_part)
        new_names[filepath] = new_name

    # Kiểm tra tên mới có trùng với file hiện có không
    for filepath, new_name in new_names.items():
        if new_name == filepath.name:
            continue
        new_path = directory / new_name
        if new_path.exists():
            raise FileExistsError(f"Tên mới '{new_name}' trùng với file hiện có")

    # Thực hiện đổi tên
    for filepath, new_name in new_names.items():
        if dry_run:
            print(f"[DRY RUN] {filepath.name} -> {new_name}")
        else:
            new_path = directory / new_name
            filepath.rename(new_path)
            print(f"{filepath.name} -> {new_name}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Đổi tên file theo mẫu")
    parser.add_argument("directory", type=Path, help="Thư mục chứa file")
    parser.add_argument("--pattern", required=True, help="Mẫu đổi tên: {n:03d}_{name}")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ in kết quả")

    args = parser.parse_args()
    try:
        rename_files(args.directory, args.pattern, args.dry_run)
    except (FileNotFoundError, NotADirectoryError, FileExistsError, ValueError) as e:
        print(f"Lỗi: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
