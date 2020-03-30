import warnings
warnings.filterwarnings('ignore')

import re, textwrap
import feedparser
import pandas as pd
from mlflow import pyfunc

from bs4 import BeautifulSoup
from html.parser import HTMLParser
from urllib.request import Request, urlopen


model = pyfunc.load_model('models/textrank')

reSubs = [
  (r'\xa0', ' '),    # replace incorrect spaces
  (r'\.\.\.', '…')   # replace '...' with '…'; periods mistaken as a sentence
]


class TagRemover(HTMLParser):
  def __init__(self):
    super().__init__()
    self.data = ''

  def handle_data(self, data):
    self.data += data

  def parse(self, text):
    self.data = ''
    self.feed(text)
    return self.data


def get_soup(url):
  req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  html = urlopen(req).read().decode('utf8')
  soup = BeautifulSoup(html, 'html.parser')
  return soup


def process_soup(soup, soupTgts, join='\n\n'):
  story = []
  # Add elements from each target to story elements
  for tgt in soupTgts:
    element = soup
    tgt_len = len(tgt)
    for i, query in enumerate(tgt,1):
      if i == tgt_len:
        story += element.find_all(*query)
      else:
        element = element.find(*query)

  for sub in reSubs:
    story = [re.sub(sub[0], sub[1], str(p)) for p in story]
  story = (TagRemover().parse(p) for p in story)
  story = (p.strip() for p in story)
  story = list(story)
  return join.join(story), story


def wrap(text, width):
  out = []
  for p in text.split('\n'):
    out.append(textwrap.fill(p, width))
  return '\n'.join(out)


def truncate(text, width):
  return text if len(text)<=width else text[:width-3]+'...'


def summarize(texts, model=model, mode='sentences', length=3):
  isstr = type(texts) is str
  if isstr:  texts = [texts]
  n = len(texts)

  data = pd.DataFrame({'text': texts, 'mode':[mode]*n, 'length':[length]*n})
  summaries = model.predict(data)
  return summaries[0] if isstr else summaries


def parse_soup_tgts(tgts_str):
  tgts_str = tgts_str.strip()

  notclosedby = lambda s, c: s[0]!=c[0] or s[-1]!=c[1]

  # Outer square bracket
  if notclosedby(tgts_str, '[]'):  return None
  else:
    tgts_str = tgts_str[1:-1].strip()

  # Inner square brackets
  tgts = re.findall(r'\[.*?\]', tgts_str)
  tgts = [re.findall(r'\(.*?\)', tgt) for tgt in tgts]

  def parse_path(pathstr):
    parts = pathstr[1:-1].strip().split(',')

    tag = parts[0].strip()
    if notclosedby(tag, "''"):  return None
    tag = tag[1:-1]

    attr = [p.strip() for p in parts[1:]]
    if attr[0]=='':  return (tag,)

    if attr[0][0]!='{' or attr[-1][-1]!='}':  return None
    attr[0] = attr[0][1:]
    attr[-1] = attr[-1][:-1]

    # work through each key-value pair in attributes
    attr_ = dict()
    for kv in attr:
      kv_ = []
      for s in kv.split(':'):
        s = s.strip()
        if notclosedby(s, "''"):  return None
        kv_.append(s[1:-1])
      attr_[kv_[0]] = kv_[1]
    return (tag, attr_)

  tgts = [[parse_path(p) for p in tgt] for tgt in tgts]
  success = not any([any([p is None for p in tgt]) for tgt in tgts])
  return tgts if success else None


def rss_summarize(rss, model=model, mode='sentences', length=3, tWidth=70, aLim=5):
  texts = {k: [] for k in rss}
  entries = texts.copy()
  for k, v in rss.items():
    feed = feedparser.parse(v['url'])
    entries[k] = feed.entries[:aLim]
    for entry in entries[k]:
      soup = get_soup(entry.link)
      text, story = process_soup(soup, v['tgts'])
      texts[k].append(text)

  out = []
  for k, v in rss.items():
    out.append('='*tWidth)
    h = f'{k.upper()} - ' if (type(k) is str) else ''
    out.append(truncate(h+f'{v["url"]}', tWidth-5))
    out.append('='*tWidth)

    for text, entry in zip(texts[k], entries[k]):
      summary = summarize(text, model=model, mode=mode, length=length)

      out.append('-'*tWidth)
      out.append(truncate(entry.title, tWidth-5))
      out.append(truncate(entry.link, tWidth))
      out.append('-'*tWidth)
      out.append(wrap(summary, tWidth))
      out.append('')
    out.append('\n')

  return '\n'.join(out)


if __name__ == '__main__':
  rss ={
    'cbc-tech': {
      'url': 'https://www.cbc.ca/cmlink/rss-technology',
      'tgts': [ [('div', {'class': 'story'}), ('p',)] ],
    },
    'med-tds': {
      'url': 'https://medium.com/feed/towards-data-science',
      'tgts': [ [('p', {'data-selectable-paragraph': ''})] ],
    }
  }

  test_tgts = "[ [('div', {'class': 'story'}), ('p',)] ]"
  rss['cbc-tech']['tgts'] = parse_soup_tgts(test_tgts)

  rss = {1: rss['cbc-tech']}

  if True:
    print(rss_summarize(rss, tWidth=70, aLim=2))