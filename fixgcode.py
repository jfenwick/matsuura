import argparse

parser = argparse.ArgumentParser(description='Fix G-Code output from HSMworks to work with Yasnac controller on Matsuura')
parser.add_argument('infile', metavar='filename', type=file,
                   help='File to fix')
args = parser.parse_args()

# scale the value of a gcode by 10000
# if cast is true, cast to an int instead of scaling
def scale_code( line, code, cast ):
	eol = False
	index = line.find(code)
	if index > -1:
		end = line[index:].find(' ')
		# if there is no space character, assume at end of line
		if end == -1:
			end = len(line) - 1
			# send end of line flag
			eol = True
		x = line[index+1:index+end]
		# if cast flag set, cast the value to int instead of scaling
		if cast:
			x = int(float(x))
		else:
			x = int(float(x) * 10000)
		line = line[:index] + code + str(x) + line[index+end:]
		# if end of line, add newline
		if eol:
			line = line + "\n"
		return line
	return line

# input file
fi = args.infile
# input file name
foname = fi.name + ".fix"
# output file
fo = open(foname, "w+")

last_gcode = ''
# loop over all the lines in the file
for line in fi:
	if line[0] == '(':
		fo.write(line)
		continue

	# find the first g-code and save it
	g_index = line.find('G')
	if g_index > -1:
		next_space = line[g_index:].find(" ")
		last_gcode = line[g_index:g_index+next_space]

	# check if the line contains N0000
	# if it does, change it to N0001
	if line.find('N0000') > -1:
		# this should be N0001
		line = line.replace("N0000", "N0001")

	line = scale_code(line, 'X', False)
	line = scale_code(line, 'Y', False)
	line = scale_code(line, 'Z', False)
	line = scale_code(line, 'I', False)
	line = scale_code(line, 'J', False)
	line = scale_code(line, 'K', False)
	line = scale_code(line, 'F', True)

	# check if there's a line that starts with X, Y or Z instead of a G
	# we're going to assume it's the g code from the last line
	# this may get ugly at some point in the future but for now it looks like that's the case where it's happening
	first_index = line.find(" ")
	first_index = first_index + 1

	if line[first_index] == 'X' or line[first_index] == 'Y' or line[first_index] == 'Z':
		firstpart, secondpart = line[0:first_index],line[first_index:len(line)]
		#secondpart = 'G03 ' + secondpart
		secondpart = last_gcode + ' ' + secondpart
		line = firstpart + secondpart
	fo.write(line)
fo.close()