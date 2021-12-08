import requests
from collections import Counter
from nltk.corpus import stopwords
import threading
import json

## BOOKS
## Alice in Wonderland by Lewis Caroll
GUTENBERG_URI = "https://www.gutenberg.org/files/11/11-0.txt"
content_type = 'book'

## POEMS don't start until "SELECTED POEMS:" and have copywrite after Poems end
## Robert Frost Poem Collection
# GUTENBERG_URI = "https://www.gutenberg.org/files/59824/59824-0.txt"
# content_type = 'poem'

if content_type == 'book':
	startline = b'CHAPTER I'
	endline = b'END OF THE PROJECT GUTENBERG EBOOK'
elif content_type == 'poem':
	startline = b'SELECTED POEMS'
	endline = b'End of the P'
else:
	startline = ''
	endline = ''

## Variables always needed for Bag of Words
tokens = Counter()
STOP = stopwords.words("english")
STOP.append('the')

## GET the target (uri)
response = requests.get(GUTENBERG_URI, stream=True)
## if on windows must add:
response.encoding = "utf-8"

## quick load and make bag of words...

## chunks of 100000 bytes
## for chunk in response.iter_content(chunk_size=100000)

## streaming lines
## for curline in response.iter_lines()

def read_content():
	start_flag = True
	start_counter = 0
	end_flag = False

	for curline in response.iter_lines():
		if curline.strip(): # "" = false
			## Check if we are at start of poems
			if start_flag: 
				# skip this line until SELECTED POEMS
				if curline.startswith(startline):
					if start_counter == 1:
						start_flag = False
					else:
						start_counter = 1

			else:
				## We have started the Poems
				if not end_flag and not curline.startswith(endline):
					# we are officially only looking at Poems!
					for word in curline.lower().split():
						if word not in STOP:
							## decode and add word because not in STOP words
							tokens[word.decode()] += 1
				else:
					break

	with open("output.txt", "w") as text_file:
		text_file.write("Top Five Phrases:\n" + json.dumps(dict(Counter(tokens).most_common(5))))

threading.Thread(target=read_content).start()