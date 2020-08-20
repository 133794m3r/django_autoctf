import random

def find_index(the_list, value, start_index=0):
	the_list_len = len(the_list)
	for i in range(start_index, the_list_len):
		if the_list[i] == value:
			index = i
			break
	else:
		return -1

	return i


def trim_the_array(the_list, max_value):
	"""
	First I just sort the list so that I know that once I find a value
	that's greater than the maximum value I can stop the loop and just
	trim all values greater than that. So long as all values are positive.
	so first I have to verify this information by seeing if any values are less than 0.
	"""
	# first I check to see if any element in the list is greater than the max value.
	maximum = max(the_list)
	minimum = min(the_list)
	if maximum > max_value and minimum > 0:
		# then I know I can filter the list to find the elements bigger than the maximum
		pass

	pass


def find_first_pair(array, chosen_sum, length=None):
	if length == None:
		next_item = len(array) - 1
	else:
		next_item = length - 1
	prev_item = 0
	working_sum = 0;
	while next_item > prev_item:
		working_sum = array[prev_item] + array[next_item]
		if working_sum == chosen_sum:
			break
		elif working_sum > chosen_sum:
			next_item -= 1
		else:
			prev_item += 1
	else:
		return False

	return True


# ok new plan I'm just going to see if there's any matches at all.
# If there are then I'll do list filtering.
def check_for_pairs(the_list, chosen_sum):
	found = False
	the_list_len = len(the_list)
	diff = 0
	i = 0;
	current_value = 0;
	found_index = 0;
	number_of_pairs = 0
	used_indicies = list();
	pair_tuples = list()
	number_of_searches = the_list_len
	if len(the_list) < 1:
		return found

	found = find_first_pair(the_list, chosen_sum, the_list_len)
	if not found:
		return '0;'

	for i in range(the_list_len):
		current_value = the_list[i]
		diff = chosen_sum - current_value
		found_index = find_index(the_list, diff, i)
		number_of_searches += ((found_index - i) if found_index != -1 else (the_list_len - i))
		if found_index != -1:
			number_of_searches += len(used_indicies)
			if found_index not in used_indicies:
				used_indicies.append(found_index)
				used_indicies.append(i)
				pair_tuples.append((the_list[found_index], the_list[i]))
				number_of_pairs += 1

	stringed = ''
	fixup = stringed.maketrans('()', '{}');
	stringed_pairs = ','.join(str(x).translate(fixup) for x in pair_tuples)
	stringed_pairs = f"{number_of_pairs};{stringed_pairs}";
	return stringed_pairs

def make_additional_pairs(number_of_items=100):
	random_list = [random.randint(-3,10) for _ in range(number_of_items)]
	chosen_sum = random.randint(1,10)

	with open("files/additional_pairs_list.csv","w") as fh:
		fh.write(','.join(str(_) for _ in random_list))

	flag = check_for_pairs(random_list,chosen_sum)

	random_list = [random.randint(-3,10) for _ in range(15)]
	testcase_chosen_sum = random.randint(1,10)

	testcase_flag = check_for_pairs(random_list,chosen_sum)

	desc = f"""<p>For this challenge you'll be given a list of integers. You will have to find all pairs of integers(meaning 2) that add up to the chosen sum value. Each item can only be used once. So once you use it, you should not use it again, as in the item at that index. The integers themselves may be repeated again throughout the list but you should only use each index once when you're creating your pairs.</p> <br />
<p> The flag will be in the format of {{ chosen_sum }};{{ a_pair }}{{ a_second_pair}}. This flag is an interview style question. You will find your testcase below.</p>
<h3> Testcase </h3><p> Given the list of integers below find all pairs that add up to the number {testcase_chosen_sum}. <span class="text-mono">{random_list} </span> <br /> Thus the flag would then be <span class="text-mono"> {testcase_flag}</span></p>
	"""

	return desc,flag