import sys
import os
import re
import shutil
import subprocess
import JESubConverter
import requests
import time

steam_workshopcontent_dir = "D:\SteamLibrary\steamapps\workshop\content\\602960"
localmods_dir = "D:\\SteamLibrary\\steamapps\\common\\Barotrauma\\LocalMods"
collection_url = "https://steamcommunity.com/sharedfiles/filedetails/?id=2832236513"


mod_id = "2883784919"

def get_htm_of_collection_site(link):
    response = requests.get(link, timeout=200)
    if response.status_code == 200:
        return response.text
    else:
        # coundt be bothered to do it other way
        return "ERROR"

def copy_and_edit(steam_workshopcontent_dir, localmods_dir, mod_id):
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
        pattern = "(?<=file=\")Mods\/" + re.escape(mod_name)
        file_content = re.sub(pattern, "%ModDir%", file_content)



    os.remove(filelist_path)
    with open(filelist_path,'w', encoding='utf8') as filelist:
        filelist.write(file_content)

    print("Copied " + os.path.join(steam_workshopcontent_dir, mod_id) + " to " + output_dir)

    return output_dir


def run_converter(mod_dir, localmods_dir, steam_workshopcontent_dir , mod_id):

    input_dir = os.path.join(steam_workshopcontent_dir, mod_id)
    print("Converter running on: " + mod_dir)
    # print("\"JE\ sub\ converter.py\"" + " -c" + " " + input_dir + " -d " + mod_dir)
    # subprocess.call(["python", "JE sub converter.py", "-c", input_dir, "-d", mod_dir])
    JESubConverter.runit(["-c", "-r", mod_dir, "-d", mod_dir])


def get_listOfMods(url_of_steam_collection):
    arr_of_witems = []
    collection_site = get_htm_of_collection_site(url_of_steam_collection)
    if collection_site != "ERROR":
        pattern = "(?<=<a href=\"https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=).*?(?=\"><div class=\"workshopItemTitle\">)"
        arrx = re.findall(pattern, collection_site)
        pattern = "(?<=<img class=\"workshopItemPreviewImage\" src=\").*?(?=\?imw=)"
        arry = re.findall(pattern, collection_site)
        for i in range(len(arrx)):
            WorkshopItem = {'ID': arrx[i], 'PrewiewPic': arry[i]}
            arr_of_witems.append(WorkshopItem)
    return arr_of_witems

def get_previewImage(url,mod_dir):
    preview_filename = "Thumbnail.JPG"
    preview_filename = os.path.join(mod_dir, preview_filename)
    time.sleep(1)
    res = requests.get(url, stream = True, timeout=200)
    if res.status_code == 200:
        with open(preview_filename,'wb') as f:
            shutil.copyfileobj(res.raw, f)
            print('Image sucessfully Downloaded: ', preview_filename)
    else:
        print('Image Couldn\'t be retrieved')

def main():
    arr_of_witems = get_listOfMods(collection_url)
    # No waypoints "error" handling, look into JESubConverter
    error_arr = []
    for x in arr_of_witems:
        mod_id = str(x["ID"])

        mod_dir = copy_and_edit(steam_workshopcontent_dir, localmods_dir, mod_id)

        # get image
        url = str(x["PrewiewPic"])
        get_previewImage(url,mod_dir)

        with open(os.path.join(mod_dir, "README.md"),'w') as f:
            f.write("Updated for Jobs Extended using JESubCollectionConverter\nOriginal submarine at: " + "https://steamcommunity.com/sharedfiles/filedetails/?id=" + mod_id)
            print('Readme created: ',os.path.join(mod_dir, "README.md"))

        run_converter(mod_dir, localmods_dir, steam_workshopcontent_dir, mod_id)
        

        # No waypoints "error" handling, look into JESubConverter
        filelist_path = os.path.join(mod_dir, "filelist.xml")
        filelist = ""
        with open(filelist_path,'r+', encoding='utf8') as file_content:
            filelist = file_content.read()
        pattern = "(?<=file=\"%ModDir%\/).*.sub(?=\" \/>)"
        sub_files = re.findall(pattern, filelist)
        not_changed = 0
        for sub_file in sub_files:
            # Fix for people INABILITY to name their subs properly
            sub_files_in_wm_folder = JESubConverter.get_list_of_sub_files_in_dir(os.path.join(steam_workshopcontent_dir, mod_id))
            sub_files_in_lm_folder = JESubConverter.get_list_of_sub_files_in_dir(mod_dir)
            # FUCK IT
            for sub_file_x in sub_files_in_lm_folder:
                for sub_file_y in sub_files_in_wm_folder:
                    if sub_file_x == sub_file_y:
                        not_changed += 1
            if os.path.exists(os.path.join(mod_dir, sub_file)) == False:
                # if it didnt find it NOT MY-- AH FUCK
                if os.path.exists(os.path.join(mod_dir, sub_file[0:-9] + ".sub")) == True:
                    filelist = filelist.replace(sub_file, sub_file[0:-9] + ".sub")
                else:
                    # ... find a sub file that is missing form sub_files_in_lm_folder
                    # on a second thought automatic is bad idea
                    filelist = filelist.replace(sub_file, "ERROR DID NOT FIND A SUB" + ".sub")
                    # should pop up in game, but in account oon me being a dumbass lest make a note to remind myself
                    error_arr.append(mod_dir[0:-5] + " - SUB COULD NOT BE FOUND -  " + sub_file)
                    with open(mod_dir[0:-5] + " - SUB COULD NOT BE FOUND -  " + sub_file + ".txt", 'w') as f:
                        pass
        if not_changed == len(sub_files):
            shutil.rmtree(mod_dir)
            with open(mod_dir[0:-5] + " - None of sub files had a valid waypoints.txt", 'w') as f:
                pass
                print("ERROR: None of sub files had a valid waypoints")
            not_changed = 0
            error_arr.append(os.path.basename(mod_dir[0:-5]))
        if not_changed > 0:
            os.remove(filelist_path)
            with open(filelist_path,'w', encoding='utf8') as file_filelist:
                file_filelist.write(filelist)
        print("\n")
    
    # No waypoints "error" handling, look into JESubConverter
    print("Printing errors:")
    for error in error_arr:
        print(error)

if __name__ == '__main__':
    main()