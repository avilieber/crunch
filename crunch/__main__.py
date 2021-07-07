import argparse

from .main import SONG_SHEET_NAME, main

__all__ = []


parser = argparse.ArgumentParser(description="Generate KPI Sheet")
parser.add_argument("date_directory", metavar="D", type=str, help="Name of Song Folder")
args = parser.parse_args()
exit(main(date_dir=args.date_directory, song_sheet_name=SONG_SHEET_NAME))
