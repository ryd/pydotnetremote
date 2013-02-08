# File IO and helper
import Log

# compare two bytestreams
def diff_bytestream(d1, d2):
	if len(d1) > len(d2):
		Log.error("Input bigger than output")
		return False
	if len(d1) < len(d2):
		Log.error("Input smaller than output")
		return False
	i=0
	while i < len(d1):
		if d1[i] == d2[i]:
			i += 1
		else:
			Log.error(" Stream diff at pos %d from %d to %d" % (i, ord(d1[i]), ord(d2[i])))
			return False
	Log.log("Streams are equal")
	return True

# simple read to bytestream
def read_from_file(filename):
	f = open(filename, "rb")
	f.seek(0,2)
	size = f.tell()
	f.seek(0)
	data = f.read(size)
	f.close()
	return data

# very simple write data to file
def write_to_file(filename, data):
	f = open(filename, "wb")
	f.write(data)
	f.close()
	return True
