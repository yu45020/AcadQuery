"""
Generate a list of papers
"""
import glob
import os

pdf_parent_folder = 'data/pdf'
out_file = 'data/list_of_papers.md'
deploy_file = 'deploy/data/list_of_papers.md'


def get_file_names(file_path, file_dict):
    parent_folder = os.path.split(os.path.dirname(file_path))[-1].strip()
    file_name = os.path.basename(file_path).strip()
    file_dict[parent_folder].append(file_name)


parent_folder = os.listdir(pdf_parent_folder)
pdf_dict = dict((i, []) for i in parent_folder)
[get_file_names(i, pdf_dict) for i in glob.glob("data/pdf/**/*.pdf", recursive=True)]

table_content = '\n'.join(
    f" - [{i} ({len(pdf_dict[i])})](#{'-'.join(i.lower().split(' '))})" for i in pdf_dict.keys())
table_content_css = """
<div id="contents" style="position:fixed;width: 350px;right:0;top:100"> 

""" + table_content + """ 

</div>
<style>
  #contents:hover div {display: block;}
</style>

"""

title = '# List of Papers'
content = table_content_css + title + "\n\n" + '---\n'
for folder in pdf_dict.keys():
    content += f"\n## {folder} \n"
    content += '\n'.join(f"* `{file.replace('.pdf', '').title()}` \n" for file in sorted(pdf_dict[folder]))
with open(out_file, 'w', encoding='utf-8') as f:
    f.write(content)

with open(deploy_file, 'w', encoding='utf-8') as f:
    f.write(content)
