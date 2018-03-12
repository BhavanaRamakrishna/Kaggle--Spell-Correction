import re
import csv
from Levenshtein import distance

'''

This code mainly uses the edit distance and a dictionary match on the incorrect words. First, the spell-errors file has been parsed to 
form a dictionary of {misspelt_word: [list of correct words]}. Another dictionary has been created to store the probability counts of 
every word in the big.txt file and count_1w.txt. The main approach while parsing the test.csv file is to first check if the misspelt word
has occured in the first dictionary. If it has then fetch the array of correct words and choose the word with the least Levenshtein distance.
However, if it does not appear in the dictionary, calculate the possible edits with distance 2 of the incorrect word and fetch the one with
the maximum probability using p(w|x) = p(x|w)*p(w). The final output is stored in the desired format in test_submit.csv.

'''

#Opens all the required files for processing
bigFile = open('C:\\Users\\Niru Suresh\\.kaggle\\competitions\\spell-checker-nyu-cds\\big.txt','r')
testFile = open('C:\\Users\\Niru Suresh\\.kaggle\\competitions\\spell-checker-nyu-cds\\test.csv','r')
outputFile = open('C:\\Users\\Niru Suresh\\.kaggle\\competitions\\spell-checker-nyu-cds\\test_submi..csv','w')
possibleCorrections = open('C:\\Users\\Niru Suresh\\.kaggle\\competitions\\spell-checker-nyu-cds\\spell-errors.txt','r')
count1 = open('C:\\Users\\Niru Suresh\\.kaggle\\competitions\\spell-checker-nyu-cds\\count_1w.txt','r')
count2 = open('C:\\Users\\Niru Suresh\\.kaggle\\competitions\\spell-checker-nyu-cds\\count_2w.txt','r')

#Regular expression to get all the words in a given text data
def words(data):
	return re.findall(r'\w+', data.lower())

#Builds a dictionary of words from big.txt and computes their probabilities
def getCountProb():
	readBig = words(bigFile.read())
	count = {}
	for word in readBig:
		if word in count:
			count[word] += 1
		else:
			count[word] = 1
	count11 = csv.reader(count1, delimiter='\t')
	for row in count11:
		if row[0].lower() in count:
			count[row[0].lower()] += int(row[1])
		else:
			count[row[0].lower()] = int(row[1])
	total = sum(count.values())
	for key in count:
		count[key] = float((count[key]+0.5)/(total+ 0.5*len(count)))
	return count

#Builds a dictionary from the misspelt words with key = misspelt word and value = [correct words]
def wordsDict():
	misspeltWords = {}
	readErrors = csv.reader(possibleCorrections, delimiter=':')
	for row in readErrors:
		correctWord, miss = row
		for word in miss.split(',',-1):
			word = re.sub('[^A-Za-z]','',word).lower().strip()
			if word in misspeltWords:
				misspeltWords[word].append(correctWord.strip())
			else:
				misspeltWords[word] = [correctWord.strip()]
	return misspeltWords

#Returns a set of words with edit distance 1 by transposing, deleting, replacing and inserting
def editDistance1(word):
	letters = 'abcdefghijklmnopqrstuvwxyz'
	splits = []
	for i in range(len(word)+1):
		splits.append((word[:i], word[i:]))
	deletes = []
	transposes = []
	replaces = []
	inserts = []
	for a,b in splits:
		deletes.append(a+b[1:])
		if len(b) > 1:
			transposes.append(a + b[1] + b[0] + b[2:])
		for c in letters:
			replaces.append(a + c + b[1:])
			inserts.append(a + c + b)
	return set(deletes + inserts + replaces + transposes)

'''Returns a set of words with edit distance 2 by first calling edit distance 1 and 
performing edit distance 1 again on the resulting words'''
def editDistance2(word):
	e1 = editDistance1(word)
	e2 = set()
	e2.update(e1)
	for w in e1:
		e2.update(editDistance1(w))
	return set(e1)

if __name__ == '__main__':
	count = getCountProb()
	readTest = csv.reader(testFile, delimiter=',')
	listOfWords = []
	words = wordsDict()
	i = 0
	outputFile.write("ID,CORRECT\n")
	for row in readTest:
		if i == 0 :
			i += 1
			continue
		if row[1].lower() in words.keys():
			wordarr = words[row[1].lower()]
			if len(wordarr) == 1:
				outputFile.write(str(i-1) + "," + wordarr[0].strip().lower() + "\n")

			else:
				p = 999.0
				finalw = ""
				for w in wordarr:
					newp = distance(w,row[1].lower())
					if newp < p:
						p = newp
						finalw = w
				outputFile.write(str(i-1) + "," + finalw.strip().lower() + "\n")
			i+= 1
		else:
			e1 = editDistance2(row[1].lower())
			maxprob = -1
			for e in e1:
				#p(x|w)*p(w)
				if e in count.keys():
					prob = float(distance(e,row[1].lower())*count[e])
					if prob > maxprob:
						maxprob = prob
						maxsim = e
			outputFile.write(str(i-1) + "," +  maxsim + "\n")
			i += 1    