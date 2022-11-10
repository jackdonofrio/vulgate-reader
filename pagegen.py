"""
Messy code..
I'll fix it later.

This is completely for fun.
"""

import csv
import os
import re
import sys



chapter_counts = {}
cached_numerals = {}
def dec_to_roman(n, cached_numerals):
    """
    Not programming D or M into this; bible chapters only
    go as high as ~150s (with Psalms)
    """
    numeral_map = {100 : "C", 90 : "XC", 50 : "L", 40 : "XL", 10 : "X", 9 : "IX", 5 : "V", 4 : "IV", 1 : "I"}

    if n in cached_numerals:
        return cached_numerals[n]
    result = ''
    v = n
    for d in numeral_map.keys():
        q = v // d
        result += (str(numeral_map[d]) * q)
        v -= (q * d)
    cached_numerals[n] = result
    return result



def pagify(chapter_data, chapter_number, book_name, chapter_counts):
    page = '''
    <html>
        <head>
            <style>
                body { 
                    font-family: monospace; 
                    text-align: left; 
                    margin-left: 30%;
                    margin-right: 30%; 
                    font-size: 150%;
                    }
                a {
                    text-decoration: inherit;
                  }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body><h4>Old Testament</h4><p>
        ''' 
    for book in chapter_counts.keys():
        if book == 'Matthew':
            page += "</p><h4>New Testament</h4><p>"
        if book == book_name:
            page += f'<b style="color:red">{book}</b>'
        else:
            page += f'<a href="https://jackdonofrio.github.io/vulgate-reader/vul/{book}/1">{book}</a>'
        page += (' * ' * (book != '2 Maccabees' and book != 'Revelation'))

    page += f'</p>{chapter_data}</body></html>'
    return page


def format_chapter(raw_text, chapter_number, book_name, chapter_counts, cached_numerals):
    roman_chapter_number = dec_to_roman(chapter_number, cached_numerals)
    chapter_data = f"<h3>{book_name} <b style='color: red' >{roman_chapter_number}</b></h3><p>"
    for c in range(1, int(chapter_counts[book_name]) + 1):
        if c == chapter_number:
            chapter_data += f'<b style="color: red">{c}</b> '
        else:
            chapter_data += f'<a href="https://jackdonofrio.github.io/vulgate-reader/vul/{book_name}/{c}">{c}</a>  '
    chapter_data += f"</p><p>{raw_text}</p>"
    return pagify(chapter_data, roman_chapter_number, book_name, chapter_counts)


translation = "vul"

base_dir = translation
if not os.path.exists(base_dir):
    os.mkdir(base_dir)

current_book = 'Genesis'
current_chapter_number = 1
current_chapter_text = ''
chapter_path = ''

def count_chapters(translation):
    # go through tsv before writing anything, just to get chapter counts
    # so that they can be used for navigation within pages
    counts = {}
    with open(f"{translation}.tsv") as file:
        row_data = csv.reader(file, delimiter="\t")
        for row in row_data:
            if len(row) < 6:
                print('not formatted correctly.', row)
                continue
            book_name = row[0]
            chapter_number = row[3]
            counts[book_name] = chapter_number
    return counts
chapter_counts = count_chapters(translation)

with open(f"{translation}.tsv") as file:
    row_data = csv.reader(file, delimiter="\t")
    for row in row_data:
        if len(row) < 6:
            print('not formatted correctly.', row)
            continue
        book_name = row[0]
        book_path = os.path.join(base_dir, current_book)
        if not os.path.exists(book_path):
            os.mkdir(book_path)
        chapter_number = row[3]
        chapter_path = os.path.join(book_path, f"{chapter_number}.html")

        if chapter_number != current_chapter_number or current_book != book_name:
            chapter_path = os.path.join(book_path, f"{current_chapter_number}.html")
            print(format_chapter(current_chapter_text, int(current_chapter_number), current_book,
                chapter_counts, cached_numerals), file=open(chapter_path, 'w'))
            current_chapter_text = ''
            current_chapter_number = chapter_number
            current_book = book_name

        verse_number = row[4]
        verse = row[5]
        verse = re.sub(r'[\[|\]]', r'', verse) # these appear throughout the source file
        verse = re.sub(r'[A-z]+',
                lambda match:  r'<a style="color: inherit;"  href="https://en.wiktionary.org/wiki/{}#Latin">{}</a>'.format(match.group(0).lower() if match.start() == 0 else match.group(0), match.group(0)), verse)

        current_chapter_text += f"<a style='color:red; font-weight:bold'  href='https://jackdonofrio.github.io/librum-apertum/{translation}/{current_book}/{current_chapter_number}/{verse_number}'>{verse_number}</a> {verse} "

