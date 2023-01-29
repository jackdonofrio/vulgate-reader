import csv
import string
import re

verses = set()

def update_frequency(verse, frequency_table):
    # remove all punctuation, double spaces, turn to lower case
    if verse in verses: # not sure why, but verses are getting added three times to the table.
        return          # probably because i did something dumb somewhere.
    verses.add(verse)
    # right bracket in psalms - replace with space
    cleaned_verse = re.sub('>', ' ', verse)
    # otherwise, replace punctuation with empty char
    cleaned_verse = re.sub('  ', ' ', cleaned_verse.translate(str.maketrans('', '', string.punctuation))).strip().lower()
    for word in cleaned_verse.split(' '):
        if word not in frequency_table.keys():
            frequency_table[word] = 0
        frequency_table[word] += 1

filename = "vulgate.tsv"

frequency = {} # maps word, naively, to how many times it appears
               # a more intelligent approach would also use part of speech
               # and group words by common stems

book_frequencies = {} # table of frequency tables for each book

with open(filename) as file:
    row_data = csv.reader(file, delimiter="\t")
    for row in row_data:
        # print(row)
        if len(row) < 6:
            print('not formatted correctly:', row)
            continue
        book = row[0]
        if book not in book_frequencies:
            book_frequencies[book] = {}
        verse = row[5]
        update_frequency(verse, book_frequencies[book])

def generate_zipf_table(freq_table):
    """
    assuming list is sorted-desc
    """
    zipf = {}
    most_common = list(freq_table.values())[0]
    for word in freq_table:
        zipf[word] = round(freq_table[word] / most_common, 3)
    return zipf


# sort freqs in each book
for book in book_frequencies.keys():
    book_frequencies[book] = dict(sorted(book_frequencies[book].items(), key=lambda item: item[1])[::-1])

# calculate zipf ratios
zipf_ratios = {}
for book in book_frequencies.keys():
    if book not in zipf_ratios.keys():
        zipf_ratios[book] = {}
    zipf_ratios[book] = generate_zipf_table(book_frequencies[book])
    # most_common = list(book_frequencies[book].values())[0]
    # for word in list(book_frequencies[book]):
    #     zipf_ratios[book][word] = round(book_frequencies[book][word] / most_common, 3)

# find words unique to each book
unique_per_book = {}
for book in book_frequencies.keys():
    for word in book_frequencies[book].keys():
        # check if this word is in any other book
        if all([word not in book_frequencies[other_book].keys() for other_book in set(book_frequencies.keys()).difference([book])]):
            if book not in unique_per_book.keys():
               unique_per_book[book] = {}
            unique_per_book[book][word] = book_frequencies[book][word]
    unique_per_book[book] = dict(sorted(unique_per_book[book].items(), key=lambda item: item[1])[::-1])

# display
for book in book_frequencies.keys():
    # print("top 10 words for", book)
    # print("%14s  %14s  %14s" % ("word", "frequency", "zipf ratio"))
    # for word in list(book_frequencies[book])[:10]:
    #     print("%14s  %14s  %14s" % (word, book_frequencies[book][word], zipf_ratios[book][word]))
    unique_count = len(list(unique_per_book[book].keys()))
    # not taking frequency into account, just proportion of uniques within set of all words used
    allword_count = len(list(book_frequencies[book].keys())) 
    print("# of words that are unique to", book, ":", unique_count)
    print("proportion of words used in", book, "unique to", book, ":", round(unique_count / allword_count, 3))
    print("top 10 unique words in", book)
    print("%18s %10s" % ("word", "freq"))
    for word in list(unique_per_book[book].keys())[:40]:
        print("%18s %10s" % (word, unique_per_book[book][word]))
    print()


# totals
total_freqs = {}
for book in book_frequencies:
    for word in book_frequencies[book]:
        if word not in total_freqs:
            total_freqs[word] = 0
        total_freqs[word] += book_frequencies[book][word]


top_n = 500
min_len = 1
print("top", top_n, "total words longer than", min_len, "letters")
total_freqs = dict(sorted(filter(lambda x : len(x[0]) >= min_len, total_freqs.items()), key=lambda item: item[1])[::-1])
total_zipf_table = generate_zipf_table(total_freqs)
print("%14s %14s %14s %14s" % ("word", "freq", "zipf ratio", "1 / rank"))
print("=" * 60)
for e, word in enumerate(list(total_freqs)[:top_n]):
    print("%14s %14s %14s %14s" % (word, total_freqs[word], total_zipf_table[word], round(1 / (e + 1), 3)))


