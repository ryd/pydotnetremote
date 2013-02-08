# All Logoutput functions

# console width
MAX_LENGTH=160

LEVEL=0

# set them empty on windows
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def log(s):
	if LEVEL < 0:
		return False
	print("[*] %s" % s)

# cut lines
def dbg(s):
	if LEVEL < 1:
		return False
	if len(s) > MAX_LENGTH:
		debug("%s..." % s[:MAX_LENGTH-3])
	else:
		debug(s)

def info(s):
	if LEVEL < 0:
		return False
	p = "[I] %s" % s
	if len(p) > MAX_LENGTH:
		p = "%s..." % p[:MAX_LENGTH-3]
	print(bcolors.OKGREEN + p + bcolors.ENDC)

def debug(s):
	if LEVEL < 1:
		return False
	print(bcolors.WARNING + "[D] %s"  % s + bcolors.ENDC)

def error(s):
	if LEVEL < 0:
		return False
	print(bcolors.FAIL + "[E] %s" % s + bcolors.ENDC)

def print_hex(data, linesize=16):
	if LEVEL < 2:
		return False
	l = len(data)
	p = 0
	while p < l:
		line = ""
		space = 0
		if p+linesize < l:
			line = data[p:p+linesize]
		else:
			line = data[p:]
			space = linesize-len(line)
		hs = ""
		cs = ""
		for b in list(line):
			number = ord(b)
			hbyte = ""
			if (number < 16):
				hbyte = "0%x" % number
			else:
				hbyte = "%x" % number
			if number > 31 and number < 128:
				cs = cs + b
			else:
				cs = cs + '.'

			hs = "%s%s " % (hs, hbyte)
		print("[H]	%s%s %s" % (hs, "   " * space, cs))
		p = p+linesize
