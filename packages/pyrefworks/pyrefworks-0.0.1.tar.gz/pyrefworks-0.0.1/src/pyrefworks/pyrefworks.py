import os
from quickcsv.file import quick_save_csv
def refworks_to_csv(refworks_folder,csv_path, ext='.txt'):

    list_item = []

    list_all_tag = []

    for file in os.listdir(refworks_folder):
        path = os.path.join(refworks_folder, file)
        if path.endswith(ext):
            lines = open(path, 'r', encoding='utf-8').readlines()
            model = {}
            is_rt = False
            for line in lines:
                line = line.strip()
                if line.startswith('RT '):
                    if is_rt:
                        if len(model.keys()) != 0:
                            list_item.append(model)
                            model = {}
                    is_rt = True
                if is_rt:
                    tag = line[:2]
                    value = line[2:]
                    tag = tag.strip()
                    value = value.strip()
                    if tag == "":
                        continue
                    if not tag.isupper():
                        continue
                    if tag not in list_all_tag:
                        list_all_tag.append(tag)
                    model[tag] = value
                    # print(tag)
                    # print(value)
                    # print()
    for idx, model in enumerate(list_item):
        for k in list_all_tag:
            if k not in model.keys():
                list_item[idx][k] = ""

    quick_save_csv(csv_path,list_all_tag, list_item)
