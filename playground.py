# %%
from docxtpl import DocxTemplate
from datetime import date
import copy
import toml
import pandoc
#%%

resume = toml.load('./resume.toml')
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
# %%
doc = DocxTemplate('./word/resumeTemplate.docx')
doc.render(resume)
doc.save('./word/generated_resume.docx')

# %%

doc = pandoc.read('teddy\@gmail.com',format='gfm')
pandoc.write(doc, format='latex', options=["--wrap",'none']).strip()
# %%
