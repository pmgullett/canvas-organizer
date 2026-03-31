#!/usr/bin/env python3
"""
Canvas LMS File Organizer

Organizes student submission files from Canvas LMS into clean student-named
directories and simplifies the filenames by removing Canvas metadata and IDs.
"""

from pathlib import Path
import fnmatch
import shutil
import argparse
import sys
import os
from typing import Optional
from collections.abc import Iterable


def is_visible_file(path: Path) -> bool:
    """Return True only for regular, non-hidden, non-system files."""
    if not path.is_file():
        return False

    name = path.name
    if name in {
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        ".Spotlight-V100",
        ".Trashes",
        "__MACOSX",
    }:
        return False
    if name.startswith(".") and name not in {".", ".."}:
        return False
    return True


def get_student_directory_name(filename: str) -> Optional[str]:
    """Extract the student name to use as a directory name."""
    if not filename or "_" not in filename:
        return None

    parts = filename.split("_")
    dir_parts = []

    for part in parts:
        if not part:
            continue
        if part[0].isdigit():
            break
        if any(c.isalpha() for c in part) and any(c.isdigit() for c in part):
            for i, char in enumerate(part):
                if char.isdigit():
                    clean_part = part[:i].strip("_")
                    if clean_part:
                        dir_parts.append(clean_part)
                    break
            else:
                dir_parts.append(part)
            break

        if part.lower() in {
            "question",
            "final",
            "submission",
            "attempt",
            "version",
            "graded",
        }:
            break

        dir_parts.append(part)

    dir_name = "_".join(dir_parts).strip("_")
    return dir_name if dir_name else None


def get_clean_filename(original_name: str) -> str:
    """
    Clean the filename by removing student prefix and Canvas numeric IDs.
    Preserves the student's actual submitted filename as much as possible.
    """
    if "_" not in original_name:
        return original_name

    name_part, ext = os.path.splitext(original_name)

    # Normalize characters and whitespace
    name_part = name_part.replace(";", " - ")
    name_part = " ".join(name_part.split())

    parts = name_part.split("_")
    i = 0
    n = len(parts)

    # Skip student name parts (anything containing letters)
    while i < n and any(c.isalpha() for c in parts[i]):
        i += 1

    # Skip long numeric Canvas IDs
    while i < n and parts[i].isdigit() and len(parts[i]) >= 5:
        i += 1

    remaining = parts[i:]

    if not remaining:
        return f"final{ext}" if "final" in name_part.lower() else original_name

    new_name = "_".join(remaining)
    return f"{new_name}{ext}"


def organize_files(
    base_dir: str = ".",
    ignore_patterns: Iterable[str] = (),
    dry_run: bool = False,
    verbose: bool = True,
) -> None:
    ignore_patterns = ignore_patterns or []
    """Main function to organize Canvas LMS files."""

    base_path = Path(base_dir).resolve()

    if not base_path.exists():
        print(f"Error: Directory does not exist: {base_path}", file=sys.stderr)
        sys.exit(1)

    # Collect visible files only
    files = [
        f
        for f in base_path.iterdir()
        if is_visible_file(f)
        and not any(fnmatch.fnmatch(f.name, pat) for pat in ignore_patterns)
    ]

    if not files:
        print("No files to organize.")
        return

    created_dirs: set[str] = set()

    for f in files:
        dir_name = get_student_directory_name(f.name)
        if not dir_name:
            if verbose:
                print(f"Skipped {f.name} (could not determine student directory)")
            continue

        if dir_name.startswith(".") or not dir_name or dir_name.isspace():
            if verbose:
                print(f"Skipped suspicious directory name: {dir_name}")
            continue

        target_dir = base_path / dir_name

        if dir_name not in created_dirs:
            if dry_run:
                print(f"[DRY RUN] Would create directory: {target_dir}")
            else:
                target_dir.mkdir(exist_ok=True)
                if verbose:
                    print(f"Directory ready: {target_dir}")
            created_dirs.add(dir_name)

        new_name = get_clean_filename(f.name)
        destination = target_dir / new_name

        if destination.exists():
            print(f"Skipped {f.name} → {destination} (file already exists)")
            continue

        if dry_run:
            print(f"[DRY RUN] Would move {f.name} → {destination}")
        else:
            try:
                shutil.move(str(f), str(destination))
                if verbose:
                    print(f"Moved {f.name} → {destination}")
            except Exception as e:
                print(f"Error moving {f.name}: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Canvas LMS File Organizer - Clean up student submissions",
        epilog="No files are ignored by default. Use --ignore to skip specific patterns.",
    )
    parser.add_argument(
        "base_dir",
        nargs="?",
        default=".",
        help="Directory containing the downloaded Canvas files (default: current directory)",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        help="File patterns to ignore (e.g. *.zip *.py)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without actually moving files",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )

    args = parser.parse_args()

    organize_files(
        base_dir=args.base_dir,
        ignore_patterns=args.ignore,
        dry_run=args.dry_run,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
