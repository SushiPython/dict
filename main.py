import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, request
import os
from random_words import RandomWords
from wiktionaryparser import WiktionaryParser
parser = WiktionaryParser()

r = RandomWords()

merriamKey = os.getenv('merriam')

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == "POST":
        return redirect(f'/word/{request.form["word"]}')
    if request.method == "GET":
        word = r.random_word()
        return render_template('index.html', rW=word)


@app.route('/proxy')
def proxy():
    word = request.args.get('word')
    if isinstance(word, type(None)):
        print(word)
        return redirect('/', 302)
    else:
        return redirect(f'/word/{word}', 302)


@app.route('/word/<word>')
def word(word):
    page = requests.get(f"https://www.dictionary.com/browse/{word}?s=t")
    page2 = requests.get(f"https://www.vocabulary.com/dictionary/{word}")
    merriam = requests.get(
        f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={merriamKey}"
    )

    soup = BeautifulSoup(page.content, 'html.parser')
    soup2 = BeautifulSoup(page2.content, 'html.parser')

    merriam = merriam.json()
    try:
        merriam = (merriam[0]['shortdef'][0])
    except:
        merriam = "Definition Not Found."
    wiki = (parser.fetch(word))
    tag = soup.find("span", class_="one-click-content css-1p89gle e1q3nk1v4")
    tag2 = soup2.find("p", class_="long")

    try:
        dictionaryDefine = (tag.get_text())
    except:
        dictionaryDefine = "Definition Not Found."

    try:
        vocabDefine = (tag2.get_text()).replace('â€™', "'")
    except:
        vocabDefine = "Definition Not Found."

    try:
        pos = wiki[0]['definitions'][0]['partOfSpeech']
    except:
        pos = 'POS Not Found'

    try:
        pronunc = wiki[0]['pronunciations']['text'][0]
    except:
        pronunc = 'Pronunciation not found.'

    try:
        audio = f"http:{wiki[0]['pronunciations']['audio'][0]}"
    except:
        audio = '/static/not-found.mp3'

    try:
        wikidef = wiki[0]['definitions'][0]['text'][1]
    except:
        wikidef = 'Definition not found.'

    try:
        etymology = wiki[0]['etymology']
    except:
        etymology = 'Etymology not found.'

    return render_template(
        'word.html',
        word=word.capitalize(),
        dictionaryDefine=dictionaryDefine,
        merriam=merriam,
        vocabDefine=vocabDefine,
        pronunc=pronunc,
        wikidef=wikidef,
        pos=pos,
        audio=audio,
        etymology=etymology)


app.run(host='0.0.0.0', port=5050)
