import argparse
import os
from PIL import Image
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
import ffmpeg
from dateutil.parser import parse
from os import listdir
from os.path import isfile, join
import re
import datetime


def get_image_metadata(full_file_path):
    pil_img = Image.open(full_file_path)
    exif_info = pil_img.getexif()
    if exif_info is None:
        return None

    exif = {TAGS.get(k, k): v for k, v in exif_info.items()}
    if "DateTime" in exif:
        dt_segments = exif["DateTime"].split()
        dt_segments[0] = dt_segments[0].replace(":", "-")
        return get_standard_time_format(" ".join(dt_segments))
    return None


def get_video_metadata(full_file_path):
    video_metadata = ffmpeg.probe(full_file_path)
    return get_standard_time_format(video_metadata["format"]["tags"]["creation_time"])


def get_date_from_filename(filename):
    m = re.search(".*([0-9]{8}).*WA.*|.*_([0-9]{8})_([0-9]{6}).*", filename)
    if m:
        groups = m.groups()
        if groups[0] is not None:
            # Whatsapp files
            file_date = groups[0]
            return get_standard_time_format(file_date), False
        elif groups[1] is not None and groups[2] is not None:
            # Instagram files
            file_date = "{0} {1}".format(groups[1], groups[2])
            return get_standard_time_format(file_date), True

    return None, False


def get_standard_time_format(date_string):
    parsed_date = parse(date_string)
    if parsed_date.year < 2000:
        # For funny cases where we can parse metadata, but this is clearly not a valid date
        return None

    return parsed_date.strftime("%Y-%m-%d %H-%M-%S")


def add_seconds(existing_date, secs):
    fulldate = existing_date + datetime.timedelta(seconds=secs)
    return fulldate.time()


if __name__ == "__main__":
    image_extensions = {".jpg", ".jpeg", ".heic", ".png"}
    video_extensions = {".mp4", ".mov"}

    parser = argparse.ArgumentParser(
        prog="rename.py",
        description="Parse files for date metadata and rename files based off date values")
    parser.add_argument("-d", "--directory", required=True, help="Directory to loop through")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--dry-run", action="store_true", help="Run without committing file renaming")
    args = parser.parse_args()

    if args.verbose:
        print("Parsing directory: {0}. . .".format(args.directory))

    register_heif_opener()
    occurrences = {}
    only_files = [f for f in listdir(args.directory) if not f.startswith('.') and isfile(join(args.directory, f))]
    for file in only_files:
        date = None
        full_file_path = join(args.directory, file)
        try:
            _, file_extension = os.path.splitext(file)
            if file_extension.lower() in image_extensions:
                date = get_image_metadata(full_file_path)
            elif file_extension.lower() in video_extensions:
                date = get_video_metadata(full_file_path)
        except KeyError:
            print("ERROR! Could not find metadata for {0}".format(file))
            continue

        if date is None:
            date, isValid = get_date_from_filename(file)
            if date is None:
                print("ERROR! Could not parse {0}".format(full_file_path))
                continue

            if not isValid:
                ymd = date.split()[0]
                dt = parse(ymd)
                if ymd in occurrences:
                    occurrences[ymd] += 1
                else:
                    occurrences[ymd] = 1
                date = "{0}_{1}".format(ymd, str(str(occurrences[ymd]).zfill(3)))

        if date is not None:
            rename = date + file_extension
            if args.verbose:
                print("File: {0} -- Date: {1}".format(file, date))

            if not args.dry_run:
                retrySuccess = False
                i = 1
                while not retrySuccess:
                    try:
                        os.rename(full_file_path, os.path.join(args.directory, rename))
                        retrySuccess = True
                    except FileExistsError:
                        rename = date + " ({0})".format(i) + file_extension
                        i += 1
