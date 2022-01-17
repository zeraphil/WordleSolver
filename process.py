import os
import json
import csv


f = open('vocab.json')
j = json.load(f)
vocab = j["solutions"] + j["herrings"]

vocab_freq = dict.fromkeys(vocab, 0)

f = open('unigram_freq.csv')
csvread = csv.reader(f, delimiter=',')
for row in csvread:
    print(row)
    if row[0] in vocab_freq.keys():
        vocab_freq[row[0]] = int(row[1])


with open('vocab_freq.json', 'w') as outfile:
    outfile.write(json.dumps(vocab_freq))