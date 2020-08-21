#  Macarthur Inbody <admin-contact@transcendental.us>
#  Licensed under LGPLv3 Or Later (2020)
from random import randint

def nato_translated_words(length=1):
	translation = { 'A':['Alpha','Afirm','Able'],
	'B':['Bravo','Baker','Buy'], 'C':['Charlie','Charlie','Cast'],
	'D':['Delta','Dog','Dock'], 'E':['Echo','Easy','Easy'],
    'F':['Foxtrot','Fox','France'], 'G':['Golf','George','Greece'],
	'H':['Hotel','How','Have'], 'I':['India','Italy','Item'],
	'J':['Juliet','Jig','John'], 'K':['Kilo','Kimberly','King'],
	'L':['Lima','Love','Lima'], 'M':['Mama','Mary','Mike'],
	'N':['November','Nan','Nap'], 'O':['Oscar','Oboe','Opal'],
	'P':['Papa','Peter','Pup'], 'Q':['Quebec','Queen','Quack'],
	'R':['Romeo','Roger','Rush'], 'S':['Sierra','Sugar','Sail'],
	'T':['Tango','Tare','Tape'], 'U':['Uniform','Uncle','Unit'],
	'V':['Victor','Victor','Vice'], 'W':['Whiskey','William','Watch'],
	'X':['Xray','X-ray','X-Ray'], 'Y':['Yankee','York','Yoke'],
	'Z':['Zulu','Zebra','Zed']}

	words = ['COME', 'DEAD', 'DIED', 'FOUR', 'FROM', 'FULL', 'GAVE', 'HAVE', 'HERE', 'LAST', 'LIVE', 'LONG', 'NOTE', 'POOR',
	         'TAKE', 'TASK', 'THAT', 'THEY', 'THIS', 'THUS', 'VAIN', 'WHAT', 'WILL', 'WORK', 'ABOVE', 'BIRTH', 'BRAVE', 'CAUSE',
	         'CIVIL', 'EARTH', 'EQUAL', 'FIELD', 'FINAL', 'FORTH', 'GREAT', 'LIVES', 'MIGHT', 'NEVER', 'NOBLY', 'PLACE', 'POWER',
	         'SCORE', 'SENSE', 'SEVEN', 'SHALL', 'THEIR', 'THESE', 'THOSE', 'UNDER', 'WHICH', 'WORLD', 'YEARS', 'BEFORE',
	         'ENDURE', 'FORGET', 'FOUGHT', 'GROUND', 'HALLOW', 'HIGHLY', 'LARGER', 'LITTLE', 'LIVING', 'NATION', 'PEOPLE',
	         'PERISH', 'PROPER', 'RATHER', 'SHOULD', 'BROUGHT', 'CREATED', 'DETRACT','MANY','TIMES','FISH','TANK']
	words_len = len(words)-1
	input_string = ''
	for i in range(length):
		input_string += words[randint(0,words_len)]


	output_string = ''
	translation_index = randint(0,2)
	for x in input_string:
		output_string += translation[x][translation_index] + " "

	return output_string


def rot_encode(msg):
	shift = randint(1,25)
	out = ''
	for c in msg:
		x = ord(c)
		if 65 <= x <= 90:
			#add the shift.
			x+=shift
			#if it's greater than 'Z'.
			if x>=90:
				#handle overflows.
				x=(x-90)+64

		#else if it's lowercase ascii.
		elif 97 <= x <= 122:
			#same thing again.
			x+=shift
			#same if it's greater than 'z'.
			if x>=122:
				#handle overflow.
				x=(x-122)+96

		out += chr(x)
	return out

def make_string(string_length=100,charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '):
	"""
make_string({int} string_length)

This function will create a string of string_length size and return it.

args:
string_length {int} The length of the string to generate.

return out_string {string} the created string.

	"""


	out_string = ''
	j = 0
	for i in range(string_length):
		if j >= 150:
			out_string += ' '
			j = 0
		out_string += charset[randint(0, 52)]
		j += 1
	return out_string