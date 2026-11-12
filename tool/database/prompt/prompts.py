import os
import yaml

def YamlToPrompt(filepath):
    with open(filepath, "r") as file:
        prompt = yaml.safe_load(file)
    
    tableinfo=f"""This is a local SQLite table.
    The table is named {prompt['table_id']}.
    this table is about {prompt['table_description']}
    The table has the following columns 
    {prompt['headers']} 
    """        
    return tableinfo

def allTablesToPrompt(folderpath):
    # for all yaml file in the folder path call YamlToPrompt
    prompts = ["The Data Set has the following tables"]
    for i ,filename in enumerate (os.listdir(folderpath)):
        if filename.endswith(".yaml"):
            filepath = os.path.join(folderpath, filename)
            prompts.append(f"Table no {i}")
            prompts.append(YamlToPrompt(filepath))
    return "\n".join(prompts)

def getPrompt():
    folderpath= os.path.join("tool","database","tableDescription")
    Prompt=allTablesToPrompt(folderpath)
    return Prompt
