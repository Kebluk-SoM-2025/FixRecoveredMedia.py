"""
FixRecoveredMedia - A tool to rename recovered media files based on their metadata timestamps.

This module provides functionality to extract creation times from various media file formats
and rename them accordingly with proper error handling and performance optimizations.
"""

# Python standard libraries
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Set, Tuple, Callable, Union, TypeVar

# External libraries
import exifread
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

T = TypeVar('T')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('media_fixer.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class MediaType(Enum):
    IMAGE = 1
    VIDEO = 2


@dataclass(frozen=True)
class FormatData:
    """Data structure containing format-specific information."""
    extensions: Tuple[str, ...]
    type: MediaType
    
    def __post_init__(self):
        # Ensure all extensions are lowercase
        object.__setattr__(self, 'extensions', tuple(ext.lower() for ext in self.extensions))


class FileFormat(Enum):
    """Enumeration of supported file formats with their metadata."""
    # Image formats
    JPEG = FormatData(
        extensions=(".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi"),
        type=MediaType.IMAGE
    )
    
    HEIF = FormatData(
        extensions=(".heic", ".heif", ".hif"),
        type=MediaType.IMAGE
    )
    
    RAW = FormatData(
        extensions=(".arw", ".cr2", ".cr3", ".nef", ".nrw", ".orf", ".rw2", 
                   ".dng", ".raf", ".pef", ".x3f", ".raw", ".rwl", ".iiq"),
        type=MediaType.IMAGE
    )
    
    PNG = FormatData(
        extensions=(".png",),
        type=MediaType.IMAGE
    )
    
    TIFF = FormatData(
        extensions=(".tiff", ".tif"),
        type=MediaType.IMAGE
    )
    
    # Video formats
    MP4 = FormatData(
        extensions=(".mp4", ".m4a", ".m4p", ".m4b", ".m4r", ".m4v"),
        type=MediaType.VIDEO
    )
    
    MOV = FormatData(
        extensions=(".mov", ".movie", ".qt"),
        type=MediaType.VIDEO
    )
    
    AVI = FormatData(
        extensions=(".avi",),
        type=MediaType.VIDEO
    )
    
    MKV = FormatData(
        extensions=(".mkv",),
        type=MediaType.VIDEO
    )


    @classmethod
    def from_path(self, path: Path) -> Optional["FileFormat"]:
        """Determine file format from file extension."""
        ext = path.suffix.lower()
        for fmt in self:
            if ext in fmt.value.extensions:
                return fmt
        return None
    
    @classmethod
    def get_supported_extensions(self) -> Set[str]:
        """Get all supported file extensions."""
        extensions = set()
        for fmt in self:
            extensions.update(fmt.value.extensions)
        return extensions


@dataclass
class ProcessingStats:
    """Statistics for file processing operations."""
    total_files: int = 0
    processed_files: int = 0
    successful_renames: int = 0
    failed_files: List[Path] = field(default_factory=list)
    skipped_files: List[Path] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_renames / self.total_files) * 100 
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate processing duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class MetadataExtractor:
    """Handles extraction of creation timestamps from various media file formats."""
    
    # Common date/time formats found in metadata
    DATETIME_FORMATS = [
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S.%f"
    ]
    
    @staticmethod
    def _parse_datetime(date_str: str) -> Optional[datetime]:
        """Parse datetime string using various formats."""
        if not date_str:
            return None
            
        # Clean up the date string
        date_str = date_str.strip()
        
        # Try ISO format first
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Try common formats
        for fmt in MetadataExtractor.DATETIME_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Unable to parse datetime: {date_str}")
        return None
    
    @staticmethod
    def extract_from_exif(file_path: Path) -> Optional[datetime]:
        """Extract creation time from EXIF data."""
        try:
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal')
                
                # Prioritize DateTimeOriginal, then DateTime
                for tag_name in ['EXIF DateTimeOriginal', 'EXIF DateTime', 'Image DateTime']:
                    if tag_name in tags:
                        date_str = str(tags[tag_name])
                        creation_time = MetadataExtractor._parse_datetime(date_str)
                        if creation_time:
                            logger.debug(f"Extracted EXIF timestamp: {creation_time} from {file_path}")
                            return creation_time
                
                logger.warning(f"No usable EXIF timestamp found in {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading EXIF from {file_path}: {e}")
            return None
    
    @staticmethod
    def extract_from_hachoir(file_path: Path) -> Optional[datetime]:
        """Extract creation time using Hachoir library."""
        try:
            parser = createParser(str(file_path))
            if not parser:
                logger.warning(f"Could not create parser for {file_path}")
                return None

            with parser:
                metadata = extractMetadata(parser)
                if not metadata:
                    logger.warning(f"Could not extract metadata from {file_path}")
                    return None
                
                # Look for creation date in metadata
                creation_keywords = [
                    'creation', 'created', 'date_time_original', 'datetime_original',
                    'media_create_date', 'track_create_date', 'date_time', 'datetime'
                ]
                
                for line in metadata.exportPlaintext():
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in creation_keywords):
                        if ": " in line:
                            date_str = line.split(": ", 1)[1]
                            creation_time = MetadataExtractor._parse_datetime(date_str)
                            if creation_time:
                                logger.debug(f"Extracted Hachoir timestamp: {creation_time} from {file_path}")
                                return creation_time
                
                logger.warning(f"No creation date found in metadata for {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading metadata with Hachoir from {file_path}: {e}")
            return None
    
    @classmethod
    def extract_creation_time(self, file_path: Path, file_format: FileFormat) -> Optional[datetime]:
        """Extract creation time based on file format."""
        extraction_methods = []
        
        if file_format.value.type is MediaType.IMAGE:
            # For images, try EXIF first, then Hachoir
            extraction_methods = [self.extract_from_exif, self.extract_from_hachoir]
        else:
            # For videos, try Hachoir first
            extraction_methods = [self.extract_from_hachoir, self.extract_from_exif]
        
        for method in extraction_methods:
            try:
                result = method(file_path)
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Method {method.__name__} failed for {file_path}: {e}")
                continue
        
        logger.warning(f"Failed to extract creation time from {file_path}")
        return None


