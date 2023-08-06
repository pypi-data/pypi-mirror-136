from scrapers.nlp_progress.main import nlp_progress
from pycountry import languages

tdb = nlp_progress()

def all_subtasks(task):
    yield task
    for subtask in task.subtasks:
        yield from all_subtasks(subtask)

def all_tasks(tdb):
    for _, task in tdb.tasks.items():
        yield from all_subtasks(task)


import re
interlink_re = re.compile(r"\[[^]]*\]\([^)]*README.md\)")
languages_re = re.compile(r"\b(" + "|".join([re.escape(lang.name) for lang in languages if len(lang.name)>4 and lang.name.istitle()])+r")\b", re.I)

def format_dataset(dataset):
    name = dataset.name
    description = dataset.description
    description = interlink_re.sub("\n", description).strip()
    description += "\nSource: [https://nlpprogress.com](NLP-progress)"
    langs = list(set(languages_re.findall(name + " " + description)))
    return {"name": name, "description": description, "languages": langs}


datasets = []
for task in all_tasks(tdb):
    for dataset in task.datasets:
        datasets.append(format_dataset(dataset))
