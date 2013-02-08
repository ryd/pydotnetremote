# Module DotNetRemote
#
# This Module parse and marshall data stream from .NET Remote protocoll designed by Microsoft.
# It took my information from Microsoft public documentation and did some skip bytes issues for
# my tests. It far away from production use and my be used for research and fuzzing the protocol.
#
# Author:	Jens Muecke - jens at nons dot de
# URL: 		https://github.com/ryd/pydotnetremote
# Licence:	Apache License, Version 2.0, January 2004, http://www.apache.org/licenses/
#
# Thx to JaWa Jan

import Log
import struct

def get_number(data, rev=True):
	l = list(data)
	if rev:
		l.reverse()
	v = 0
	for b in l:
		v = v * 256 + ord(b)
	return v

def get_string(data):
	l = ord(data[0])
	p = 1
	if (l > 127):
		p = 2
		l2 = ord(data[1])
		if l2 < 128:
			l = l - 128 + (l2 * 128)
		else:
			l3 = ord(data[2])
			p = 3
			if l3 < 128:
				l = l - 128 + ((l2 - 128) * 128) + (l3 * 128 * 128)
			else:
				Log.error("To Big String") # there is one more layer
				exit(0)
		
	return data[p:p+l], p+l

def to_string(s, length=0):
	data = []
	if length == 0:
		length = len(s)
	if length < 128:
		data.append(to_byte(length))
	elif length < 256:
		data.append(to_byte(length))
		data.append('\x01')
	else:
		Log.error("Can't serialize Strings that long: %d" % length)
		exit(1)
	data.append(s)	
	return "".join(data)

def to_int(n):
	return struct.pack("<L", n)

def to_byte(n):
	return struct.pack("<B", n)

def parse_record_arraysingleobject(data, start):
	record = {}
	record["Type"] = "ArraySingleObject"
	record["ObjectId"] = get_number(data[start+1:start+5])
	record["Length"] = get_number(data[start+5:start+9])
	return record, start + 9

def parse_record_arraysingleprimitive(data, start):
	record = {}
	record["Type"] = "ArraySinglePrimitive"
	record["ObjectId"] = get_number(data[start+1:start+5])
	record["Length"] = get_number(data[start+5:start+9])
	record["PrimitiveType"] = get_type_enum(ord(data[start+9]))
	pos = start + 10
	record["Value"] = data[pos:pos+record["Length"]]
	return record, pos + record["Length"]

def parse_record_classwithid(data, start):
	record = {}
	record["Type"] = "ClassWithId"
	record["ObjectId"] = get_number(data[start+1:start+5])
	record["MetadataId"] = get_number(data[start+5:start+9])
	return record, start + 9

def parse_record_binarylibrary(data, start):
	record = {}
	record["Type"] = "BinaryLibrary"
	record["LibraryId"] = get_number(data[start+1:start+5])
	record["LibraryName"], pos = get_string(data[start+5:])
	return record, start + 5 + pos

def parse_record_binaryobjectstring(data, start):
	record = {}
	record["Type"] = "BinaryObjectString"
	record["ObjectId"] = get_number(data[start+1:start+5])
	record["Value"], pos = get_string(data[start+5:])
	return record, start + 5 + pos


def get_binary_type_enum(id):
	if id == 0:
		return "Primitive"
	elif id == 1:
		return "String"
	elif id == 2:
		return "System.Object"
	elif id == 3:
		return "SystemClass"
	elif id == 4:
		return "Class"
	elif id == 5:
		return "ObjectArray"
	elif id == 6:
		return "StringArray"
	elif id == 7:
		return "PrimitiveArray"
	elif id == 8:
		return "Int32"
	elif id == 9:
		return "Int64"
	# else
	Log.error("Unkown BinaryTypeEnum -> %d" % id)
	return None

