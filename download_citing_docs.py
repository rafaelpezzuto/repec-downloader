import os
import requests

from multiprocessing import Pool


CITING_DOCS_MAIN_URL = 'https://econpapers.repec.org/scripts/showcites.pf?h={0};iframes=no'
DIRECTORY_CITING_DOCS_PAGES = '/home/rafaeljpd/Data/repec/raw/citing_docs'
COLLECTING_COUNTER = 0


def _read_existing_files():
    return set([i[:-5] for i in os.listdir(DIRECTORY_CITING_DOCS_PAGES)])


def read_cited_codes(path_file):
    codes = set()
    existing_files = _read_existing_files()

    with open(path_file) as f:
        for row in f:
            els = row.split('|')
            total_citations = els[-1].strip()
            code = els[3].strip().replace('/', '_')

            if code not in existing_files:
                if int(total_citations) > 0:
                    codes.add(code)
    print('Existentes: %d\tPara baixar: %d' % (len(existing_files), len(codes)))
    return codes


def collect_page(code):
    data = requests.get(CITING_DOCS_MAIN_URL.format(code))
    if data:
        save_page(code, data.content.decode())

        global COLLECTING_COUNTER
        COLLECTING_COUNTER += 1

        print(code, COLLECTING_COUNTER, len(data.content.decode()))


def save_page(name, data):
    with open(os.path.join(DIRECTORY_CITING_DOCS_PAGES, name + '.html'), 'w') as f:
        f.write(data)


if __name__ == '__main__':
    codes = read_cited_codes('/home/rafaeljpd/Data/repec/biblio_econpapers.csv')
    with Pool(6) as p:
        p.map(collect_page, codes)
