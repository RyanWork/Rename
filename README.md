# Rename.py

## Description
A small script to read photo/video metadata to try and find a uniform naming scheme across all files.

## Requirements
- [FFmpeg](https://ffmpeg.org/): For video processing 
  - Update PATH variable to point to `ffmpeg/bin/`
- [PIL](https://pypi.org/project/Pillow/)
  - `pip install Pillow`
- [pillow-heif](https://pypi.org/project/pillow-heif/)
  - `pip install pillow-heif`
- [dateutil](https://pypi.org/project/python-dateutil/)
  - `pip install python-dateutil`

## Usage
```bash
usage: rename.py [-h] -d DIRECTORY [-v] [--dry-run]

Parse files for date metadata and rename files based off date values

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory to loop through
  -v, --verbose         Enable verbose logging
  --dry-run             Run without committing file renaming
```

## Process
1. If it is a valid `image_extensions`, attempt to read EXIF data off image
2. If it is a valid `video_extensions`, attempt to use ffmpeg data off video
3. If we could not fetch metadata from EXIF or ffmpeg, try to parse filename for date
    1. If we could get a valid date from the filename:
       1. Check if we got an entire timestamp (format YYYY-mm-dd HH:MM:SS) 
       2. If we could only get YYYY-mm-dd, append `_00i`, where `i` is an incremented integer
4. If we ended up finding a vaLid timestamp:
    1. Try to rename file
    2. If the file already exists, append ` (i)` to the filename 
    3. Repeat steps 1-4 until all files processed 
5. Log error, repeat steps 1-4 until all files processed