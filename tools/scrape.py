#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""An executable package that scrapes adjective words from auswandern-schweiz.

This binary scrapes word audio files from the site and saves them to audio/ as
DE_CH.mp3.
"""
import csv
import logging
import re
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

def is_meta_row(tr_row) -> bool:
    return tr_row.find_all('td')[0].text == '\xa0'

def get_entry_from_entry_row(row) -> Tuple:
    tds = row.find_all("td")
    audio = tds[0].find('audio').attrs['src']
    ch = tds[1].text
    de = tds[2].text
    return (audio, ch, de)

def fetch_entries(src: str) -> List[Tuple]:
    response = requests.get(src)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, features='html.parser')
    entries_table = soup.find_all('table')[0]
    word_entry_rows = [row for row in entries_table.find_all('tr')
                       if not is_meta_row(row)]
    entries = [get_entry_from_entry_row(r) for r in word_entry_rows]
    return entries


HOST = 'https://www.auswandern-schweiz.net'

def fetch_audio(target: str) -> None:
    response = requests.get(HOST + '/mp3/' + target)
    response.raise_for_status()

    with open('audio/' + target, 'wb') as audio_file:
        audio_file.write(response.content)


def save_entries(entries: List) -> None:
    with open('audio/index.csv', 'w') as idx_file:
        fieldnames = ['mp3', 'ch', 'de']
        writer = csv.DictWriter(idx_file, fieldnames=fieldnames)
        writer.writeheader()
        for e in entries:
            audio_target = e[0][5:]
            fetch_audio(audio_target)
            writer.writerow({
                'mp3': audio_target,
                'ch': e[1],
                'de': e[2],
            })

SOURCES = [
    HOST
    + '/schweizer-kultur/schweizerdeutsch-woerterbuch/'
    + str(28 + idx)
    + '-schweizerdeutsch-'
    + suffix for (idx, suffix) in enumerate(['a-c', 'd-f', 'g-j', 'k-m', 'n-p', 'r-t', 'u-z'])]

def main():
    logging.basicConfig(filename='scrape.log', level=logging.INFO)
    entries = []
    for src in SOURCES:
        entries.extend(fetch_entries(src))
    save_entries(entries)
    return entries


if __name__ == "__main__":
    main()
