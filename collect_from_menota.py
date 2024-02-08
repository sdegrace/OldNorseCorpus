import csv

from urllib.request import urlopen
from lxml import etree
from io import TextIOWrapper
import re

def get_tree(path):
    with urlopen(path) as response:
        xml = TextIOWrapper(response, encoding='utf-8')
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8', no_network=False)
        textXML = xml.read().replace('&twodotPM;', '⁚')
        return etree.fromstring(bytes(bytearray(textXML, encoding='utf-8')), parser)


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
        title = tree.find('{http://www.tei-c.org/ns/1.0}teiHeader').find('{http://www.tei-c.org/ns/1.0}fileDesc').find('{http://www.tei-c.org/ns/1.0}titleStmt').find('{http://www.tei-c.org/ns/1.0}title').text
        title = re.sub(r'(:|/|\\|\)|\(|,|\.)+', '-', title)
        title = re.sub(r'\s+', '_', title).replace(' ', '_').replace(':', '').replace('_-_', '-')
        print(title)
        for page in pages:
            # print('\tPage '+page.text)
            for e in page.findall('*'):
                f = e.find('.//{http://www.menota.org/ns/1.0}facs')
                if f is not None and f.itertext() is not None:
                    facs += ''.join(f.itertext()) + ' '
                d = e.find('.//{http://www.menota.org/ns/1.0}dipl')
                if d is not None and d.itertext() is not None:
                    dipl += ''.join(d.itertext()) + ' '
                n = e.find('.//{http://www.menota.org/ns/1.0}norm')
                if n is not None and n.itertext() is not None:
                    norm += ''.join(n.itertext()) + ' '

        if len(facs):
            with open(f'./data/out/{title}_facs.txt', 'w', encoding='utf8') as f:
                f.write(facs)
        if len(dipl):
            with open(f'./data/out/{title}_dipl.txt', 'w', encoding='utf8') as f:
                f.write(dipl)
        if len(norm):
            with open(f'./data/out/{title}_norm.txt', 'w', encoding='utf8') as f:
                f.write(norm)



