import csv
from collections import defaultdict

from urllib.request import urlopen
from lxml import etree
from io import TextIOWrapper
import re

import json

def get_tree(path):
    with urlopen(path) as response:
        xml = TextIOWrapper(response, encoding='utf-8')
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8', no_network=False)
        textXML = xml.read().replace('&twodotPM;', '⁚')
        return etree.fromstring(bytes(bytearray(textXML, encoding='utf-8')), parser)


vocab = {'dipl': defaultdict(list),
         'norm': defaultdict(list),
         'facs': defaultdict(list)}

with open('./data/menota.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for i in range(1):
        next(spamreader)
    for row in spamreader:
        tree = get_tree(row[-1])
        pages = tree.find('./{http://www.tei-c.org/ns/1.0}text').find('./{http://www.tei-c.org/ns/1.0}body').findall('.//{http://www.tei-c.org/ns/1.0}p')
        facs = ''
        dipl = ''
        norm = ''
        lemma = ''
        title = tree.find('{http://www.tei-c.org/ns/1.0}teiHeader').find('{http://www.tei-c.org/ns/1.0}fileDesc').find('{http://www.tei-c.org/ns/1.0}titleStmt').find('{http://www.tei-c.org/ns/1.0}title').text
        title = re.sub(r'(:|/|\\|\)|\(|,|\.)+', '-', title)
        title = re.sub(r'\s+', '_', title).replace(' ', '_').replace(':', '').replace('_-_', '-')
        print(title)
        for page in pages:
            # print('\tPage '+page.text)
            for e in page.findall('*'):
                l = None
                if e.get('lemma') is not None:
                    l = e.get('lemma')
                    lemma += l + ' '
                f = e.find('.//{http://www.menota.org/ns/1.0}facs')
                if f is not None and f.itertext() is not None:
                    w = ''.join(f.itertext()).strip()
                    facs += w + ' '
                    if l is not None and w not in vocab['facs'][l]:
                        vocab['facs'][l].append(w)
                d = e.find('.//{http://www.menota.org/ns/1.0}dipl')
                if d is not None and d.itertext() is not None:
                    w = ''.join(d.itertext()).strip()
                    dipl += w + ' '
                    if l is not None and w not in vocab['dipl'][l]:
                        vocab['dipl'][l].append(w)
                n = e.find('.//{http://www.menota.org/ns/1.0}norm')
                if n is not None and n.itertext() is not None:
                    w = ''.join(n.itertext()).strip()
                    norm += w + ' '
                    if l is not None and w not in vocab['norm'][l]:
                        vocab['norm'][l].append(w)

        if len(facs):
            with open(f'./data/out/texts/{title}_facs.txt', 'w', encoding='utf8') as f:
                f.write(facs)
        if len(dipl):
            with open(f'./data/out/texts/{title}_dipl.txt', 'w', encoding='utf8') as f:
                f.write(dipl)
        if len(norm):
            with open(f'./data/out/texts/{title}_norm.txt', 'w', encoding='utf8') as f:
                f.write(norm)
with open('./data/out/vocab/norm.json', 'w', encoding='utf8') as f:
    json.dump(dict(vocab['norm']), f)

with open('./data/out/vocab/dipl.json', 'w', encoding='utf8') as f:
    json.dump(dict(vocab['dipl']), f)

with open('./data/out/vocab/facs.json', 'w', encoding='utf8') as f:
    json.dump(dict(vocab['facs']), f)

print('done')