def to_binary_type_enum(id):
	if id == "Primitive":
		return '\x00'
	elif id == "String":
		return '\x01'
	elif id == "System.Object":
		return '\x02'
	elif id == "SystemClass":
		return '\x03'
	elif id == "Class":
		return '\x04'
	elif id == "ObjectArray":
		return '\x05'
	elif id == "StringArray":
		return '\x06'
	elif id == "PrimitiveArray":
		return '\x07'
	elif id == "Int32":
		return '\x08'
	elif id == "Int64":
		return '\x09'
	elif id == "Boolean":
		return '\x01'
	elif type(id) == dict:
		t = to_string(id["TypeName"])
		if id["Type"] == "Class":
			t+= to_int(id["LibraryId"])
		return t
	# else
	return to_byte(to_type_enum(id))

def to_binaryarraytypeenum(s):
	if s == "Single":
		return "\x00"
	elif s == "Jagged":
		return "\x01"
	elif s == "Rectangular":
		return "\x02"
	elif s == "SingleOffset":
		return "\x03"
	elif s == "JaggedOffset":
		return "\x04"
	elif s == "RectangularOffset":
		return "\x05"
	else:
		Log.error("Unkown BinaryArrayTypeEnum - %s" % s)
		exit(1)

def get_binary_array_type_enum(id):
	if id == 0:
		return "Single"
	elif id == 1:
		return "Jagged"
	elif id == 2:
		return "Rectangular"
	elif id == 3:
		return "SingleOffset"
	elif id == 4:
		return "JaggedOffset"
	elif id == 5:
		return "RectangularOffset"
	# else
	Log.error("Unkown BinaryArrayTypeEnum - %d" % id)
	return None

def get_type_enum(t):
	if t == 1:
		return "Boolean"
	elif t == 2:
		return "Byte"
	elif t == 3:
		return "Char"
	elif t == 4:
		return "Currency"
	elif t == 5:
		return "Decimal"
	elif t == 6:
		return "Double"
	elif t == 7:
		return "Int16"
	elif t == 8:
		return "Int32"
	elif t == 9:
		return "Int64"
	elif t == 10:
		return "SByte"
	elif t == 11:
		return "Single"
	elif t == 12:
		return "TimeSpan"
	elif t == 13:
		return "DateTime"
	elif t == 14:
		return "UInt16"
	elif t == 15:
		return "UInt32"
	elif t == 16:
		return "UInt64"
	elif t == 17:
		return "Null"
	elif t == 18:
		return "String"
	elif t == 21:
		return "StringValueWithCode"
	else:
		Log.error("Unkown Type - %d" % t)
		return None

def to_type_enum(t):
	if t == "Boolean":
		return 1
	elif t == "Byte":
		return 2
	elif t == "Char":
		return 3
	elif t == "Currency":
		return 4
	elif t == "Decimal":
		return 5
	elif t == "Double":
		return 6
	elif t == "Int16":
		return 7
	elif t == "Int32":
		return 8
	elif t == "Int64":
		return 9
	elif t == "SByte":
		return 10
	elif t == "Single":
		return 11
	elif t == "TimeSpan":
		return 12
	elif t == "DateTime":
		return 13
	elif t == "UInt16":
		return 14
	elif t == "UInt32":
		return 15
	elif t == "UInt64":
		return 16
	elif t == "Null":
		return 17
	elif t == "String":
		return 18
	elif t == "StringValueWithCode":
		return 21
	else:
		Log.error("Unkown Type - %s" % t)
		exit(1)

def parse_record_memberprimitivetype(data, start):
	record = {}
	record["Type"] = "MemberPrimitiveType"
	record["PrimitiveType"] = get_type_enum(ord(data[start+1]))
	pos = start + 2
	if record["PrimitiveType"] in ["Boolean"]:
		record["Value"] = ord(data[pos:pos+1])
		pos += 1
	else: 
		error("	Type=%s" % record["PrimitiveType"])
		Log.print_hex(data[start:start+16])
		record["Value"] = None
		pos += 1
	return record, pos

