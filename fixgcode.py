import argparse

parser = argparse.ArgumentParser(description='Fix G-Code output from HSMworks to work with Yasnac controller on Matsuura')
parser.add_argument('infile', metavar='filename', type=file,
                   help='File to fix')
args = parser.parse_args()

# scale the value of a gcode by amount
def scale_code( line, code, amount ):
	eol = False
	index = line.find(code)
	if index > -1:
		end = line[index:].find(' ')
		# if there is no space character, assume at end of line
		if end == -1:
			end = len(line) - 1
			# send end of line flag
			eol = True
		# find the numerical part of the gcode
		x = line[index+1:index+end]
		# scale the gcode
		x = int(float(x) * amount)
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

	line = scale_code(line, 'X', 10000)
	line = scale_code(line, 'Y', 10000)
	line = scale_code(line, 'Z', 10000)
	line = scale_code(line, 'I', 10000)
	line = scale_code(line, 'J', 10000)
	line = scale_code(line, 'K', 10000)
	line = scale_code(line, 'F', 10)

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