import jinja2
import os
import toml
import argparse
from datetime import date
import pandoc
import copy



def getClosestDir(path : str) -> str:
  absPath = os.path.abspath(path)
  if os.path.isdir(absPath):
    return path
  else:
    return os.path.split(absPath)[0]


parser = argparse.ArgumentParser()
parser.add_argument('-s,', '--source')
parser.add_argument('-i,', '--input', required=True)
parser.add_argument('-o,', '--output', required=True)
args = parser.parse_args()

# TOML
resumeTOMLPath = args.source if args.source else 'resume.toml'
resume = toml.load(resumeTOMLPath)

def addDateStrings(toml_dict: dict):
  toml_dict_copy = copy.copy(toml_dict)
  for key, value in toml_dict.items():
    if type(value) == dict:
      toml_dict[key] =  addDateStrings(value)
    elif type(value) == str:
      if value == "Present":
        toml_dict_copy[f"{key}MonthYear"] = "Present"
        continue
      try:
        dt = date.fromisoformat(value)
        # print(dt)
        month = date.strftime(dt, "%B")
        year = date.strftime(dt, "%Y")
        toml_dict_copy[f"{key}Month"] = month
        toml_dict_copy[f"{key}Year"] = year
        toml_dict_copy[f"{key}MonthYear"] = f"{month} {year}"
      except Exception:
        pass
  return toml_dict_copy

resume = addDateStrings(resume)

def sanitizeStrings(target):
  if type(target) ==  list:
    items = enumerate(target)
  elif type(target) == dict:
    items = target.items()

  for key,value in items:
    if type(value) ==  list or type(value) == dict:
      sanitizeStrings(value)
    elif type(value) == str:
      doc = pandoc.read(value,format='commonmark')
      target[key] = pandoc.write(doc, format='latex', options=["--wrap",'none']).strip()

      print(target[key])
  return target

#only if latex
resume = sanitizeStrings(resume)

# from json import dumps
# print(dumps(resume,indent=4))




latexDirPath = getClosestDir(args.input)
inFileName = os.path.basename(args.input)
outFilePath = os.path.abspath(args.output)


latex_jinja_env = jinja2.Environment(
    block_start_string='\\block{',
    block_end_string='}',
    variable_start_string='\\var{',
    variable_end_string='}',
    comment_start_string='\#{;',
    comment_end_string='}',
    # line_statement_prefix='%-',
    # line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(latexDirPath)
)

resumeLatexTemplate = latex_jinja_env.get_template(inFileName)
resumeLatex = resumeLatexTemplate.render(**resume)
with open(outFilePath, 'w') as outFile:
  outFile.write(resumeLatex)