def parse_record_binaryarray(data, start):
	record = {}
	record["Type"] = "BinaryArray"
	record["ObjectId"] = get_number(data[start+1:start+5])
	record["BinaryArrayType"] = get_binary_array_type_enum(ord(data[start+5]))
	if record["BinaryArrayType"] == None:
		return None, 0
	record["Rank"] = get_number(data[start+6:start+10])
	record["Length"] = get_number(data[start+10:start+14])
	# Might be wrong
	record["TypeEnum"] = get_binary_type_enum(ord(data[start+14]))
	record["SystemClass"], pos = get_string(data[start+15:])
	return record, start + 15 + pos

def parse_record_classwithmembersandtypes(data, start):
	record = {}
	record["Type"] = "ClassWithMembersAndTypes"
	record["ObjectId"] = get_number(data[start+1:start+5])
	record["ObjectName"], pos = get_string(data[start+5:])
	pos += start + 5
	record["MemberCount"] = get_number(data[pos:pos+4])
	pos += 4
	i = 0
	record["MemberNames"] = []
	while i < record["MemberCount"]:
		name, t = get_string(data[pos:])
		record["MemberNames"].append(name)
		i += 1
		pos += t
	record["MemberTypeInfo"] = []
	i = 0
	additional = []
	while i < record["MemberCount"]:
		t = get_binary_type_enum(ord(data[pos]))
		if t == None:
			return None, 0
		if t in ["Primitive", "SystemClass", "Class", "PrimitiveArray"]:
			additional.append(t)
		record["MemberTypeInfo"].append(t)
		i += 1
		pos += 1
	for i in additional:
		if i in ["Primitive", "PrimitiveArray"]:
			t = get_type_enum(ord(data[pos]))
			if t == None:
				return None, 0
			record["MemberTypeInfo"].append(t)
			pos += 1
		if i in ["Class", "SystemClass"]:
			name, t = get_string(data[pos:])
			pos += t
			c = {}
			if i == "Class":
				c["Type"] = "Class"
				c["TypeName"] = name
				c["LibraryId"] = get_number(data[pos:pos+4])
				pos += 4
			else:
				c["Type"] = "SystemClass"
				c["TypeName"] = name
			record["MemberTypeInfo"].append(c)
	record["LibraryId"] = get_number(data[pos:pos+4])
	return record, pos + 4

def parse_record_classwithmembers(data, start):
	record = {}
	record["Type"] = "ClassWithMembers"

	x = 59
	record["Data"] = data[start:start+x]
	Log.print_hex(data[start+x:start+x+64])
	return record, start+x

	record["ObjectId"] = get_number(data[start+1:start+5])
	record["ObjectName"], pos = get_string(data[start+5:])
	pos += start + 5
	record["MemberCount"] = get_number(data[pos:pos+4])
	pos += 4
	i = 0
	record["MemberNames"] = []
	while i < record["MemberCount"]:
		name, t = get_string(data[pos:])
		record["MemberNames"].append(name)
		i += 1
		pos += t
	record["LibraryId"] = get_number(data[pos:pos+4])
	Log.error(record)
	return record, pos + 4

