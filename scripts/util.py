
# Apoligies for the messy lambda function.
# It simply draws a certain number of spaces with a given indentation value.
def log_anything_prettily(logfunc,thingy,indent = 0, indentf = lambda i: ''.join(['  ' for x in range(i)])):
	""" A function that logs multidimentional lists/dictionaries recursively.

	Parameters:
		logfunc - a function that will be called for logging (ex: print)
		thingy - the thing to log (dictionary, list, etc)
		[indent] - indentation level to start at (used in recursion)
		[indentf] - function to generate indentation
	"""
	if isinstance(thingy, dict):
		logfunc(indentf(indent) + "[DICTIONARY]")
		for key in thingy:
			val = thingy[key]
			logfunc(indentf(indent) + str(key) + "==>")
			log_anything_prettily(logfunc,val,indent+1,indentf)
	elif isinstance(thingy,list):
		logfunc(indentf(indent) + "[LIST]")
		for val in thingy:
			log_anything_prettily(logfunc,val,indent+1,indentf)
	else:
		logfunc(indentf(indent) + str(thingy))

def reverse_lookup(d, v):
    """A function which does a reverse-lookup in a dictionary, given the
    value to lookup it returns the key.
    """
    for k in d:
        if d[k] == v:
            return k
    raise ValueError


def convert_date(date_tup):
    """A function which converts a tuple with the the date in the format
    ('Jan', '09', '2012') and returns a string in the format "2012-01-09"
    """
    # Map each month to its numeric representation
    months = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05',
              'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10',
              'nov': '11', 'dec': '12'}

    return date_tup[2] + '-' + months[date_tup[0].lower()] + '-' + date_tup[1]


def convert_time(time):
    """A function which converts time from the AM/PM tuple format ('2:40', 'pm')
    into military time 14:40:00.
    """
    # Split the time up into hours and minutes
    (hour, minute) = time[0].split(':')
    military_time = ""

    # I hate doing this, there must be a library FFS
    if hour == '12' and time[1].lower() == 'pm':
        military_time = hour + ':' + minute + ':' + '00'
    elif hour == '12' and minute == '00' and time[1].lower() == 'am':
        military_time = '24' + ':' + '00' + ':' + '00'
    elif hour == '12' and time[1].lower() == 'am':
        military_time = '24' + ':' + minute + ':' + '00'
    elif time[1].lower() == 'pm':
        # Add 12 hours to the time
        hour = str(int(hour) + 12)  # Why can't python do simple addition of int and string like ruby
        military_time = hour + ':' + minute + ':' + '00'
    elif time[1].lower() == 'am':
        # Add a leading 0 for single digit time
        if len(hour) == 1:
            hour = '0' + hour
        military_time = hour + ':' + minute + ':' + '00'

    return military_time


def generate_dictionary(file_name, delim):
    """A function which parses a file of keys and values based on the delimiter
    sepcifed and returns a dicitionary with the corresponding key/value pairs.
    """
    dictionary = {}

    print file_name
    # Populate the dictionary
    with open(file_name) as f:
        for line in f:
            (k, v) = line.split(delim)
            dictionary[k] = v.strip()

    return dictionary
