# 📂 File Organizer Automation

A Python-based desktop automation utility that organizes
cluttered directories by automatically categorizing files
according to their extensions.

## 🚀 Features

- Automatic file categorization
- Dynamic folder creation
- Duplicate filename checks
- Permission and filesystem error handling
- Preview mode before moving files
- Execution summary and category statistics
- Logging of file operations
- No external dependencies required

## 📁 Supported Categories

| Category | Examples |
|----------|----------|
| Documents | PDF, DOCX, TXT, XLSX |
| Images | JPG, PNG, GIF, SVG |
| Videos | MP4, AVI, MKV |
| Audio | MP3, WAV, FLAC |
| Archives | ZIP, RAR, 7Z |
| Code | PY, JAVA, HTML, CSS, JS |
| Executables | EXE, MSI, APK |
| Other | Unrecognized file extensions |

## 🛠️ Technologies

- Python 3
- os
- shutil
- pathlib
- argparse
- logging

## ⚙️ Installation

Clone the repository:

    git clone https://github.com/YOUR_USERNAME/file-organizer-automation.git

Navigate into the project:

    cd file-organizer-automation

## ▶️ Usage

Preview file organization:

    python organizer.py "D:\MyFiles" --dry-run

Organize a directory:

    python organizer.py "D:\MyFiles"

Replace the example directory with your target directory.

## 📊 Execution Summary

The program reports:
- Total files scanned
- Files relocated
- Files previewed
- Files skipped
- Files that failed
- Category-wise file counts

## 📝 Logging

Operation logs are stored in the logs directory.

## 🔒 Safety

Test the program on a temporary directory before organizing
important files. Review the preview and retain backups.

The current filename collision handling is not a strict
atomic no-overwrite guarantee when concurrent processes
modify the destination directory.

## 🎯 Project Objective

To demonstrate Python file handling, desktop automation,
exception handling, logging, and command-line interfaces.

## 👨‍💻 Author

Shanmukha Sai