def parse_record_systemclasswithmembersandtypes(data, start):
	record = {}
	record["Type"] = "SystemClassWithMembersAndTypes"
	record["ObjectId"] = get_number(data[start+1:start+5])
	
	Log.print_hex(data[start:start+32])

	# stupid workaround
	if record["ObjectId"] > 0x01000000:
		Log.error("	Skip 9 Bytes in SystemClassWithMembersAndTypes parser")
		record["skip1"] = data[start+5:start+14]
		start += 9

	record["ObjectName"], pos = get_string(data[start+5:])
	Log.dbg("	# Systemobjectname=%s" % record["ObjectName"])
	pos += start + 5
	record["MemberCount"] = get_number(data[pos:pos+4])
	pos += 4
	i = 0
	record["MemberNames"] = []
	while i < record["MemberCount"]:
		name, t = get_string(data[pos:])
		record["MemberNames"].append(name)
		i += 1
		pos += t
	# stupid bugfix
	record["MemberTypeInfo"] = []
	i = 0
	additional = []
	while i < record["MemberCount"]:
		t = get_binary_type_enum(ord(data[pos]))
		if t == None:
			return None, 0
		if t in ["Primitive", "SystemClass", "Class", "PrimitiveArray", "System.Object"]:
			additional.append(t)
		record["MemberTypeInfo"].append(t)
		i += 1
		pos += 1
	for i in additional:
		if i in ["Primitive", "PrimitiveArray"]:
			t = get_type_enum(ord(data[pos]))
			if t == None:
				return None, 0
			record["MemberTypeInfo"].append(t)
			pos += 1
		if i in ["Class", "SystemClass"]:
			name, t = get_string(data[pos:])
			pos += t
			c = {}
			if i == "Class":
				c["Type"] = "Class"
				c["TypeName"] = name
				c["LibraryId"] = get_number(data[pos:pos+4])
				pos += 4
			else:
				c["Type"] = "SystemClass"
				c["TypeName"] = name
			record["MemberTypeInfo"].append(c)
	if get_number(data[pos:pos+4]) == 7:
		Log.error("	Found Library - fix 4 bytes - this is not in the specs")
		record["skip2"] = data[pos:pos+4]
		pos += 4
	return record, pos

def parse_record_memberreference(data, start):
	record = {}
	record["Type"] = "MemberReference"
	record["IdRef"] = get_number(data[start+1:start+5])
	return record, start + 5

def parse_record_memberprimitiveuntyped(data, start, length):
	record = {}
	record["Type"] = "MemberPrimitiveUnTyped"
	record["Value"] = data[start:start+length]
	return record, start + length

def parse_record_objectnull(data, start):
	record = {}
	record["Type"] = "ObjectNull"
	return record, start + 1

def parse_methode_call_record(data, start):
	record = {}
	r_type = ord(data[start])
	if r_type == 1: # ClassWithId
		return parse_record_classwithid(data, start)
	elif r_type == 3: # ClassWithMembers
		return parse_record_classwithmembers(data, start)
	elif r_type == 4: # SystemClassWithMembersAndTypes
		return parse_record_systemclasswithmembersandtypes(data, start)
	elif r_type == 5: # ClassWithMembersAndTypes
		return parse_record_classwithmembersandtypes(data, start)
	elif r_type == 6: # BinaryObjectString
		return parse_record_binaryobjectstring(data, start)
	elif r_type == 7: # BinaryArray
		return parse_record_binaryarray(data, start)
	elif r_type == 8: # MemberPrimitiveType
		return parse_record_memberprimitivetype(data, start)
	elif r_type == 9: # MemberReference
		return parse_record_memberreference(data, start)
	elif r_type == 10: # ObjectNull
		return parse_record_objectnull(data, start)
	# 11 == messageend
	elif r_type == 12: # BinaryLibrary
		return parse_record_binarylibrary(data, start)
	# 13 == ObjectNullMultible256
	# 14 == ObjectNullMultible
	elif r_type == 15: # ArraySinglePrimitive
		return parse_record_arraysingleprimitive(data, start)
	elif r_type == 16: # ArraySingleObject
		return parse_record_arraysingleobject(data, start)
	Log.error("Unkown Record Type: %d" % r_type)
	Log.print_hex(data[start:])
	return None, start + 1

def get_definition_list(record):
	def_list = []
	count = record["MemberCount"]
	offset = count
	for entry in record["MemberTypeInfo"][0:count]:
		if entry in ["String", "Byte"]:
			def_list.append(entry)
		elif entry == "SystemClass":
			def_list.append(entry)
			offset += 1
		elif entry in ["Primitive", "Class"]:
			def_list.append(record["MemberTypeInfo"][offset])
			offset += 1
		elif entry == "PrimitiveArray":
			def_list.append("Array")
			def_list.append(record["MemberTypeInfo"][offset])
			offset += 1			
		elif entry == "System.Object":
			def_list.append(entry)
		else:
			Log.error("Unkown MemberTypeInfo - %s"  % entry)
	return def_list[::-1]

