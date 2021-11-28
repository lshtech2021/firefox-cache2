import sys, os
from pathlib import Path

from index_file import IndexFile, IndexRecord
from entry_file import EntryFile


cache_path = 'cache2'


def test1():
	index_path = Path(cache_path).joinpath('index')
	index_file = IndexFile()
	index_file.parse_index_file(index_path)

def test2(entry_name):
	entry_path = Path(cache_path).joinpath('entries').joinpath(entry_name)
	entry_file = EntryFile()
	entry_file.parse_entry_file(entry_path)

def test3():
	entries_folder = Path(cache_path).joinpath('entries')
	entries_map = {}
	for file in entries_folder.iterdir():
		if not file.is_dir():
			entry_file = EntryFile()
			entry_file.parse_entry_file(file)

if __name__ == '__main__':
	test1()
	test2('000CDFA8FB68D63B101F03F1C7759A37ABD61919')
	test3()
