import sys,os
import struct
from datetime import datetime
from pathlib import Path
import gzip


def parse_index(cache_path):
	index_path = Path(cache_path).joinpath('index')
	index_file = IndexFile()
	index_file.parse_index_file(index_path)
	return index_file

def parse_entries(cache_path):
	entries_folder = Path(cache_path).joinpath('entries')
	entries_map = {}
	for file in entries_folder.iterdir():
		if not file.is_dir():
			entry_file = EntryFile()
			entry_file.parse_entry_file(file)
			entries_map[file.name] = entry_file
	return entries_map

def main(argv):
	cache_path = argv[1]
	index_file = parse_index(cache_path)
	entries = parse_entries(cache_path)

if __name__ == '__main__':
	main(sys.argv)