def parse_methode_call_array(c, data):
	Log.info("  MethodeCallArray:")
	carray = []
	type_list = []
	pos = 0
	while len(data) > pos:
		if len(type_list) > 0:
			item = type_list.pop()
			Log.debug("	# Item %s" % item)
			#print_hex(data[pos:pos+16])
			extra = 0
			if item == "Array":
				item = type_list.pop()
				if item == "Int64":
					extra += 7
				elif item == "Byte":
					extra += 4
				else:
					error("Unkown Size of Array Prefix.")
					exit(1)
				Log.debug(" 	# ArrayType: %s" % item)
			if item == "Byte":
				record, pos = parse_record_memberprimitiveuntyped(data, pos, 1 + extra)
			elif item == "Int32":
				record, pos = parse_record_memberprimitiveuntyped(data, pos, 4 + extra)
			elif item == "Int64":
				record, pos = parse_record_memberprimitiveuntyped(data, pos, 8 + extra)
			elif item == "Boolean":
				#print_hex(data[pos:pos+16])
				record, pos = parse_record_memberprimitiveuntyped(data, pos, 1 + extra)
			elif item == "DateTime":
				Log.print_hex(data[pos:pos+8])
				record, pos = parse_record_memberprimitiveuntyped(data, pos, 8 + extra)
			elif item == "TimeSpan":
				Log.print_hex(data[pos:pos+8])
				record, pos = parse_record_memberprimitiveuntyped(data, pos, 8 + extra)
			#elif type(item) == dict: # class
			#	record, pos = parse_record_memberprimitiveuntyped(data, pos, 19 + extra)
			else:
				record, pos = parse_methode_call_record(data,pos)
		else:	
			record, pos = parse_methode_call_record(data,pos)
		if record == None:
			return False
		carray.append(record)
		if record["Type"] == "BinaryObjectString":
			Log.info("    BinaryObjectString(%d): %s" % (record["ObjectId"], record["Value"]))
		elif record["Type"] == "ClassWithId":
			Log.info("    ClassWithId(%d) => %d" % (record["ObjectId"], record["MetadataId"]))
		elif record["Type"] == "MemberReference":
			Log.info("    MemberReference(%d)" % record["IdRef"])
		elif record["Type"] == "BinaryLibrary":
			Log.info("    BinaryLibrary(%d) - %s" % (record["LibraryId"], record["LibraryName"]))
		elif record["Type"] in ["SystemClassWithMembersAndTypes", "ClassWithMembersAndTypes"]:
			Log.info("    %s(%d) %s" % (record["Type"], record["ObjectId"], record["MemberNames"]))
			Log.debug(record)
		elif record["Type"] == "MemberPrimitiveUnTyped":
			Log.info("    %s" % record["Type"])
			Log.print_hex(record["Value"])
		elif record["Type"] in ["ArraySinglePrimitive", "ArraySingleObject", "BinaryArray"]:
			Log.info("    %s(%d) - %d" % (record["Type"], record["ObjectId"], record["Length"]))
			if record["Type"] == "ArraySinglePrimitive":
				Log.print_hex(record["Value"], 32)
		else:
			Log.info("    %s" % record["Type"])
		if record["Type"] in ["ClassWithMembersAndTypes", "SystemClassWithMembersAndTypes"]:
			t = get_definition_list(record)
			if len(type_list) > 0 and len(t) > 0:
				skip = 19
				#Log.error("conflict: list %s and %s" % (type_list, t))
				#error("skip %d bytes and add them to record and empty list" % skip)
				Log.print_hex(data[pos:pos+skip])
				#record["skip3"] = data[pos:pos+skip]
				#pos += skip
				#type_list = []

				type_list += t
			else:
				type_list = t
	c["CallArray"] = carray
	return True

