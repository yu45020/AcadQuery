import os
import glob
from tqdm import tqdm
from multiprocessing import Pool

pandoc_command = 'pandoc -f docx --strip-comments -i "{in_file}" -t plain -o "{out_file}"'


def main(file):
    os.system(pandoc_command.format(in_file=file, out_file=file.replace(".docx", '.txt')))


word_files = glob.glob("./data/pdf/**/*.docx")
for file in tqdm(word_files):
    main(file)