class Config:
    media_path: Path = None
    separate_formats: bool = True
    image_format: str = "IMG_{Y}{M}{D}_{h}{m}{s}{ext}"
    video_format: str = "VID_{Y}{M}{D}_{h}{m}{s}{ext}"
    unified_format: str = "MEDIA_{Y}{M}{D}_{h}{m}{s}{ext}"
    recursive: bool = True
    excluded_extensions: Set[str] = set()

DEFAULT_CONFIG = Config()


class FilenameFormatter:
    """Handles filename formatting based on templates and creation times."""
    
    def __init__(self, config: Config):
        if config.separate_formats:
            self.image_format = config.image_format
            self.video_format = config.video_format
        else:
            self.image_format = self.video_format = config.unified_format
    
    def format_filename(self, creation_time: datetime, file_format: FileFormat, 
                       original_extension: str) -> str:
        """Format filename based on creation time and file format."""
        format_string = self.image_format if file_format.value.type is MediaType.IMAGE else self.video_format
        
        return format_string.format(
            Y=str(creation_time.year).zfill(4),
            M=str(creation_time.month).zfill(2),
            D=str(creation_time.day).zfill(2),
            h=str(creation_time.hour).zfill(2),
            m=str(creation_time.minute).zfill(2),
            s=str(creation_time.second).zfill(2),
            ext=original_extension
        )


class FileManager:
    """Handles file operations like renaming with conflict resolution."""

    @staticmethod
    def safe_rename(source_path: Path, target_name: str) -> Tuple[bool, Optional[Path]]:
        """Safely rename file with automatic conflict resolution."""
        target_path = source_path.parent / target_name
        
        if not target_path.exists():
            try:
                source_path.rename(target_path)
                return True, target_path
            except Exception as e:
                logger.error(f"Error renaming {source_path} to {target_path}: {e}")
                return False, None
        
        # Handle naming conflicts
        stem = target_path.stem
        suffix = target_path.suffix

        for i in range(1, 9999 + 1): # 9999 inclusive
            candidate_path = source_path.parent / f"{stem}_{i}{suffix}"
            if not candidate_path.exists():
                try:
                    source_path.rename(candidate_path)
                    return True, candidate_path
                except Exception as e:
                    logger.error(f"Error renaming {source_path} to {candidate_path}: {e}")
                    return False, None

        logger.error(f"Could not find available name after 9998 attempts for {source_path}")
        return False, None


