# utils.py

import re

def process_extracted_text(text):
    # Dummy example of processing OCR text for name, college, UID
    data = {
        'name': None,
        'college': None,
        'UID': None
    }

    # Example of extracting name, college, and UID using regex or string matching
    name_match = re.search(r'Name: (\w+ \w+)', text)  # Adjust this regex to your needs
    college_match = re.search(r'College: ([\w\s]+)', text)
    uid_match = re.search(r'UID: (\d+)', text)
    print(name_match, college_match, uid_match)
    if name_match:
        data['name'] = name_match.group(1)
    if college_match:
        data['college'] = college_match.group(1)
    if uid_match:
        data['UID'] = uid_match.group(1)

    return data