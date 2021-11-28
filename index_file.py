import struct
from datetime import datetime

from constants import INDEX_HEADER_SIZE, INDEX_RECORD_SIZE


class IndexFile:
	def __init__(self):
		# header properties, 16 bytes
		self.version = 0
		self.timestamp = 0
		self.dirty_flag = 0
		self.kbwritten = 0

		self.time = None
		self.records = []

	def parse_header(self, buf):
		self.version, self.timestamp, self.dirty_flag, self.kbwritten = struct.unpack('>IIII', buf)
		self.time = datetime.fromtimestamp(self.timestamp)

	def __str__(self):
		return "version: %d, time: %d(%s), dirty_flag: %d, kbwritten: %d" % \
		(self.version, self.timestamp, self.time.strftime('%Y-%m-%d %H:%M:%S'), self.dirty_flag, self.kbwritten)

	def parse_index_file(self, file_path):
		with open(file_path, 'rb') as fd:
			data = fd.read()
		pos = 0
		self.parse_header(data[pos:pos+INDEX_HEADER_SIZE])
		pos += INDEX_HEADER_SIZE
		record_buf = data[pos:]
		record_size = INDEX_RECORD_SIZE
		record_count = int(len(record_buf)/record_size)
		pos = 0
		for i in range(record_count):
			buf = record_buf[pos:pos+record_size]
			pos += record_size
			record = IndexRecord()
			record.parse_record(buf)
			self.records.append(record)


class IndexRecord:

	def __init__(self):
		# header properties, 16 bytes
		self.hash_code = 0
		self.frecency = 0
		self.origin_attr_hash = 0
		self.start_time = 0
		self.end_time = 0
		self.content_type = 0
		self.flags = 0

	def parse_record(self, buf):
		pos = 0
		self.hash_code = buf[pos:pos+20]
		pos += 20
		self.frecency, = struct.unpack('>I', buf[pos:pos+4])
		pos += 4
		self.origin_attr_hash, = struct.unpack('>Q', buf[pos:pos+8])
		pos += 8
		self.start_time, self.end_time = struct.unpack('>HH', buf[pos:pos+4])
		pos += 4
		self.content_type, = struct.unpack('>B', buf[pos:pos+1])
		pos += 1
		self.flags, = struct.unpack('>I', buf[pos:pos+4])