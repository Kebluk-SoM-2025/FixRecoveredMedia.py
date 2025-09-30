# 📸 FixRecoveredMedia

> **Organize your recovered media files effortlessly** 🚀

A powerful Python tool that intelligently renames recovered media files based on their metadata timestamps. Transform chaotic recovered files into an organized collection with proper chronological naming based on when photos and videos were actually taken.

## ✨ Key Features

🎯 **Smart Metadata Extraction** - Automatically extracts creation dates from EXIF data and multimedia metadata  
🎨 **Customizable Naming** - Define your own filename formats with flexible placeholder system  
🔄 **Batch Processing** - Process hundreds of files with comprehensive progress tracking  
📁 **Recursive Scanning** - Optionally scan subdirectories for complete organization  
⚡ **Conflict Resolution** - Automatically handles duplicate names with incremental numbering  
📊 **Detailed Reporting** - Get comprehensive statistics and logs of all operations  
🎨 **Colorful Interface** - User-friendly interface with color-coded feedback  
🛡️ **Safe Operations** - Non-destructive processing with comprehensive error handling

## 📋 Supported File Formats

### 🖼️ Image Formats

| Format        | Extensions                                                                                                     | Metadata Support  |
| ------------- | -------------------------------------------------------------------------------------------------------------- | ----------------- |
| **JPEG**      | `.jpg`, `.jpeg`, `.jpe`, `.jif`, `.jfif`, `.jfi`                                                               | ✅ EXIF + Hachoir |
| **HEIF/HEIC** | `.heic`, `.heif`, `.hif`                                                                                       | ✅ Hachoir        |
| **RAW**       | `.arw`, `.cr2`, `.cr3`, `.nef`, `.nrw`, `.orf`, `.rw2`, `.dng`, `.raf`, `.pef`, `.x3f`, `.raw`, `.rwl`, `.iiq` | ✅ EXIF + Hachoir |
| **PNG**       | `.png`                                                                                                         | ✅ Hachoir        |
| **TIFF**      | `.tiff`, `.tif`                                                                                                | ✅ EXIF + Hachoir |

### 🎥 Video Formats

| Format  | Extensions                                     | Metadata Support |
| ------- | ---------------------------------------------- | ---------------- |
| **MP4** | `.mp4`, `.m4a`, `.m4p`, `.m4b`, `.m4r`, `.m4v` | ✅ Hachoir       |
| **MOV** | `.mov`, `.movie`, `.qt`                        | ✅ Hachoir       |
| **AVI** | `.avi`                                         | ✅ Hachoir       |
| **MKV** | `.mkv`                                         | ✅ Hachoir       |

> **Note:** The tool uses dual extraction methods (EXIF for images, Hachoir for all formats) to maximize compatibility. JPEG photos and MP4 videos from smartphones are fully tested and work reliably.

## 🛠️ Installation & Requirements

### Prerequisites

