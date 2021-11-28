import sys, os
from pathlib import Path

from index_file import IndexFile, IndexRecord
from entry_file import EntryFile


def test1(cache_path):
	index_path = Path(cache_path).joinpath('index')
	index_file = IndexFile()
	index_file.parse_index_file(index_path)

def test2(cache_path, entry_name):
	entry_path = Path(cache_path).joinpath('entries').joinpath(entry_name)
	entry_file = EntryFile()
	entry_file.parse_entry_file(entry_path)

def test3(entry_path):
	entry_file = EntryFile()
	entry_file.parse_entry_file(entry_path)

def test4(cache_path):
	entries_folder = Path(cache_path).joinpath('entries')
	entries_map = {}
	for file in entries_folder.iterdir():
		if not file.is_dir():
			print('entry', file)
			entry_file = EntryFile()
			entry_file.parse_entry_file(file)
			print('key', entry_file.key)
			print('hash_codes', entry_file.hash_codes)
			# print('elements', entry_file.elements)
			elem_count = len(entry_file.elements)
			if elem_count > 0:
				count = int(elem_count/2)
				k = 0
				for i in range(count):
					print('element key', entry_file.elements[k])
					k += 2
			for chunk in entry_file.chunks:
				print('chunk', len(chunk))

def dump_chunk(self, buf, folder, chunk_name):
	logs_folder = Path('logs').joinpath(folder).joinpath(self.entry_file)
	if not logs_folder.exists():
		os.makedirs(logs_folder)
	file_path = logs_folder.joinpath(chunk_name)
	with open(file_path, 'wb') as fd:
		fd.write(buf)

if __name__ == '__main__':
	# test1('cache2')
	# test2('cache2', '000CDFA8FB68D63B101F03F1C7759A37ABD61919')
	test4('cache2')
	# test3('logs/error/00A1CCFD94424EFD95D20D7BDED33F7892865F5D/chunk1')
