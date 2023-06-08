from pdfminer.high_level import extract_pages, extract_text
import re
import os

filename = 'Profile (5).pdf'
filedir = os.path.join('dataset', filename)

text = extract_text(filedir)
print(text)

pattern = re.compile(r'[A-Z][a-z.]+ [A-Z][a-z.]+')
matches = pattern.findall(text)
print(matches)

