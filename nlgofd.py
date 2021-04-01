#!/usr/bin/python

import sys
line = 0
first_arg = True
past_input = {}
print_buffer = 0;
buffer_len = 1;

def panic():
	raise ValueError("A very specific bad thing happened.")

def nop(current, varstr):
	return varstr

def add(current, varstr):
	return current + varstr

def sub(current, varstr):
	return current - varstr

def mult(current, varstr):
	return current * varstr

def div(current, varstr): 
	global blokestack
	if varstr == 0 and current == 0:
		return 1
	elif current == 0:
		panic()
	else:
		return varstr // current

def give(current, varstr):
	global print_buffer, buffer_len
	if current == 0:
		print_buffer = print_buffer * varstr + line % varstr
		buffer_len *= varstr
		while (buffer_len > 255): # only handles single len chars
			print (chr(print_buffer % 256), end="")
			buffer_len //= 256
			print_buffer = print_buffer // 256
	return buffer_len

def brack(current, varstr):
	if varstr == 0:
		return current
	else:
		panic()

def endbrack(current, varstr): 
	global blokestack
	blokestack.append(current);
	return varstr

def take(current, varstr):
	global past_input, prog_index
	if not current in past_input:
		if current == 1:
			past_input.insert(1, len(sys.argv) - prog_index)
		else:
			if current == 0:
				tmp = input() + "\n"
			else:
				arg = current - 2
				arg_on = 1
				tmp = ""
				while arg_on <= len(sys.argv) - prog_index:
					if arg == 0:
						tmp = sys.argv[prog_index + arg_on]
					elif arg == 1:
						tmp = open(sys.argv[prog_index + arg_on], "r").read()

			past_input[current] = 0
			for c in reversed(tmp):
				past_input[current] = add_with_unicode(ord(c), past_input[current])
	if varstr == 0:
		retval = past_input.pop(current)
	else:
		retval = past_input[current] % varstr
		past_input[current] //= varstr
		if past_input[current] == 0:
			past_input.pop(current)
	return retval

def add_with_unicode(value, existingValue):
	if value <= 0x7F:
		return value + existingValue * 0x100
	elif value <= 0x7FF:
		return (value & 0x7C0) * 0x4 + (value & 0x3F) + existingValue * 0x10000 + 0xC080
	elif value <= 0xffff:
		return (value & 0xF000) * 0x10 + (value & 0xFC0) * 0x4 + (value & 0x3F) + existingValue * 0x1000000 + 0xE08080
	else:
		return (value & 0x1C0000) * 0x14 + (value & 0x3F000) * 0x10 + (value & 0xFC0) * 0x4 + (value & 0x3F) + existingValue * 0x100000000 + 0xF0808080

action = {'.' : nop,
		  '+' : add,
		  '-' : sub,
		  '*' : mult,
		  '\\' : div,
		  ':' : give,
		  '(' : brack,
		  ')' : endbrack,
		  '?' : take
		  }

def parse(the_code):
	global blokestack
	blokestack = []
	next = '.'
	varstr = ""
	current = 0
	for c in the_code:
		if c == '.':
			panic()
		elif c == '(':
			current = action[next](current,blokestack.pop())
			next = c
		elif c == '+' or c == '-' or c == '*' or c == '\\' or c == ':' or c == ')' or c == '?':
			current = action[next](current, parse_val(varstr))
			next = c
			varstr = ""
		else:
			varstr += c
	if (not len(blokestack) == 0):
		panic()
	return action[next](current, parse_val(varstr))


def parse_val(valstr):
	if valstr == "":
		return 0
	retval = parse_val_internal(valstr)
	if retval is None:
		return 0
	else:
		return retval

def parse_val_internal(valstr):
	last_val = None
	while True:
		if valstr in values:
			retval = values[valstr]
			if not last_val is None:
				tmp = retval
				while True:
					tmp /= 19
					last_val *= 19
					if tmp < 1:
						break
				retval += last_val
			return  retval
		else:
			has = False
			if len(valstr) == 1:
				return last_val
			for h in range(len(valstr)-1, 0, -1):
				if valstr[:h] in values:
					tmp = values[valstr[:h]]
					if not last_val is None:
						tmp2 = tmp
						while True:
							tmp2 /= 19
							last_val *= 19
							if tmp2 < 1:
								break
						tmp += last_val
					valstr = valstr[h:]
					last_val = tmp
					has = True
					break;
			if not has:
				valstr = valstr[1:]

i = 0
debug = False
use_hex = False
for arg in sys.argv:
	if first_arg:
		first_arg = False
	else:
		if arg == "-d" or arg == "--debug":
			debug = True
		if arg == "-h" or arg == "--hex":
			use_hex = True
		if arg[len(arg) - 3:] == ".fd":
			file = arg
			prog_index = i
			break;
	i += 1

code = open(file, "r").readlines()

line = 0
values = {}

while (not code[line] == "\n"):
	
	if debug:
		print (str(line) + ": " + code[line].rstrip("\n"), end="")
	lineparts = code[line].rstrip("\n").split(",");

	first_arg = True
	for part in lineparts:
		if first_arg:
			line = parse(part)
			first_arg = False
			if debug:
				if (use_hex):
					print (" -> 0x" + format(line, "X"), end="")
				else:
					print (" -> " + str(line), end="")
		else:
			if '.' in part or '+' in part or '-' in part or '*' in part or '\\' in part or ':' in part or '(' in part or ')' in part or '?' in part:
				panic()
			else:
				values[part] = line
	line = line % len(code)
	if debug:
		input()
if debug:
	print (str(line) + ":")
print()
