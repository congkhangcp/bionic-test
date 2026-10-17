#!/usr/bin/env python3
"""
Công cụ dòng lệnh đổi tên file trong thư mục.
Sử dụng: python renamer.py <thư_muc> --pattern "<mẫu>" [--dry-run]
Ví dụ: python renamer.py ./images --pattern "{n:03d}_{name}"
"""

import os
import re
import argparse
from pathlib import Path


def parse_pattern(pattern: str) -> tuple[re.Pattern, str]:
    """
    Parse the rename pattern and return a regex pattern and replacement string.
    
    Args:
        pattern: Pattern string like "{n:03d}_{name}" or "{year}_{month}"
    
    Returns:
        Tuple of (compiled regex pattern, replacement string)
    """
    # Convert pattern to regex
    regex_pattern = pattern.replace("{n}", r"(?P<n>\d+)").replace("{name}", r"(?P<name>[^_]+)")
    regex_pattern = regex_pattern.replace("{year}", r"(?P<year>\d{4})")
    regex_pattern = regex_pattern.replace("{month}", r"(?P<month>\d+)")
    regex_pattern = regex_pattern.replace("{day}", r"(?P<day>\d+)")
    regex_pattern = regex_pattern.replace("{ext}", r"(?P<ext>\.\w+)")
    regex_pattern = regex_pattern.replace("{original}", r"(?P<original>.*)")
    
    # Handle multiple capture groups
    regex_pattern = regex_pattern.replace("{n}", r"(?P<n>\d+)").replace("{name}", r"(?P<name>[^_]+)")
    
    try:
        compiled_pattern = re.compile(regex_pattern)
        return compiled_pattern, pattern
    except re.error as e:
        raise ValueError(f"Lỗi với mẫu '{pattern}': {e}")


def get_file_number(filepath: Path, extension: str) -> int:
    """
    Extract the number prefix from a file path.
    
    Args:
        filepath: Path to the file
        extension: File extension (with dot)
    
    Returns:
        Integer number or 0 if no number found
    """
    stem = filepath.stem
    # Try to extract number from start of filename
    match = re.match(r"(\d+)", stem)
    if match:
        return int(match.group(1))
    return 0


def rename_files(directory: Path, pattern: str, dry_run: bool = False) -> list[dict]:
    """
    Rename files in the directory according to the pattern.
    
    Args:
        directory: Directory path
        pattern: Rename pattern like "{n:03d}_{name}"
        dry_run: If True, only print what would be done without making changes
    
    Returns:
        List of dictionaries with rename information
    """
    results = []
    
    if not directory.exists():
        raise FileNotFoundError(f"Thư mục không tồn tại: {directory}")
    
    if not directory.is_dir():
        raise NotADirectoryError(f"Không phải là thư mục: {directory}")
    
    # Get all files in the directory (not recursive by default)
    files = list(directory.iterdir())
    files = [f for f in files if f.is_file()]
    
    # Sort files by their number prefix
    def sort_key(f):
        return get_file_number(f, f.suffix)
    
    files.sort(key=sort_key)
    
    for filepath in files:
        extension = filepath.suffix
        stem = filepath.stem
        
        # Try to match the pattern
        try:
            compiled_pattern, replacement = parse_pattern(pattern)
        except ValueError as e:
            print(f"Lỗi: {e}")
            continue
        
        # Check if pattern matches
        match = compiled_pattern.match(stem)
        if not match:
            print(f"Không khớp mẫu cho file: {filepath.name}")
            continue
        
        # Extract groups
        groups = match.groupdict()
        
        # Generate new name
        new_name = replacement.format(**groups)
        
        # Handle duplicate names
        new_path = directory / new_name
        counter = 1
        original_new_name = new_name
        
        while new_path.exists():
            if new_name.count("_") > 0:
                # Try to add number before extension
                parts = new_name.rsplit(".", 1)
                if len(parts) == 2:
                    new_name = f"{parts[0]}_{counter}{parts[1]}"
                else:
                    new_name = f"{new_name}_{counter}"
            else:
                new_name = f"{new_name}_{counter}"
            
            new_path = directory / new_name
            counter += 1
        
        old_path_str = str(filepath)
        new_path_str = str(new_path)
        
        if dry_run:
            print(f"[DRY RUN] {filepath.name} -> {new_path.name}")
            results.append({
                "old": old_path_str,
                "new": new_path_str,
                "action": "dry_run"
            })
        else:
            try:
                filepath.rename(new_path)
                print(f"{filepath.name} -> {new_path.name}")
                results.append({
                    "old": old_path_str,
                    "new": new_path_str,
                    "action": "renamed"
                })
            except Exception as e:
                print(f"Lỗi khi đổi tên {filepath.name}: {e}")
                results.append({
                    "old": old_path_str,
                    "new": new_path_str,
                    "action": "failed",
                    "error": str(e)
                })
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Công cụ đổi tên file theo mẫu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python renamer.py ./images --pattern "{n:03d}_{name}"
  python renamer.py ./docs --pattern "{year}_{month}_{day}" --dry-run
        """
    )
    
    parser.add_argument(
        "directory",
        type=Path,
        help="Thư mục chứa các file cần đổi tên"
    )
    
    parser.add_argument(
        "--pattern",
        required=True,
        type=str,
        help="Mẫu đổi tên. Các biến có thể dùng: "
             "{n} (số), {name} (tên), {year}, {month}, {day}, {ext}"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ in kết quả mà không đổi tên thật"
    )
    
    args = parser.parse_args()
    
    try:
        results = rename_files(args.directory, args.pattern, args.dry_run)
        
        if dry_run:
            print(f"\n[Tổng cộng] {len(results)} file sẽ được đổi tên")
        else:
            successful = len([r for r in results if r["action"] == "renamed"])
            failed = len([r for r in results if r["action"] == "failed"])
            print(f"\n[Tổng cộng] {successful} file đã đổi tên, {failed} file lỗi")
            
    except FileNotFoundError as e:
        print(f"Lỗi: {e}")
        return 1
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
