import os
from datetime import datetime


class MediaFixer:
    def __init__(self, media_path: str, image_format: str, video_format: str) -> None:
        self.media_path = media_path
        self.image_format = image_format
        self.video_format = video_format
        self.image_extensions = (".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi")
        self.video_extensions = (".mp4", ".m4a", ".m4p", ".m4b", ".m4r", ".m4v")


    def get_image_creation_time(self, file_path: str) -> tuple[datetime, bool]:
        """Get the creation time and HDR status of a image file from its metadata."""


    def get_video_creation_time(self, file_path: str) -> datetime:
        """Get the creation time of a video file from its metadata."""


    def format_image_filename(self, creation_time: datetime, file_extension: str, is_hdr: bool = False) -> str:
        """Format the image filename based on the creation time and HDR status."""
        hdr_suffix = "_HDR" if is_hdr else ""
        return self.image_format.format(
            Y=creation_time.year,
            M=creation_time.month,
            D=creation_time.day,
            h=creation_time.hour,
            m=creation_time.minute,
            s=creation_time.second,
            hdr=hdr_suffix,
            ext=file_extension
        )
    

    def format_video_filename(self, creation_time: datetime, file_extension: str) -> str:
        """Format the video filename based on the creation time."""
        return self.video_format.format(
            Y=creation_time.year,
            M=creation_time.month,
            D=creation_time.day,
            h=creation_time.hour,
            m=creation_time.minute,
            s=creation_time.second,
            ext=file_extension
        )
    

    def rename_file(self, file_path: str, new_name: str) -> None:
        """Rename the file to the new name."""
        new_name = os.path.join(os.path.dirname(file_path), new_name)
        try:
            os.rename(file_path, new_name)
        except Exception as e:
            print(f"Error renaming file {file_path} to {new_name}: {e}")


    def process_media_files(self) -> None:
        """Process the media files."""
        for root, _, files in os.walk(self.media_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Process image file
                if file.lower().endswith(self.image_extensions):
                    creation_time, is_hdr = self.get_image_creation_time(file_path)
                    file_extension = os.path.splitext(file)[1].lower()
                    if creation_time and is_hdr is not None and file_extension:
                        new_name = self.format_image_filename(creation_time, file_extension, is_hdr)
                        self.rename_file(file_path, new_name)

                # Process video file
                elif file.lower().endswith(self.video_extensions):
                    creation_time = self.get_video_creation_time(file_path)
                    file_extension = os.path.splitext(file)[1].lower()
                    if creation_time and file_extension:
                        new_name = self.format_video_filename(creation_time, file_extension)
                        self.rename_file(file_path, new_name)


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def main() -> None:
    clear_screen()

    print("\n\033[1;36mWelcome to the Recovered Media Fixer!\033[0m")
    print("Currently supported formats are: JPEG, MP4")

    media_path = input("\nPlease enter the path to the media files: ").strip()

    if not os.path.exists(media_path):
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
    "\t{hdr} - Adds \"_HDR\" if the photo is HDR, otherwise nothing\n" +
    "\t{ext} - The original file extension\n" +
    "Example: IMG_{Y}{M}{D}_{h}{m}{s}{hdr}{ext} → IMG_20250816_224044_HDR.jpg\n")

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