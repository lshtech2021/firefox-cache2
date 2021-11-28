import os
import struct
from datetime import datetime
from pathlib import Path
import gzip

from constants import META_HEADER_SIZE, kMinMetadataRead, kChunkSize, \
	kMaxElementsSize, kAlignSize

"""
Refs:
https://searchfox.org/mozilla-central/source/netwerk/cache2/CacheFile.cpp

"""
class MetaDataHeader:
	version: int
	fetch_count: int
	last_fetched: int
	last_modified: int
	frecency: int
	expire_time: int
	key_size: int
	flags: int


class EntryFile:

	def __init__(self):
		self.entry_file = None
		self.key = None
		self.hash_expected = 0
		self.hash_buf = None
		self.hash_codes = []
		self.elements = []
		self.chunks = []
		self.metadata_header = MetaDataHeader()

	def parse_entry_file(self, file_path):
		self.entry_file = Path(file_path).name
		with open(file_path, 'rb') as fd:
			data = fd.read()
		self.parse_entry(data)

	def parse_entry(self, data):
		size = len(data)
		offset = 0
		if size < kMinMetadataRead:
			offset = 0
		else:
			offset = size - kMinMetadataRead
		offset = int(offset/kAlignSize) * kAlignSize
		buf_size = size - offset
		metadata_buf = data[offset:offset+buf_size]
		data_size = self.parse_metadata(metadata_buf, data, size)
		data_buf = data[:data_size]
		self.parse_chunks(data_buf)

	def parse_metadata(self, metadata_buf, data, size):
		buf_size = len(metadata_buf)
		real_offset, = struct.unpack('>I', metadata_buf[-4:])
		used_offset = size - buf_size
		if real_offset < used_offset:
			missing = used_offset - real_offset
			buf_size = buf_size + missing
			metadata_buf = data[real_offset:real_offset+buf_size]
			used_offset = size - buf_size

		meta_offset = real_offset
		buf_offset = real_offset - used_offset
		meta_pos_offset = buf_size - 4
		hashes_offset = buf_offset + 4
		hash_count = int(meta_offset / kChunkSize)
		if meta_offset % kChunkSize != 0:
			hash_count += 1
		hashes_len = hash_count * 2
		hdr_offset = hashes_offset + hashes_len
		key_offset = hdr_offset + META_HEADER_SIZE
		header_buf = metadata_buf[hdr_offset:key_offset]
		metaHdr = self.parse_meta_header(header_buf)
		self.metadata_header = metaHdr
		key_size = metaHdr.key_size
		self.key = metadata_buf[key_offset: key_offset + key_size + 1]
		elements_offset = metaHdr.key_size + key_offset + 1;
		if elements_offset > meta_pos_offset:
			print('error: elements offset %d exceeds %d' % (elements_offset, meta_pos_offset))
		else:
			element_buf_size = meta_pos_offset - elements_offset
			self.parse_elements(metadata_buf[elements_offset:elements_offset+element_buf_size], element_buf_size)

		hash_buf_size = meta_pos_offset - hashes_offset
		hash_buf = metadata_buf[hashes_offset:hashes_offset+hash_buf_size]
		self.hash_expected, = struct.unpack('>I', metadata_buf[:4])
		hash_buf = metadata_buf[hashes_offset:hashes_offset+hashes_len]
		self.parse_hashes(hash_buf, hash_count)
		return meta_offset

	def parse_meta_header(self, buf):
		metaHdr = MetaDataHeader()
		version, fetch_count, last_fetched, last_modified, frecency, expire_time, key_size, flags =\
		struct.unpack('>IIIIIIII', buf[0:META_HEADER_SIZE])
		metaHdr.version = version
		metaHdr.fetch_count = fetch_count
		metaHdr.last_fetched = last_fetched
		metaHdr.last_modified = last_modified
		metaHdr.frecency = frecency
		metaHdr.expire_time = expire_time
		metaHdr.key_size = key_size
		metaHdr.flags = flags
		return metaHdr

	def parse_elements(self, buf, buf_size):
		i = 0
		start = 0
		while i < buf_size:
			if buf[i] == 0:
				key = buf[start:i]
				self.elements.append(key)
				start = i + 1
			i+=1

	def parse_hashes(self, hash_buf, count):
		i = 0
		pos = 0
		while i < count:
			hash_value, = struct.unpack('>H', hash_buf[pos:pos+2])
			self.hash_codes.append(hash_value)
			i+=1
			pos +=2

	def parse_chunks(self, data_buf):
		size = len(data_buf)
		i = 0
		pos = 0
		while pos < size:
			chunk_size = min(kChunkSize, size - pos)
			chunk_buf = data_buf[pos:pos+chunk_size]
			pos += kChunkSize
			i += 1
			if chunk_buf[0:2] == b'\x1F\x8B':
				try:
					plain_buf = gzip.decompress(chunk_buf)
					self.chunks.append(plain_buf)
				except Exception as e:
					print(e)
			else:
				self.chunks.append(chunk_buf)
