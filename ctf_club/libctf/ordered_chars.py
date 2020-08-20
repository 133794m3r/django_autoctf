"""
Ordinal Counter Flag Generator
Macarthur Inbody
AGPLv3 or Later
2020 -

This module will generate a test case and file for people to use. They have to create a script that loops through a string and adds up the ordinal value of each uppercase character. Then they have to return the total value.
"""


# then I import the function/module.
from random import randint

def ordinal_counter(input_string):
	"""
ordinal_counter({string} input_string)

This function will add up the ordinal values of each character of a string
so long as the character is uppercase.
args:
input_string {string} The string that we're going to process.

return total_value {int} The total value of all ordinal values summed.
	"""

	total_value = 0
	cp = 0
	input_string = [ord(x) for x in input_string]
	for cp in input_string:
		if 33 <= cp <= 90:
			total_value += cp

	return total_value


def make_string(string_length=100):
	"""
make_string({int} string_length)

This function will create a string of string_length size and return it.

args:
string_length {int} The length of the string to generate.

return out_string {string} the created string.

	"""

	charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
	out_string = ''
	j = 0
	for i in range(string_length):
		if j >= 150:
			out_string += ' '
			j = 0
		out_string += charset[randint(0, 52)]
		j += 1
	return out_string


def make_orded_chars(string_length=1024):
	"""
make_ordinal_counter({int} string_length)

This function will create the flag for you. It will create a dynamically created test case of 10 characters. Then create the help text for them to visualize it. Then it will show them the answer for that test case.


It will then generate the flag string. The string it generates will be 1024-2048 characters in length. The string has spaces at least every 150 characters so that word-wrapping will break at the space to make it easier to see when they open it. It will then calculate the total value of all of the uppercase letter's ordinal values and print it.


args
string_length {int} The length of the string to be generated.

return Nothing.
	"""

	# printing the initial string that's static.
	desc = "<p>The flag this time is to take the given string and give me the total sum of all of the characters of the string if they are uppercase. As per usual you have a test case given below. You can safely assume that the string you're working with will only be uppercase and lower case US alphabetical characters and that any spaces encountered can be safely discarded because they are solely there to make it easier to view the string.</p>"
	# generate the test case.
	string = make_string(10)
	# get the test-cases answer.
	total_value = ordinal_counter(string)
	# get the test cases's cp's in a list.
	ordinal_list = [ord(x) for x in string]
	# take each value and map it to a string that shows it's relationship.
	mapped_values = str(dict(zip(string, ordinal_list))).replace(": ", "=>")[1:-1]
	# print this help string. I'm using positional options. so {0} means first argument. {1} means second to format. This way I can easily repeat it.
	desc +=f"""<br /><h3>TESTCASE</h3>
<p>For the string<span class="text-mono">'{string}'</span>. If you added up the ordinal values of each of the characters you'd have gotten {total_value}. Thus the flag is {total_value}. The ordinal mappings can be seen below.<br /><span class="text-mono">{mapped_values}</span>
</p>"""
	# generate the flag string.
	string = make_string(randint(1024, 2048))
	# show the total value.
	flag = ordinal_counter(string)
	# make sure that it ends in a new line.
	# create/open the file for writing.
	fh = open("files/das_string.txt", "w")
	# write the string.
	fh.write(string)
	# print the flag.

	return desc,flag,"das_string.txt"