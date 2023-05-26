"""
Use Adobe to convert pdf to word, then convert to plain text.
Adobe has hard time converting some documents, and all footnotes & headers are included
"""
"""
example 
pandoc -f docx -i  "[Ascarza et al](2017) Beyond the Target Customer.docx" -t plain -o  "[Ascarza et al](2017) Beyond the Target Customer.txt"
"""

import glob
import os
from tqdm import tqdm

docx_files = glob.glob('data/pdf/**/*.docx')
pandoc_command = 'pandoc -f docx -i "{in_file}" -t plain -o "{out_file}"'

for file in tqdm(docx_files):
    os.system(pandoc_command.format(in_file=file,
                                    out_file=file.replace(".docx", '.txt')))
