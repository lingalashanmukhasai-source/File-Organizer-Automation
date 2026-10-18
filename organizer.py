
import os
import shutil
import logging
import argparse

from pathlib import Path
from datetime import datetime


# ==========================================================
# FILE ORGANIZER AUTOMATION
# ==========================================================

APP_NAME = "File Organizer Automation"
APP_VERSION = "1.0.0"

# Directory containing this Python script
BASE_DIR = Path(__file__).resolve().parent

# Log directory and file
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "organizer.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


# ==========================================================
# FILE CATEGORY MAPPING
# ==========================================================

CATEGORIES = {
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf",
        ".odt", ".xls", ".xlsx", ".csv", ".ppt",
        ".pptx", ".odp"
    },

    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".svg", ".webp", ".tiff", ".ico", ".heic"
    },

    "Videos": {
        ".mp4", ".mkv", ".avi", ".mov", ".wmv",
        ".flv", ".webm", ".mpeg", ".mpg", ".m4v"
    },

    "Audio": {
        ".mp3", ".wav", ".aac", ".flac",
        ".ogg", ".m4a", ".wma"
    },

    "Archives": {
        ".zip", ".rar", ".7z", ".tar",
        ".gz", ".bz2", ".xz"
    },

    "Code": {
        ".py", ".java", ".c", ".cpp", ".h",
        ".html", ".css", ".js", ".ts", ".jsx",
        ".tsx", ".php", ".sql", ".json", ".xml",
        ".yaml", ".yml", ".sh", ".bat", ".ipynb"
    },

    "Executables": {
        ".exe", ".msi", ".apk", ".deb", ".rpm"
    }
}

DEFAULT_CATEGORY = "Other"


# ==========================================================
# STATISTICS
# ==========================================================

def create_summary():
    """Initialize execution statistics."""

    return {
        "scanned": 0,
        "moved": 0,
        "previewed": 0,
        "skipped": 0,
        "failed": 0,
        "categories": {},
    }


# ==========================================================
# CATEGORY DETECTION
# ==========================================================

def get_category(file_path):
    """Identify the appropriate category using file extension."""

    extension = file_path.suffix.lower()

    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category

    return DEFAULT_CATEGORY


# ==========================================================
# SAFE DESTINATION SELECTION
# ==========================================================

def get_unique_destination(destination):
    """
    Return an unused destination path.

    Example:
        report.pdf
        report_1.pdf
        report_2.pdf
    """

    if not destination.exists():
        return destination

    parent = destination.parent
    stem = destination.stem
    suffix = destination.suffix

    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"

        if not candidate.exists():
            return candidate

        counter += 1


# ==========================================================
# FILE ORGANIZATION
# ==========================================================

