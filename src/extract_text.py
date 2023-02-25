import glob
import os

import bs4
from bs4 import BeautifulSoup
from tqdm import tqdm

from grobid_client_python.grobid_client.grobid_client import GrobidClient

# start docker
identify = ["persName", 'head', "ref", "biblStruct", "formula", "s"]
client = GrobidClient(grobid_server="http://localhost:8070",
                      coordinates=identify,
                      sleep_time=10,
                      timeout=600, )

# +++++++++++++++++++++++++++++++++++++
#           Extract text from pdf
# -------------------------------------
# loop over folder to avoid hanging

folders = os.listdir('data/pdf')
tei_parent_folder = 'data/pdf-extract-tei-xml'
for folder in tqdm(folders):
    client.process(service='processFulltextDocument',
                   input_path=f'data/pdf/{folders}',
                   output=f'{tei_parent_folder}/{folders}',
                   n=10,
                   consolidate_header=True,
                   consolidate_citations=True,
                   tei_coordinates=False,
                   segment_sentences=True,
                   force=False,
                   verbose=True)

# +++++++++++++++++++++++++++++++++++++
#           Convert Tei to Txt
# -------------------------------------

out_folder = 'data/pdf-plain-text'
os.makedirs(out_folder, exist_ok=True)


def main(file):
    file_name = os.path.basename(file)

    soup = BeautifulSoup(open(file, 'r', encoding='utf-8'), features='lxml')

    def get_sentence_list(tag):
        return ' '.join([i.get_text() for i in tag.find_all("s")])

    def parse_main_body_text(body_tag):
        session_list = body_tag.find_all('div', recursive=False)
        out = []  # return nested list [[paragraphs...],[,,,]]
        for session in session_list:
            par_text = ''
            for paragraph in session.contents:
                if isinstance(paragraph, bs4.element.NavigableString):
                    par_text += paragraph.get_text() + '\n'
                elif isinstance(paragraph, bs4.element.Tag):
                    par_text += ' '.join([i.get_text() for i in paragraph.find_all('s')])
                else:
                    raise ValueError
            out.append(par_text)
        return '\n'.join(out)

    title = soup.title.get_text(separator=' ', strip=True)

    abstract = get_sentence_list(soup.abstract)
    if bool(abstract):
        abstract = 'Abstract: ' + abstract
    body = parse_main_body_text(soup.find('text'))

    out_text = '\n'.join([title, abstract, body])

    out_file = os.path.join(out_folder, file_name.replace('.tei.xml', '.txt'))
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(out_text)


files = glob.glob(f'{tei_parent_folder}/**/*.xml', recursive=True)
for file in tqdm(files):
    main(file)