class MediaFixer:
    """Main class for processing and renaming media files based on metadata timestamps."""
    
    def __init__(self, config: Config):
        self.config = config
        self.formatter = FilenameFormatter(config)
        self.stats = ProcessingStats()
        
        if not self.config.media_path.exists():
            raise FileNotFoundError(f"Media path does not exist: {self.config.media_path}")
        
        if not self.config.media_path.is_dir():
            raise ValueError(f"Media path must be a directory: {self.config.media_path}")

    def _get_media_files(self) -> List[Path]:
        """Get all media files in the specified directory."""
        supported_extensions = FileFormat.get_supported_extensions()
        supported_extensions -= self.config.excluded_extensions

        if self.config.recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        files = []
        for file_path in self.config.media_path.glob(pattern):
            if (file_path.is_file() and file_path.suffix.lower() in supported_extensions):
                files.append(file_path)
        
        return files
    
    def _process_file(self, file_path: Path) -> Tuple[bool, str]:
        """Process a single media file and return success status and message."""
        try:
            # Determine file format
            file_format = FileFormat.from_path(file_path)
            if not file_format:
                return False, f"Unsupported file format: {file_path.suffix}"
            
            # Extract creation time
            creation_time = MetadataExtractor.extract_creation_time(file_path, file_format)
            if not creation_time:
                return False, "Could not extract creation time from metadata"
            
            # Generate new filename
            original_extension = file_path.suffix
            new_filename = self.formatter.format_filename(creation_time, file_format, original_extension)
            
            # Rename file
            success, new_path = FileManager.safe_rename(file_path, new_filename)
            if success:
                relative_old = file_path.relative_to(self.config.media_path)
                relative_new = new_path.relative_to(self.config.media_path)
                return True, f"Renamed '{relative_old}' to '{relative_new}'"
            else:
                return False, "Failed to rename file"
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False, str(e)
    
    
    def process_files(self) -> None:
        """Process all media files in the directory."""
        files = self._get_media_files()
        self.stats.total_files = len(files)
        self.stats.start_time = datetime.now()
        
        logger.info(f"Processing {len(files)} files...")
        
        for i, file_path in enumerate(files, 1):
            logger.info(f"Processing file {i}/{len(files)}: {file_path.name}")
            
            success, message = self._process_file(file_path)
            self.stats.processed_files += 1
            
            if success:
                self.stats.successful_renames += 1
                logger.info(f"✓ {message}")
            else:
                self.stats.failed_files.append(file_path)
                logger.warning(f"✗ Failed: {file_path.name} - {message}")
        
        self.stats.end_time = datetime.now()

    
    def print_summary(self) -> None:
        """Print processing summary with colored output."""
        print(f"\n{'='*60}")
        print(f"\033[1;36m{'PROCESSING SUMMARY':^60}\033[0m")
        print(f"{'='*60}")
        
        print(f"\033[34mTotal files found: {self.stats.total_files}\033[0m")
        print(f"\033[32mSuccessfully renamed: {self.stats.successful_renames}\033[0m")
        if self.stats.failed_files:
            print(f"\033[31mFailed to process: {len(self.stats.failed_files)}\033[0m")
        print(f"\033[33mSuccess rate: {self.stats.success_rate:.2f}%\033[0m")
        
        if self.stats.duration:
            print(f"\033[35mProcessing time: {self.stats.duration:.2f} seconds\033[0m")
        
        if self.stats.failed_files:
            print(f"\n\033[31mFailed files:\033[0m")
            for file_path in self.stats.failed_files:
                relative_path = file_path.relative_to(self.config.media_path)
                print(f"\033[31m  - {relative_path}\033[0m")
        
        print(f"{'='*60}")


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def validate_extensions(ext_str: str) -> Set[str]:
    """Validate string of extensions separated by a comma and return set of file extensions from comma-separated string."""
    if not ext_str.strip():
        return set()
    
    extensions = {ext.strip().lower() for ext in ext_str.split(",") if ext.strip()}
    supported_extensions = FileFormat.get_supported_extensions()
    
    for ext in extensions:
        if not ext.startswith('.') or ext not in supported_extensions:
            raise ValueError(f"Invalid extension format: {ext}. Must start with a dot (e.g., .jpg) and be supported.")
    
    return extensions


def validate_path(path_str: str) -> Path:
    """Validate and return Path object for given path string."""
    if not path_str.strip():
        raise ValueError("Path cannot be empty")
    
    # Remove quotes if present
    path_str = path_str.strip().removeprefix('"').removesuffix('"')
    path = Path(path_str)
    
    if not path.exists():
        raise FileNotFoundError(f"The specified path does not exist: {path}")
    
    if not path.is_dir():
        raise ValueError(f"The specified path is not a directory: {path}")
    
    return path