- **Python 3.8+** - [Download from python.org](https://www.python.org/)
- **Required packages:**
  ```bash
  pip install hachoir exifread
  ```

### Installation Options

#### Option 1: 🐍 Python Script

1. Clone or download this repository
2. Install dependencies:
   ```powershell
   pip install hachoir exifread
   ```
3. Run the script:
   ```powershell
   python FixRecoveredMedia.py
   ```

#### Option 2: 💻 Windows Executable

1. Download the pre-built `.exe` from [Releases](https://github.com/Kebluk-SoM-2025/FixRecoveredMedia.py/releases)
2. Double-click to run or execute from command line
3. No Python installation required!

## 🚀 Usage Guide

### Quick Start

1. **Launch the application:**

   ```powershell
   python FixRecoveredMedia.py
   ```

2. **Follow the interactive prompts:**
   - 📂 Select your media directory
   - ⚙️ Configure processing options
   - 🎨 Set filename formats
   - ▶️ Start processing

### 🎨 Filename Format System

The tool uses a powerful placeholder system for creating custom filename patterns:

#### Available Placeholders

| Placeholder | Description                     | Example |
| ----------- | ------------------------------- | ------- |
| `{Y}`       | Year (4 digits)                 | `2024`  |
| `{M}`       | Month (2 digits, zero-padded)   | `03`    |
| `{D}`       | Day (2 digits, zero-padded)     | `15`    |
| `{h}`       | Hour (2 digits, 24-hour format) | `14`    |
| `{m}`       | Minute (2 digits, zero-padded)  | `30`    |
| `{s}`       | Second (2 digits, zero-padded)  | `22`    |
| `{ext}`     | Original file extension         | `.jpg`  |

#### Example Formats

```
IMG_{Y}{M}{D}_{h}{m}{s}{ext}     → IMG_20240315_143022.jpg
VID_{Y}{M}{D}_{h}{m}{s}{ext}     → VID_20240315_143022.mp4
Photo_{Y}-{M}-{D}_{h}-{m}{ext}   → Photo_2024-03-15_14-30.jpg
{Y}{M}{D}_{h}{m}{s}_{ext}        → 20240315_143022_.jpg
```

### ⚙️ Configuration Options

The tool offers flexible configuration through an interactive setup:

- **📂 Directory Selection** - Choose source folder for media files
- **🎯 Format Separation** - Use different naming for images vs videos
- **🔄 Recursive Processing** - Include subdirectories in scan
- **🚫 File Exclusions** - Skip specific file extensions
- **📝 Custom Formats** - Define your preferred naming patterns

### 📊 Processing Features

- **🎯 Intelligent Processing** - Optimized metadata extraction based on file type
- **⚡ Progress Tracking** - Real-time status updates during processing
- **🛡️ Safe Renaming** - Automatic conflict resolution with incremental naming
- **📋 Comprehensive Logs** - Detailed processing logs saved to `media_fixer.log`
- **📈 Success Statistics** - Complete summary with success rates and timing

## 📖 Advanced Usage

### Processing Statistics

After processing, you'll receive a detailed summary including:

- Total files processed
- Success/failure counts
- Processing duration
- Success rate percentage
- List of failed files (if any)

### Logging System

- **Log File:** `media_fixer.log`
- **Captures:** All operations, errors, and performance metrics
- **Format:** Timestamped entries with severity levels
- **Encoding:** UTF-8 for international filename support

### Conflict Resolution

When filename conflicts occur, the tool automatically:

1. Detects existing files with the same name
2. Appends incremental numbers (`_1`, `_2`, etc.)
3. Finds the first available filename
4. Supports up to 9999 incremental attempts

## 🔧 Troubleshooting

### Common Issues

#### ❌ "Could not extract creation time"

**Causes:**

- File lacks metadata/EXIF data
- Corrupted file
- Unsupported metadata format

**Solutions:**

- Verify file integrity
- Check if file was edited/processed by software that strips metadata

#### ❌ "Permission denied" errors

**Causes:**

- Insufficient file system permissions
- Files in use by other applications
- System-protected directories

**Solutions:**

- Run as administrator (Windows)
- Close applications using the files
- Check file/folder permissions

#### 🐌 Slow processing

**Causes:**

- Large files or many files
- Slow storage (HDD vs SSD)
- Antivirus scanning

**Solutions:**

- Process smaller batches
- Temporarily disable antivirus scanning
- Use faster storage if available

### Log Analysis

Check `media_fixer.log` for detailed error information:

```
2024-03-15 14:30:22 - INFO - Processing file 1/100: IMG_001.jpg
2024-03-15 14:30:22 - WARNING - No usable EXIF timestamp found in IMG_001.jpg
2024-03-15 14:30:22 - ERROR - Error reading EXIF from IMG_002.jpg: [Errno 13] Permission denied
```

## 🤝 Contributing

Currently, there isn't an active way to contribute code to this project, as this script isn't perfect and will be completely remade in the future. However, you can help by:

### 🐛 **Issue Reporting**

- Report bugs and unexpected behavior
- Suggest improvements and new features
- Share compatibility issues with specific file formats
- Document problems with metadata extraction

Feel free to open issues on GitHub if you encounter problems or have suggestions for the future rewrite!

## 📄 License

This project is licensed under the **GNU General Public License v3.0**.

📖 See [LICENSE.txt](LICENSE.txt) for full details  
🌐 Or visit [https://www.gnu.org/licenses/gpl-3.0.txt](https://www.gnu.org/licenses/gpl-3.0.txt)

## ⚠️ Important Notes

- 🔒 **Safe Processing** - Only renames files, never modifies content
- 📱 **Tested Formats** - JPEG photos and MP4 videos from smartphones work reliably
- 🧪 **Experimental Support** - Other formats work if they contain compatible metadata
- 📦 **Dependencies** - Keep `hachoir` and `exifread` updated for best results
- 🗂️ **File Organization** - Files without readable metadata will be skipped and reported
- 🚧 **Future Development** - This script isn't perfect and will be remade in the future in a compiled language like C, C++ or Rust once I learn any of them :) There will be more comprehensive **TESTED** support for all formats!

---

**Transform your recovered media chaos into organized perfection!** ✨
