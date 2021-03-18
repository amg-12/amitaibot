#!/usr/bin/python2.7.6

import traceback
from random import *
from datetime import datetime

dolog = False
def log(x):
    x = str(x)
    if dolog:
        file = open('log.txt','a')
        file.write(x + '\n')
        file.close()
    print x

from wordnik import *
apiUrl = 'http://api.wordnik.com/v4'
apiKey = '[REDACTED]'
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)
wordsApi = WordsApi.WordsApi(client)

import requests
token = '[REDACTED]'
def publish(kind, message, url):
    response = requests.post('https://graph.facebook.com/me/' + kind, data=dict(access_token=token, message=message, url=url)).json()
    if 'id' in response:
        link = 'fb.com/' + response['id']
        log(link + ' at ' + str(datetime.now())[:-10])
        log('')
    else:
        log(response)
        log('')
    return link;

def rand(part):
    word = wordsApi.getRandomWord(includePartOfSpeech=part, minCorpusCount=randint(0, 200000), minLength=1).word
    return word;

def srand(part, s):
    defi = ''
    while not any(n in defi.lower() for n in s):
        word = rand(part)
        print word
        try:
            defi = wordApi.getDefinitions(word, partOfSpeech=part)[0].text
        except TypeError:
            print
    return word;

def nrand(part, s):
    while True:
        word = rand(part)
        print word
        try:
            defi = wordApi.getDefinitions(word, partOfSpeech=part)[0].text
        except TypeError:
            print
        if not(s.lower() in defi.lower()):
            return word;

def part(word):
    part = wordApi.getDefinitions(word=word, limit=1)
    return part[0].partOfSpeech;

import unicodedata
def asc(data):
    data = unicode(data)
    normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
    return normal;

from mtranslate import translate
'''
def translate(text, toLang):
    api_key = '[REDACTED]'
    result = requests.post('https://translation.googleapis.com/language/translate/v2', params={'key': api_key, 'q': text, 'target': toLang})
    return result.json()["data"]["translations"][0]["translatedText"];
'''

def correct(sentence):
    log(sentence)
    for i in range(2):
        sentence = translate(asc(sentence), 'es')
        sentence = translate(asc(sentence), 'en', 'es')
        log(sentence)
    return sentence;

from flickrapi import FlickrAPI
FLICKR_PUBLIC = '[REDACTED]'
FLICKR_SECRET = '[REDACTED]'
flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
def search(text):
    while text:
        photo = flickr.photos.search(text=text, per_page=1, extras='url_l', sort='interestingness-desc', content_type='1', media='photos')
        try:
            return photo['photos']['photo'][0]['url_l']
        except: pass
        words = text.split(' ')
        words.pop(randrange(len(words)))
        text = ' '.join(words)
        log(text)

from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO
def imagegen(sentence):
    url = search(sentence)
    response = requests.get(url)
    image = Image.open(StringIO(response.content))
    draw = ImageDraw.Draw(image)
    W, H = image.size
    fontsize = 1
    fraction = 0.8
    font = ImageFont.truetype('Comic Sans MS.ttf', fontsize)
    while font.getsize(sentence)[0] < fraction*W:
        fontsize += 1
        font = ImageFont.truetype('Comic Sans MS.ttf', fontsize)
    w, h = draw.textsize(sentence, font=font)
    x, y = ((W-w)/2), ((H-h)/2)
    shadowcolor = 'black'
    draw.text((x-2, y-2), sentence, font=font, fill=shadowcolor)
    draw.text((x+2, y-2), sentence, font=font, fill=shadowcolor)
    draw.text((x-2, y+2), sentence, font=font, fill=shadowcolor)
    draw.text((x+2, y+2), sentence, font=font, fill=shadowcolor)
    draw.text((x,y), sentence, fill="white", font=font)
    image.save('image.png', 'PNG')

def postimage(sentence):
    imagegen(sentence)
    files={'file': open('image.png','rb')}
    response = requests.post('https://graph.facebook.com/me/photos', data=dict(access_token=token), files=files).json()
    if 'id' in response:
        link = 'fb.com/' + response['id']
        log(link + ' at ' + str(datetime.now())[:-10])
        log('')
    else:
        log(response)

def run():
    try:
        sentence = choice(['a ', '']) + rand('noun') + ' ' + choice([rand('auxiliary-verb') + ' ', rand('auxiliary-verb') + ' ', '']) + choice(['be ', '']) + rand('verb') + choice([' a ', ' ']) + rand('noun') + '.'
        sentence = correct(sentence)
        try:
            postimage(sentence)
        except:
            log('Failed to generate image.')
            publish('feed', sentence, 'none')
    except Exception as e:
        log(traceback.format_exc(e))
        message = 'Failed to generate sentence. Posting a random Pokemon instead.'
        url = 'http://www.serebii.net/art/th/' + str(randint(1, 802)) + '.png'
        publish('photos', message, url)

def lose():
    token = '[REDACTED]'
    status = 'This is an automatic message. Followers of this page will now lose The Game every Wednesday at 13:37. <3'
    try:
        requests.post('https://graph.facebook.com/me/feed', data=dict(access_token=token, message=status)).json()
    except: pass
