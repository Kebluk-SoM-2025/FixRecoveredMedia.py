from pathlib import Path
from datetime import datetime
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from typing import Optional
import exifread


class MediaFixer:
    def __init__(self, media_path: str, image_format: str, video_format: str) -> None:
        self.media_path = Path(media_path)
        self.image_format = image_format
        self.video_format = video_format
        self.image_extensions = {".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi"}
        self.video_extensions = {".mp4", ".m4a", ".m4p", ".m4b", ".m4r", ".m4v"}
        self.total = 0
        self.success = 0
        self.failures = []


    def get_image_creation_time(self, file_path: str) -> Optional[datetime]:
        """Get the creation time of a image file from its metadata."""
        try:
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f)
                if not tags:
                    print(f"\033[31mNo EXIF tags found in {file_path}.\033[0m")
                    return None
                
                creation_time = tags.get("EXIF DateTimeOriginal") or tags.get("EXIF DateTime")
                if not creation_time:
                    print(f"\033[31mNo creation time found in EXIF tags of {file_path}.\033[0m")
                    return None
                creation_time = datetime.strptime(str(creation_time), "%Y:%m:%d %H:%M:%S")
                
                return creation_time
        except Exception as e:
            print(f"\033[31mError reading image metadata from {file_path}: {e}\033[0m")
            return None


    def get_video_creation_time(self, file_path: str) -> Optional[datetime]:
        """Get the creation time of a video file from its metadata."""
        try:
            parser = createParser(file_path)
            if not parser:
                print(f"\033[31mCould not create parser for {file_path}.\033[0m")
                return None

            with parser:
                try:
                    metadata = extractMetadata(parser)
                except Exception as e:
                    print(f"\033[31mError extracting metadata from {file_path}: {e}\033[0m")

            if not metadata:
                print(f"\033[31mCould not extract metadata from {file_path}.\033[0m")
                return None

            creation_time = metadata.get("creation_date")
            if not creation_time:
                print(f"\033[31mCould not find creation time in metadata from {file_path}.\033[0m")
                return None
            parser.close()
            return creation_time
        except Exception as e:
            print(f"\033[31mError reading video metadata from {file_path}: {e}\033[0m")
            return None


    def format_filename(self, creation_time: datetime, file_extension: str, format_string: str) -> str:
        """Format the filename based on the creation time."""
        return format_string.format(
            Y=str(creation_time.year).zfill(2),
            M=str(creation_time.month).zfill(2),
            D=str(creation_time.day).zfill(2),
            h=str(creation_time.hour).zfill(2),
            m=str(creation_time.minute).zfill(2),
            s=str(creation_time.second).zfill(2),
            ext=file_extension
        )
    

    def rename_file(self, file_path: Path, new_name: str, n: int = 1) -> None:
        """Rename the file to the new name."""
        new_path = file_path.parent / new_name
        if new_path.exists():
            stem, ext = new_path.stem, new_path.suffix
            new_name = f"{stem}_{n}{ext}"
            self.rename_file(file_path, new_name, n + 1)
            return
        try:
            file_path.rename(new_path)
            print(f"\033[32mSuccessfully renamed '{file_path.relative_to(self.media_path)}' to '{new_path.relative_to(self.media_path)}'\033[0m")
            self.success += 1
        except Exception as e:
            print(f"\033[31mError renaming file {file_path.relative_to(self.media_path)} to {new_path.relative_to(self.media_path)}: {e}\033[0m")
            self.failures.append(file_path)


    def print_summary(self) -> None:
        """Print the end summary."""
        print(f"\n\033[34mTotal files processed: {self.total}\033[0m")
        print(f"\033[32mSuccessfully renamed files: {self.success}\033[0m")
        print(f"\033[32mSuccess rate: {self.success / self.total * 100:.2f} %\033[0m")
        print(f"\033[31mFailed renaming attempts: {len(self.failures)}\033[0m")
        if self.failures:
            print("\n\033[31mFailed Renaming Attempts:\033[0m")
            for path in self.failures:
                print(f"\033[31m - {path}\033[0m")


    def process_media_files(self) -> None:
        """Process the media files."""
        for file_path in self.media_path.rglob("*"):
            if not file_path.is_file():
                continue
            file_extension = file_path.suffix.lower()
            self.total += 1
            creation_time = None
            is_image = file_extension in self.image_extensions
            is_video = file_extension in self.video_extensions
            if is_image:
                creation_time = self.get_image_creation_time(str(file_path))
            elif is_video:
                creation_time = self.get_video_creation_time(str(file_path))
            else:
                print(f"\033[33mUnsupported file format: {file_path.name}\033[0m")
                continue
            if creation_time:
                new_name = self.format_filename(creation_time, file_extension, self.image_format if is_image else self.video_format)
                self.rename_file(file_path, new_name)
            else:
                self.failures.append(str(file_path))
        self.print_summary()


def clear_screen() -> None:
    import os
    os.system("cls" if os.name == "nt" else "clear")


def main() -> None:
    clear_screen()

    print("\033[1;36mWelcome to the Recovered Media Fixer!\033[0m")
    print("Currently supported formats are: JPEG, MP4")

    media_path = input("\nPlease enter the path to the media files: ").strip().removeprefix("\"").removesuffix("\"")

    if not Path(media_path).exists():
        raise FileNotFoundError(f"\n\033[31mThe specified path does not exist: {media_path}\033[0m")

    separated_formats = (input("Do you want to define separated filename formats for images and videos? (y/n) [y]: ").strip().lower() or "y") == "y"

    # Print possible format placeholders
    print("\nPossible format placeholders:\n" +
    "\t{Y} - Creation year of original file\n" +
    "\t{M} - Creation month of original file\n" +
    "\t{D} - Creation day of original file\n" +
    "\t{h} - Creation hour of original file\n" +
    "\t{m} - Creation minute of original file\n" +
    "\t{s} - Creation second of original file\n" +
    "\t{ext} - The original file extension with the dot\n" +
    "\033[34mNote: All time values are zero-padded to two digits.\033[0m\n" +
    "\033[35mExample: IMG_{Y}{M}{D}_{h}{m}{s}{ext} → IMG_20250816_224044.jpg\033[0m\n")

    if separated_formats:
        image_format = input("Image format: ").strip()
        video_format = input("Video format: ").strip()
    else:
        image_format = video_format = input("Image/Video format: ").strip()

    media_fixer = MediaFixer(media_path, image_format, video_format)

    media_fixer.process_media_files()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[31mProcess interrupted by user.\033[0m")
    except Exception as e:
        print(f"\n\033[31mError occurred: {e}\033[0m")
    input("\nPress Enter to exit...")