def parse_methode_call_request(c, data):
	call = {}
	call["flags"] = get_number(data[0:4])
	if ord(data[4]) != 18: # Expect MethodeName to be a string
		Log.error("Expect MethodeName to be a String")
		return False
	call["MethodeName"], pos = get_string(data[5:])
	pos += 5
	if ord(data[pos]) != 18: # Expect TypeName to be a string
		error("Expect TypeName to be a String")
		return False
	call["TypeName"], pos2 = get_string(data[pos+1:])
	pos2 += pos+1
	Log.info("  BinaryMethodeCall:")
	Log.info("    Flags: %d" % call["flags"])
	Log.info("    Methode: %s" % call["MethodeName"])
	Log.info("    Type: %s" % call["TypeName"])
	c["MethodeCall"] = call
	return parse_methode_call_array(c, data[pos2:])

def parse_methode_call_response(c, data):
	call = {}
	call["flags"] = get_number(data[0:4])
	Log.info("  BinaryMethodeResponse:")
	Log.info("    Flags: %d" % call["flags"])
	c["MethodeResponse"] = call
	return parse_methode_call_array(c, data[4:])

def parse(c, data):
	if ord(data[0]) == 0 and ord(data[-1]) == 11:	# check first and last byte (00 und 0b)
		Log.info("SerializedStreamHeader")
		header = {}
		header["RootId"] = get_number(data[1:5])
		header["RecordType"] = get_number(data[5:9])
		header["MajorVersion"] = get_number(data[9:13])
		header["MinorVersion"] = get_number(data[13:17])
		c["SerializaionHeader"] = header
		Log.info("  RootId: %d" % header["RootId"])
		Log.info("  RecordType: %d" % header["RecordType"])
		Log.info("  MajorVersion: %d" % header["MajorVersion"])
		Log.info("  MinorVersion: %d" % header["MinorVersion"])
		i = ord(data[17])
		if i == 21: # BinaryMethodeCall
			return parse_methode_call_request(c, data[18:-1])
		elif i == 22: # BinaryMethodeResponse
			return parse_methode_call_response(c, data[18:-1])
		Log.error("Unkown Methode - %d" % i)
		return False
	else:
		Log.error("Unkown Header - %d" % ord(data[0]))
		return False

def m_arraysingleobject(item, data):
	data.append('\x10')
	data.append(to_int(item["ObjectId"]))
	data.append(to_int(item["Length"]))
	return True

def m_memberreference(item, data):
	data.append('\x09')
	data.append(to_int(item["IdRef"]))
	return True

def m_binarylibrary(item, data):
	data.append('\x0c')
	data.append(to_int(item["LibraryId"]))
	data.append(to_string(item["LibraryName"]))
	return True

def m_memberprimitiveuntyped(item, data):
	data.append(item["Value"])
	return True

def m_classwithreferencesandtypes(item, data):
	data.append('\x05')
	data.append(to_int(item["ObjectId"]))
	data.append(to_string(item["ObjectName"]))
	data.append(to_int(item["MemberCount"]))
	for i in item["MemberNames"]:
		data.append(to_string(i))
	for i in item["MemberTypeInfo"]:
		data.append(to_binary_type_enum(i))
	data.append(to_int(item["LibraryId"]))
	if item.has_key("skip3"):
		data.append(item["skip3"])
	return True

def m_systemclasswithreferencesandtypes(item, data):
	data.append('\x04')
	data.append(to_int(item["ObjectId"]))
	if item.has_key("skip1"):
		data.append(item["skip1"])
	data.append(to_string(item["ObjectName"]))
	data.append(to_int(item["MemberCount"]))
	for i in item["MemberNames"]:
		data.append(to_string(i))
	for i in item["MemberTypeInfo"]:
		data.append(to_binary_type_enum(i))
	if item.has_key("skip2"):
		data.append(item["skip2"])
	return True

def m_binaryobjectstring(item, data):
	data.append('\x06')
	data.append(to_int(item["ObjectId"]))
	data.append(to_string(item["Value"]))
	return True

def m_objectnull(item, data):
	data.append('\x0a')
	return True

