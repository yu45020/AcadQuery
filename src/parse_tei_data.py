"""
TODO: need spell checker?
"""
import glob
import os

import bs4
import pkg_resources
from bs4 import BeautifulSoup
from tqdm import tqdm

out_folder = 'data-processed/pdf-plain-text-from-tei'
os.makedirs(out_folder, exist_ok=True)
# dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
# bigram_path = pkg_resources.resource_filename("symspellpy", "frequency_bigramdictionary_en_243_342.txt")


def main(file_path):
    file_name = os.path.basename(file_path)

    soup = BeautifulSoup(open(file_path, 'r', encoding='utf-8'), features='lxml')

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

    out_file = os.path.join(out_folder, file_name.replace('.tei.xml', '.txt'))
    out_text = '\n'.join([title, abstract, body])
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(out_text)


files = glob.glob('data-processed/**/*.xml', recursive=True)
for file in tqdm(files):
    main(file)
