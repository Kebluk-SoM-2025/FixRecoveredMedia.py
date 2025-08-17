# FixRecoveredMedia.py

This Python script helps you organize recovered media files (currently JPEG and MP4) by reading their metadata and renaming them to structured filenames based on their original creation date and time. You can define your own filename format (e.g., IMG*{Y}{M}{D}*{h}{m}{s}.jpg), making your recovered files easy to sort and manage as if they had never been lost.

## Requirements

- Python 3.8 or higher
- `hachoir` package
- `exifread` package

## Installation

You can use FixRecoveredMedia in two ways:

### Option 1: Run as a Python Script

1. Install Python 3.8 or higher from [python.org](https://www.python.org/).
2. Install the required packages:
   ```powershell
   pip install hachoir exifread
   ```

### Option 2: Use the Windows Executable

1. Download the pre-built Windows executable (.exe) from the [Releases](https://github.com/Kebluk-SoM-2025/FixRecoveredMedia.py/releases) page.

## Usage

You can run FixRecoveredMedia using either method:

### If using the Python script:

```powershell
python FixRecoveredMedia.py
```

### If using the Windows executable:

Double-click the downloaded `.exe` file or run it from the command line.

---

The script will prompt you for:

- The path to your media files
- Whether you want separate filename formats for images and videos
- Your preferred filename format (with placeholders for year, month, day, hour, minute, second, and extension)

It will then process all JPEG and MP4 files in the specified folder, renaming them according to their metadata and your chosen format.

## License

FixRecoveredMedia.py is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE.txt) or
visit https://www.gnu.org/licenses/gpl-3.0.txt for details.

## Notes

- Only JPEG and MP4 formats are currently supported.
- The script does not modify file contents, only renames files based on metadata.
- If metadata is missing or unreadable, the file will not be renamed and will be listed in the summary.
- For best results, use the latest versions of `hachoir` and `exifread`.