def m_binaryarray(item, data):
	data.append('\x07')
	data.append(to_int(item["ObjectId"]))
	data.append(to_binaryarraytypeenum(item["BinaryArrayType"]))
	data.append(to_int(item["Rank"]))
	data.append(to_int(item["Length"]))
	data.append(to_binary_type_enum(item["TypeEnum"]))
	data.append(to_string(item["SystemClass"]))
	return True

def m_classwithid(item, data):
	data.append('\x01')
	data.append(to_int(item["ObjectId"]))
	data.append(to_int(item["MetadataId"]))
	return True

def m_memberprimitivetype(item, data):
	data.append('\x08')
	data.append(to_byte(to_type_enum(item["PrimitiveType"])))
	if item["PrimitiveType"] in ["Boolean"]:
		data.append(to_byte(item["Value"]))
	else:
		Log.error("Unkown Primitive Type in PrimitiveType - %s" % item["PrimitiveType"])
	return True

def m_arraysingleprimitive(item, data):
	data.append('\x0f')
	data.append(to_int(item["ObjectId"]))
	data.append(to_int(item["Length"]))
	data.append(to_byte(to_type_enum(item["PrimitiveType"])))
	data.append(item["Value"])
	return True

def m_methode_call_array_data(c, data, item):
	if item["Type"] == "ArraySingleObject":
		return m_arraysingleobject(item, data)
	elif item["Type"] == "MemberReference":
		return m_memberreference(item, data)
	elif item["Type"] == "BinaryLibrary":
		return m_binarylibrary(item, data)
	elif item["Type"] == "ClassWithMembersAndTypes":
		return m_classwithreferencesandtypes(item, data)
	elif item["Type"] == "BinaryObjectString":
		return m_binaryobjectstring(item, data)
	elif item["Type"] == "MemberPrimitiveUnTyped":
		return m_memberprimitiveuntyped(item, data)
	elif item["Type"] == "ObjectNull":
		return m_objectnull(item, data)
	elif item["Type"] == "SystemClassWithMembersAndTypes":
		return m_systemclasswithreferencesandtypes(item, data)
	elif item["Type"] == "ClassWithId":
		return m_classwithid(item, data)
	elif item["Type"] == "BinaryArray":
		return m_binaryarray(item, data)
	elif item["Type"] == "MemberPrimitiveType":
		return m_memberprimitivetype(item, data)
	elif item["Type"] == "ArraySinglePrimitive":
		return m_arraysingleprimitive(item, data)
	return False

def m_methode_call_request(c, data):
	data.append('\x15') # Methode Call
	data.append(to_int(c["MethodeCall"]["flags"]))
	data.append('\x12') # Methode Name is a String
	data.append(to_string(c["MethodeCall"]["MethodeName"]))
	data.append('\x12') # Methode Name is a String
	data.append(to_string(c["MethodeCall"]["TypeName"]))
	for item in c["CallArray"]:
		if m_methode_call_array_data(c, data, item):
			Log.dbg("	Item serialized: %s" % item["Type"])
		else:
			Log.error("	Unable to serialize %s" % item["Type"])
			return False
		for i in data:
			if type(i) == int:
				Log.error("Zero Item detected")
	return True

def m_serializeheader(c, data):
		data.append('\x00')
		data.append(to_int(c["SerializaionHeader"]["RootId"]))
		data.append(to_int(c["SerializaionHeader"]["RecordType"]))
		data.append(to_int(c["SerializaionHeader"]["MajorVersion"]))
		data.append(to_int(c["SerializaionHeader"]["MinorVersion"]))
		if c.has_key("MethodeCall") and m_methode_call_request(c, data):
			Log.log("Serialized.")
		else:
			Log.error("Serialization failed.")
			exit(1)
		data.append("\x0b") # end flag
		return True

def marshall(c, data):
	#print(c)
	if c.has_key("SerializaionHeader"):
		return m_serializeheader(c, data)
	Log.error("Unkown Context to marshall")
	return False
