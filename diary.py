#!/usr/bin/python
import sys, os, datetime, glob, re, calendar
from subprocess import call

# Set this to something if you wish to use truecrypt
TRUECRYPT_VOLUME = ""
# If using truecrypt ensure this points to the truecrypt mounted folder
# Diary config file: Mine says '~/Dropbox/My Notes/'
DIARY_CONFIG_FILE = os.path.expanduser('~/.diary')
try:
    DIARY_CONFIG = map(str.strip, open(DIARY_CONFIG_FILE).readlines())
except IOError:
    DIARY_CONFIG = ['']
DIARY_FOLDER = os.path.expanduser(DIARY_CONFIG[0])
EDITOR = os.environ.get('EDITOR','vim')

ED_ENABLED = False
if len(EDITOR) > 0:
	ED_ENABLED = True

TRUECRYPT_ENABLED = False
if len(TRUECRYPT_VOLUME) > 0:
	TRUECRYPT_BINARY = os.popen("which truecrypt").read().rstrip('\n')
	if TRUECRYPT_BINARY != 0 and len(TRUECRYPT_BINARY) > 0:
		TRUECRYPT_ENABLED = True

NOW = datetime.datetime.now()

#Handles arguments a function calls
def main():
	if TRUECRYPT_ENABLED:
		mount_truecrypt()

	if not diary_folder_exists():
		print("Please specify a valid diary folder, using a config file at "
              "~/.diary")
		return

	action = ''
	argument = ''

	if len(sys.argv) >= 2:
		action=sys.argv[1]
	if len(sys.argv) >= 3:
		argument=sys.argv[2]
	else:
		argument=None

	{'add': add,
			'ls': list,
			'find': d_search,
			'help': help,
			'hide': dismount_truecrypt,
			'edit': edit,
			'rand': random,
			'stats': stats,
			}.get(action, help)(argument)

def mount_truecrypt():
	if not diary_folder_exists():
		os.popen('%s %s' % (TRUECRYPT_BINARY, TRUECRYPT_VOLUME)).read()

def resolve_date(diary_date=None):
	todays_diary = datetime.date.today().strftime("%Y-%m-%d") + ".txt"
	if diary_date==None:
		return datetime.date.today().strftime("%Y-%m-%d")
	elif diary_date=='yes':
		return datetime.date.today().strftime("%Y-%m-%d")

def dismount_truecrypt(arg):
	if diary_folder_exists():
		os.popen('%s %s -d' % (TRUECRYPT_BINARY, TRUECRYPT_VOLUME))

#Add a diary entry via the text supplied
def add(text):
	todays_diary = 'Journal ' + datetime.date.today().strftime("%Y-%m-%d") + ".txt"
	with open(get_diary_folder()+todays_diary, "a") as today:
		today.write(text+"\n")
		print("Added diary entry")

def random(text):
	file_list = glob.glob(os.path.join(get_diary_folder(), '*.txt'))
	file_list.sort()
	from random import choice
	random_date = choice(file_list)
	if os.path.isfile(random_date):
		diary_file = open(random_date,'r').read()
		print(random_date)
		print(diary_file)
	else:
		print('No diary entry specified and no entries for today')

#Edit a diary entry via the text supplied
def edit(diary_date=None):
	todays_diary = 'Journal ' + datetime.date.today().strftime("%Y-%m-%d") + ".txt"
	if diary_date==None:
		diary_date = datetime.date.today().strftime("%Y-%m-%d")

	abs_file = get_diary_folder() + 'Journal ' + diary_date + ".txt"
	call([EDITOR, abs_file])


#List a specific date or today
def list(diary_date=None):
	"""List all elements for a specific date"""
	if diary_date==None:
		diary_date = datetime.date.today().strftime("%Y-%m-%d")

	abs_file = get_diary_folder() + 'Journal ' + diary_date + ".txt"
	if os.path.isfile(abs_file):
		diary_file = open(abs_file,'r').read()
		print(diary_file)
	else:
		print('No diary entry specified and no entries for today')

#Search all files for a supplied pattern
def d_search(pattern):
	file_list = glob.glob(os.path.join(get_diary_folder(), '*.txt'))
	file_list.sort()
	for infile in file_list:
		file = open(infile,"r")
		text = file.read()
		file.close()
		index = text.find(pattern)
		if index > 0:
			search_file(infile, pattern, text)

#Build up stats by month and year
def stats(text):
	file_list = glob.glob(os.path.join(get_diary_folder(), '*.txt'))
	file_list.sort()
	ordered_list = {}
	for infile in file_list:
		abs_list = re.split('/',infile)
		date = re.split('-', abs_list[-1][8:-4])
		file = open(infile,"r")
		text = file.read()
		tempwords = text.split(None)

		if int(date[0]) in ordered_list:
			if int(date[1]) in ordered_list[int(date[0])]:
				ordered_list[int(date[0])][int(date[1])] += len(tempwords)
			else:
				ordered_list[int(date[0])][int(date[1])] = len(tempwords)
		else:
			ordered_list[int(date[0])] = {}
			ordered_list[int(date[0])][int(date[1])] = len(tempwords)
	years = sorted(ordered_list.iteritems())
	print("Word Count By Month\n")
	for year in years:
		for month in year:
			if isinstance(month, int):
				print("%d" % month)
			elif isinstance(month, dict):
				for date, word_count in month.iteritems():
					print("%s" % calendar.month_abbr[date], word_count)




#Searches the specific file for text
def search_file(infile, pattern, text):
	file_name = infile.split('/')
	lines = text.split('\n')
	for line in lines:
		index = line.find(pattern)
		if index > 0:
			print ("%s -- %s" % (file_name[-1], line))

def get_diary_folder():
	if DIARY_FOLDER:
		if DIARY_FOLDER[-1] == '/':
			return DIARY_FOLDER
		return DIARY_FOLDER + '/'
	return False

def diary_folder_exists():
	if get_diary_folder() != False:
		return os.path.isdir(get_diary_folder())
	return False

def help(argument):
	print("Usage:")
	print("\tdiary.py add 'Today I went to the @shops and bought some cake for the #party'")
	print("\tdiary.py find 'search term'")
	print("\tdiary.py ls - Lists current day or date format specified")
	print("\tdiary.py help - Displays this text")
	print("\tdiary.py hide - Will unmount the truecrypt volume")
	print("\tdiary.py edit - Edits current day or date specificed in format")
	print("\tdiary.py rand - Returns random element")
	print("\tdiary.py stats - Prints monthly word-count of stats")

if __name__ == '__main__':
	main()
