#  Macarthur Inbody <admin-contact@transcendental.us>
#  Licensed under LGPLv3 Or Later (2020)

# !/usr/bin/env python3
from .lib import nato_translated_words


def make_encoded_msg(length=3):
	from random import randint
	padding_character = "!#%&,/;<>@_`{|}~ "[randint(0,16)]
	random_string = nato_translated_words(length)
	output_string = ''

	for x in random_string:
		output_string += hex(ord(x))[2:]
		output_string += padding_character

	return random_string,output_string,padding_character

def make_byteme():

	flag,encoded_string,padding_character = make_encoded_msg()
	with open("files/hex.txt","w") as fh:
		fh.write(encoded_string)

	fake_flag,encoded_string,fake_padding = make_encoded_msg(1)
	desc=f"""<p>The EBS is on the fritz and sending out messages in hex for some reason. We can't tell if they're sending gibberish or real messages so we need you to give us the answer. You have to take the string given to you in hex.txt and then decode the hex string given to you via the delimiter. Then convert this string into ASCII text. Note the string you get back may not make any sense but as long as it contains <i>only</i> alphanumeric characters,spaces, and maybe a "-" then it's the right flag.</p><p><b>Padding Character:<i>{padding_character}</i></b></p>
<h3>TESTCASE</h3><p>Given the string below and the padding character of <b>{fake_padding}</b> what was the original string.</p>
<p class="text-monospace">{encoded_string}</p>
<p> The answer would thus be <b>{fake_flag}</b> after decoding the hex characters.</p>"""

	return desc,flag,"hex.txt"
