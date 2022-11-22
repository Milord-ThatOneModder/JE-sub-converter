import sys
import os
import re
import shutil
import subprocess
import JESubConverter
import requests
import time

steam_workshopcontent_dir = "D:\SteamLibrary\steamapps\workshop\content\\602960"
localmods_dir = "LocalMods"

mod_id = "2883784919"

def copy_and_edit(steam_workshopcontent_dir, localmods_dir, mod_id):

    # parsed


    # vars used later
    pattern = "(?<=name=\").*?(?=\")"
    input_dir = os.path.join(steam_workshopcontent_dir, mod_id)
    output_dir = ""
    mod_name = ""

    filelist_path = os.path.join(input_dir, "filelist.xml")
    # load filelist, find mod name, remove steamworkshopid expectedhash, copy it to outputdir
    with open(filelist_path,'r', encoding='utf8') as filelist:
        # pattern = "name=\"Buntbarsch\""
        for line in filelist:
            if re.search(pattern, line):
                arrx = re.findall(pattern, line)
                mod_name = arrx[0]
                break

    output_dir = os.path.join(localmods_dir, mod_name + " [JE]")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    shutil.copytree(input_dir, output_dir)

    filelist_path = os.path.join(output_dir, "filelist.xml")
    file_content = ""
    with open(filelist_path,'r', encoding='utf8') as filelist:
        file_content = filelist.read()
        pattern = " steamworkshopid=\".*?\""
        file_content = re.sub(pattern, "", file_content)
        pattern = " installtime=\".*?\""
        file_content = re.sub(pattern, "", file_content)
        pattern = " expectedhash=\".*?\""
        file_content = re.sub(pattern, "", file_content)
        pattern = "(?<=name=\").*?(?=\")"
        file_content = re.sub(pattern, mod_name + " [JE]", file_content)
        pattern = "(?!([JE]))\.sub"
        file_content = re.sub(pattern, " [JE].sub", file_content)


    os.remove(filelist_path)
    with open(filelist_path,'w', encoding='utf8') as filelist:
        filelist.write(file_content)

    print("Copied " + os.path.join(steam_workshopcontent_dir, mod_id) + " to " + os.path.join(localmods_dir, mod_name))

    return output_dir

def run_converter(mod_dir, localmods_dir, steam_workshopcontent_dir , mod_id):

    input_dir = os.path.join(steam_workshopcontent_dir, mod_id)
    print("Converter running on: " + mod_dir)
    # print("\"JE\ sub\ converter.py\"" + " -c" + " " + input_dir + " -d " + mod_dir)
    # subprocess.call(["python", "JE sub converter.py", "-c", input_dir, "-d", mod_dir])
    JESubConverter.runit(["-c", "-r", mod_dir, "-d", mod_dir])

# (?<=<a href="https://steamcommunity.com/sharedfiles/filedetails/\?id=).*?(?="><div class="workshopItemTitle">)
filename = "Steam Workshop Subs to convert.htm"
steam_workshopcontent_dir = ""

arr_of_witems = []

with open(filename,'r', encoding='utf-8') as file_for_id:
    file_for_id_str = file_for_id.read()
    pattern = "(?<=<a href=\"https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=).*?(?=\"><div class=\"workshopItemTitle\">)"
    arrx = re.findall(pattern, file_for_id_str)
    pattern = "(?<=<img class=\"workshopItemPreviewImage\" src=\").*?(?=\?imw=)"
    arry = re.findall(pattern, file_for_id_str)
    for i in range(len(arrx)):
        WorkshopItem = {'ID': arrx[i], 'PrewiewPic': arry[i]}
        arr_of_witems.append(WorkshopItem)


for x in arr_of_witems:
    steam_workshopcontent_dir = "D:\SteamLibrary\steamapps\workshop\content\\602960"
    localmods_dir = "D:\\SteamLibrary\\steamapps\\common\\Barotrauma\\LocalMods"

    mod_id = str(x["ID"])

    mod_dir = copy_and_edit(steam_workshopcontent_dir, localmods_dir, mod_id)

    # get image
    url = str(x["PrewiewPic"])
    preview_filename = "thumbnail.JPG"
    preview_filename = os.path.join(mod_dir, preview_filename)
    time.sleep(1)
    res = requests.get(url, stream = True)
    if res.status_code == 200:
        with open(preview_filename,'wb') as f:
            shutil.copyfileobj(res.raw, f)
            print('Image sucessfully Downloaded: ',preview_filename)
    else:
        print('Image Couldn\'t be retrieved')

    with open(os.path.join(mod_dir, "README.md"),'w') as f:
        f.write("Original submarine at: " + "https://steamcommunity.com/sharedfiles/filedetails/?id=" + mod_id)
        print('Readme created: ',os.path.join(mod_dir, "README.md"))

    run_converter(mod_dir, localmods_dir, steam_workshopcontent_dir, mod_id)