def get_user_choice(prompt: str, default: str = "") -> bool:
    """Get a yes/no user choice with optional default."""
    approved_choices = ['y', 'yes', 'true', '1']

    choice = get_user_input(prompt, default).lower()

    return choice in approved_choices


def get_user_input(prompt: str, default: str = "", validator: Optional[Callable[[str], T]] = None) -> Union[str, T]:
    """Get user input with optional default value and validation."""
    if default:
        default = "y" if default is True else "n" if default is False else default
        display_prompt = f"{prompt} [{default}]: "
    else:
        display_prompt = f"{prompt}: "
    
    while True:
        user_input = input(display_prompt).strip() or default
        
        if validator:
            try:
                user_input = validator(user_input)
                return user_input
            except (ValueError, FileNotFoundError) as e:
                print(f"\033[31mError: {e}\033[0m")
                continue
        
        return str(user_input)


def main() -> None:
    """Main function with error handling and user interface."""
    try:
        clear_screen()
        
        # Print header
        print("\033[1;36m" + "="*70 + "\033[0m")
        print("\033[1;36m" + "RECOVERED MEDIA FIXER".center(70) + "\033[0m")
        print("\033[1;36m" + "="*70 + "\033[0m")
        
        # Display supported formats
        supported_formats = ", ".join([fmt.name for fmt in FileFormat])
        print(f"\n\033[32mSupported formats:\033[0m {supported_formats}")

        # Load existing configuration
        config = Config()
        
        # Get media path
        config.media_path = get_user_input(
            "Enter the path to your media files",
            validator=validate_path
        )
                
        # Ask about separate formats
        config.separate_formats = get_user_choice(
            "\nUse different formats for images and videos? (y/n)",
            "y"
        )

        # Show available format placeholders
        print("\033[1;33mAvailable format placeholders:\033[0m")
        print("\033[33m  {Y}\033[0m - Creation year (4 digits, e.g., 2024)")
        print("\033[33m  {M}\033[0m - Creation month (2 digits, e.g., 03)")
        print("\033[33m  {D}\033[0m - Creation day (2 digits, e.g., 15)")
        print("\033[33m  {h}\033[0m - Creation hour (2 digits, 24-hour format)")
        print("\033[33m  {m}\033[0m - Creation minute (2 digits)")
        print("\033[33m  {s}\033[0m - Creation second (2 digits)")
        print("\033[33m  {ext}\033[0m - Original file extension with dot (e.g., .jpg)")
    
        print("\n\033[34mNote: All time values are zero-padded to ensure consistent formatting.\033[0m")
        print("\033[35mExample: IMG_{Y}{M}{D}_{h}{m}{s}{ext} → IMG_20250816_224044.jpg\033[0m")
        
        # Get filename formats
        if config.separate_formats:
            config.image_format = get_user_input(
                "Image filename format",
                DEFAULT_CONFIG.image_format
            )
            config.video_format = get_user_input(
                "Video filename format",
                DEFAULT_CONFIG.video_format
            )
        else:
            config.unified_format = get_user_input(
                "Unified filename format",
                DEFAULT_CONFIG.unified_format
            )

        # Ask about recursive processing
        config.recursive = get_user_choice(
            "\nProcess files in subdirectories recursively? (y/n)",
            DEFAULT_CONFIG.recursive
        )

        config.excluded_extensions = get_user_input(
            "\nEnter file extensions to exclude (comma-separated, e.g., .png,.tiff) or leave empty",
            validator=validate_extensions
        )

        # Create and run MediaFixer
        print("\n\033[1;33mSummary:\033[0m")
        print(f"\033[36mProcessing files in: {config.media_path}\033[0m")
        if config.separate_formats:
            print(f"\033[36mImage format: {config.image_format}\033[0m")
            print(f"\033[36mVideo format: {config.video_format}\033[0m")
        else:
            print(f"\033[36mUnified format: {config.unified_format}\033[0m")
        print(f"\033[36mRecursive processing: {'Enabled' if config.recursive else 'Disabled'}\033[0m")

        input("\nPress Enter to start processing...")

        media_fixer = MediaFixer(config)

        # Process files
        media_fixer.process_files()
        
        # Print summary
        media_fixer.print_summary()
        
    except KeyboardInterrupt:
        print("\n\033[31mProcess interrupted by user.\033[0m")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n\033[31mError: {e}\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")