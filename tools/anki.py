#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A collection of utilities for adding cards to Anki's DB."""
from contextlib import closing
import csv
from pathlib import PosixPath
from itertools import chain
import os
from typing import Dict, List

from bs4 import BeautifulSoup as BS

import anki
import anki.storage

ANKI_DB = PosixPath('/home/grzesiek/Anki2/grzesiek/collection.anki2')
assert (ANKI_DB.is_file())
AUDIO = PosixPath('audio/').absolute()
assert (AUDIO.is_dir())
AUDIO_INDEX = AUDIO / 'index.csv'
assert (AUDIO_INDEX.is_file())

def load_index() -> List[Dict]:
    with open(AUDIO_INDEX, 'r') as f:
        return list(csv.DictReader(f))

def add_a_note(col: anki.collection._Collection, entry: Dict) -> None:
    basicfb = col.models.by_name('BasicFB')
    col.models.set_current(basicfb)
    ch_deck = col.decks.by_name('Foreign Languages::Swiss German::Schwiizerdütsch')

    note = col.newNote(forDeck=False)
    note.model()['did'] = ch_deck['id']
    audio_file = col.media.addFile(AUDIO / entry['mp3'])
    note.fields[0] = (
        '<div style="text-align: center;">' +
        entry['ch'] + '<br/>' +
        '[sound:{mp3}]'.format(mp3=entry['mp3']) +
        '</div>')
    note.fields[1] = (
        '<div style="text-align: center;">' +
        entry['de'] +
        '</div>')
    note.fields[2] = (
        '<div style="text-align: center;">' +
        '<a href="https://www.auswandern-schweiz.net/schweizer-kultur/schweizerdeutsch-woerterbuch/28-schweizerdeutsch-a-c">' +
        'auswandern-schweiz.net</a></div>')
    col.addNote(note)
    note.flush()

def open_my_collection() -> anki.collection._Collection:
    cwd = os.getcwd()
    try:
        return anki.storage.Collection(ANKI_DB)
    finally:
        # Opening an Anki Collection can have the inadvertent effect of
        # changing the PWD, so restore PWD afterwards.
        if cwd != os.getcwd():
            os.chdir(cwd)

def main():
    index = load_index()
    with closing(open_my_collection()) as col:
        for e in index:
            add_a_note(col, e)

if __name__ == '__main__':
    main()

