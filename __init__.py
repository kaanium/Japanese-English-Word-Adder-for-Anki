import anki
import bs4
import requests
from anki import hooks
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, qconnect
import concurrent.futures

max_threads = 10000


def jisho_function(i):
    card = mw.col.getCard(i)
    note = card.note()
    try:
        value = note["Notes"]
    except:
        return
    if not ("," in value or value == ""):
        link = 'https://jisho.org/word/' + value
        try:
            res = requests.get(link)
        except:
            return
        try:
            res.raise_for_status()
        except:
            return
        found = bs4.BeautifulSoup(res.text, 'html.parser')
        try:
            a = found.select('.meaning-meaning')
        except:
            return
        if note["Reading"] == "":
            for j in a:
                note["Reading"] += (j.text + " || ")
            mw.col.update_note(note)


def threads():
    ids = mw.col.find_cards("tag:test")
    threads_amount = min(max_threads, len(ids))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads_amount) as executor:
        executor.map(jisho_function, ids)


action = QAction("Jisho", mw)
qconnect(action.triggered, threads)
mw.form.menuTools.addAction(action)
