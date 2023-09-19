# 1. (30 points) Using Python's hashlib library, find a meaningful English word whose ASCII encoding has the following SHA-256 hex digest:

# 69d8c7575198a63bc8d97306e80c26e04015a9afdb92a699adaaac0b51570de7

# Hint: use hashlib.sha256(word.encode("ascii", "ignore")).hexdigest() to get the hex digest of the ASCII encoding of a given word. List of all meaningful English words is here. See the following video giving you some help for Q1 and Q3:

import hashlib

f = open("dict.txt", 'r')

words = f.readlines()
stripped_words = []
for word in words:
    stripped_words.append(word[:-1])  
i = 0
target = "69d8c7575198a63bc8d97306e80c26e04015a9afdb92a699adaaac0b51570de7"

for word in stripped_words:
    if target == str(hashlib.sha256(word.encode("ascii", "ignore")).hexdigest()):
        print(word)
        break
    i += 1
    if i % 1000 == 0:
        print(i)
f.close()