def organize_directory(directory, dry_run=False):
    """
    Organize files directly inside a selected directory.

    Preview mode:
        Displays planned changes without moving files.

    Live mode:
        Creates category folders and moves files.
    """

    target = Path(directory).expanduser().resolve()

    if not target.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {target}"
        )

    if not target.is_dir():
        raise NotADirectoryError(
            f"Specified path is not a directory: {target}"
        )

    if target == LOG_DIR.resolve():
        raise ValueError(
            "The application's log directory cannot be the target."
        )

    summary = create_summary()

    print("\n" + "=" * 60)
    print(f"       {APP_NAME} v{APP_VERSION}")
    print("=" * 60)

    print(f"Target directory : {target}")
    print(f"Execution mode   : {'PREVIEW' if dry_run else 'LIVE'}")

    print("-" * 60)

    try:
        with os.scandir(target) as entries:

            for entry in entries:

                # Ignore directories and symbolic links.
                try:
                    if entry.is_symlink():
                        summary["skipped"] += 1
                        continue

                    if not entry.is_file(follow_symlinks=False):
                        summary["skipped"] += 1
                        continue

                    source = Path(entry.path)

                    # Do not organize the log file if it is inside
                    # the target directory.
                    if source.resolve() == LOG_FILE.resolve():
                        summary["skipped"] += 1
                        continue

                    summary["scanned"] += 1

                    category = get_category(source)

                    category_dir = target / category

                    destination = get_unique_destination(
                        category_dir / source.name
                    )

                    # ------------------------------------------
                    # PREVIEW MODE
                    # ------------------------------------------

                    if dry_run:

                        print(
                            f"[PREVIEW] {source.name} "
                            f"-> {category}/{destination.name}"
                        )

                        summary["previewed"] += 1

                        summary["categories"][category] = (
                            summary["categories"].get(category, 0) + 1
                        )

                        continue

                    # ------------------------------------------
                    # CREATE CATEGORY DIRECTORY
                    # ------------------------------------------

                    category_dir.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    # ------------------------------------------
                    # MOVE FILE SAFELY
                    # ------------------------------------------

                    # Reserve an unused destination name using
                    # exclusive file creation. This reduces the
                    # chance of choosing an existing filename.
                    while True:

                        destination = get_unique_destination(
                            category_dir / source.name
                        )

                        try:
                            descriptor = os.open(
                                str(destination),
                                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                                0o600
                            )

                            os.close(descriptor)
                            break

                        except FileExistsError:
                            continue

                    try:
                        # Remove our empty reservation before moving.
                        # See the note after the code regarding
                        # concurrency and atomic no-overwrite moves.
                        destination.unlink()

                        shutil.move(
                            str(source),
                            str(destination)
                        )

                    except Exception:
                        # Clean up an empty reservation if one remains.
                        try:
                            if (
                                destination.exists()
                                and destination.is_file()
                                and destination.stat().st_size == 0
                            ):
                                destination.unlink()
                        except OSError:
                            pass

                        raise

                    print(
                        f"[MOVED] {source.name} "
                        f"-> {category}/{destination.name}"
                    )

                    summary["moved"] += 1

                    summary["categories"][category] = (
                        summary["categories"].get(category, 0) + 1
                    )

                    logging.info(
                        "Moved file: %s -> %s",
                        source,
                        destination
                    )

                except PermissionError as error:

                    summary["failed"] += 1

                    print(
                        f"[PERMISSION DENIED] "
                        f"{entry.name}: {error}"
                    )

                    logging.error(
                        "Permission denied for %s: %s",
                        entry.path,
                        error
                    )

                except (OSError, shutil.Error) as error:

                    summary["failed"] += 1

                    print(
                        f"[ERROR] {entry.name}: {error}"
                    )

                    logging.exception(
                        "Failed to process file: %s",
                        entry.path
                    )

    except PermissionError as error:

        summary["failed"] += 1

        print(f"[ERROR] Cannot access directory: {error}")

        logging.error(
            "Cannot access directory %s: %s",
            target,
            error
        )

    # Print the final report.
    print_summary(summary, dry_run)

    return summary


# ==========================================================
# EXECUTION SUMMARY
# ==========================================================

def print_summary(summary, dry_run=False):
    """Display the final execution report."""

    print("\n" + "=" * 60)
    print("                 EXECUTION SUMMARY")
    print("=" * 60)

    print(f"Files scanned     : {summary['scanned']}")
    print(f"Files relocated   : {summary['moved']}")
    print(f"Files previewed   : {summary['previewed']}")
    print(f"Files skipped     : {summary['skipped']}")
    print(f"Files failed      : {summary['failed']}")

    if summary["categories"]:

        print("\nCategory breakdown:")

        for category, count in sorted(
            summary["categories"].items()
        ):

            print(f"  {category:<15}: {count}")

    if dry_run:
        print("\nPreview complete. No files were moved.")

    print(f"\nLog file: {LOG_FILE}")

    print("=" * 60)

    logging.info(
        "Run completed | scanned=%s | moved=%s | "
        "previewed=%s | skipped=%s | failed=%s",
        summary["scanned"],
        summary["moved"],
        summary["previewed"],
        summary["skipped"],
        summary["failed"]
    )


# ==========================================================
# COMMAND-LINE INTERFACE
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Automatically organize files into category folders."
        )
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=str(Path.home() / "Downloads"),
        help=(
            "Directory to organize. Defaults to the user's "
            "Downloads directory."
        )
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview planned file movements without moving files."
    )

    args = parser.parse_args()

    try:

        organize_directory(
            args.directory,
            dry_run=args.dry_run
        )

    except (FileNotFoundError, NotADirectoryError, ValueError) as error:

        print(f"\n[ERROR] {error}")

        logging.error(
            "Organizer stopped: %s",
            error
        )

    except OSError as error:

        print(f"\n[ERROR] Unable to organize directory: {error}")

        logging.exception(
            "Unexpected operating-system error"
        )


# ==========================================================
# APPLICATION ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()

