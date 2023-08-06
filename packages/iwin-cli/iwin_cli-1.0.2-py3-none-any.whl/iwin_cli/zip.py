# import OS module
import json
import os
import json
from pathlib import Path
import zipfile
from iwin_cli.utils import createItem


def zipdir(path, zipfile):
    # ziph is zipfile handle

    for root, dirs, files in os.walk(path):
        for file in files:
            zipfile.write(os.path.join(root, file))

def createConfig(f_dir, zip_file):

    directory = Path(f_dir)
    p_path = directory.parent
    with zipfile.ZipFile(zip_file, mode="w") as archive:
        for file_path in directory.rglob("*"):
            archive.write(
                file_path,
                arcname=file_path.relative_to(p_path)
                )


# to store files in a list
def gen(path, config_file):

    json_fn = Path(path) /'pack.json'
    start_path = Path(path).parent
    list = []
    data = {"preload": {"files":list}}

    # dirs=directories
    for (root, dirs, file) in os.walk(path):
        for f in file:
            file_type = None

            if '.png' in f or '.jpg' in f:
                
                file_type = "image"
            elif '.mp3' in f or '.wav' in f or '.ogg' in f:
                file_type = "audio"
            elif 'pack.json' in f:
                file_type = None
            elif '.json' in f:
                file_type = "json"
            if file_type is None:
                continue

            item = createItem(f, root, file_type, start_path)
            # print(f'item:{item}')
            list.append(item)
        json_data = json.dumps(data, indent=4)
        with open(json_fn, "w") as outfile:
            outfile.write(json_data)
            
        createConfig(path, config_file)

def generateConfigZip(simulation_path):
    yes = input("需要生成压缩的模拟配置文件吗？[y/n?]") or 'n'
    if yes in ['y', 'Y', 'yes', 'Yes', 'YES']:
        config_file = input("压缩后的文件名：<simulation_config.zip> ") or "simulation_config.zip"
        gen(simulation_path, config_file)
# # Using the special variable 
# # __name__
# if __name__=="__main__":
#     gen()