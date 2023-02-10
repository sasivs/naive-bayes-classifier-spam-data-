import re
import string
import nltk

stop_words = set(nltk.corpus.stopwords.words('english'))
from nltk.stem import PorterStemmer
stemmer= PorterStemmer()
from nltk.stem import WordNetLemmatizer
lemmatizer=WordNetLemmatizer()

file = open("SMSSpamCollection", 'r')
word_count = {}
word_count_target={'spam':{}, 'ham':{}}
spam = 0
ham = 0
lines = len(file.readlines())
file.close()
test = int(lines*0.3)
train = lines-test
spam_lines = 0
file = open('SMSSpamCollection', 'r')
for _ in range(train):
    line = file.readline().strip().lower()
    if not line:
        continue
    line = re.sub(r'\d+', '', line)
    line = line.translate(line.maketrans("","",string.punctuation))
    line = line.split()
    target = line.pop(0)
    line = set(line)-stop_words
    line = [lemmatizer.lemmatize(stemmer.stem(word)) for word in line]
    if target == 'spam':
        spam_lines += 1
    for word in line:
        word = word.strip()
        if word in word_count.keys():
            word_count[word] += 1
        else:
            word_count[word] = 1
        if target=='spam':
            if word in word_count_target['spam'].keys():
                word_count_target['spam'][word] += 1
            else:
                word_count_target['spam'][word] = 1
        else:
            if word in word_count_target['ham'].keys():
                word_count_target['ham'][word] += 1
            else:
                word_count_target['ham'][word] = 1

total_words = sum(word_count.values())
word_prob = {key:value/total_words for key, value in word_count.items()}

total_spam_words = sum(word_count_target['spam'].values())
total_ham_words = total_words-total_spam_words
word_target_prob = {'spam':{key:value/total_spam_words for key, value in word_count_target['spam'].items()}, \
                        'ham':{key:value/total_ham_words for key,value in word_count_target['ham'].items()}}

distinct_spam_words = len(word_count_target['spam'].keys())
distinct_ham_words = len(word_count_target['ham'].keys())
stat_spam_prob = spam_lines/lines
stat_ham_prob = 1-stat_spam_prob

correct = 0
for _ in range(test):
    line = file.readline().strip().lower()
    if not line:
        continue
    line = re.sub(r'\d+', '', line)
    line = line.translate(line.maketrans("","",string.punctuation))
    line = line.split()
    target = line.pop(0)
    line = set(line)-stop_words
    line = [lemmatizer.lemmatize(stemmer.stem(word)) for word in line]
    ham_prob = stat_ham_prob
    spam_prob = stat_spam_prob
    s_words = distinct_spam_words
    h_words = distinct_ham_words
    for word in line:
        if word not in word_target_prob['spam'].keys():
            s_words += 1
        if word not in word_target_prob['ham'].keys():
            h_words += 1
    for word in line:
        word = word.strip()
        if word in word_target_prob['spam'].keys():
            spam_prob *= (word_target_prob['spam'][word] + (1/s_words))
        else:
            spam_prob *= (1/s_words)
        if word in word_target_prob['ham'].keys():
            ham_prob *= (word_target_prob['ham'][word] + (1/h_words))
        else:
            ham_prob *= (1/h_words)
    if (spam_prob/(spam_prob+ham_prob)) > 0.5:
        if target == 'spam':
            correct += 1
    elif target == 'ham':
        correct += 1
print(correct*100/test)