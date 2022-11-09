# import OS module
import os
 
dir_to_check = ""
# Get the list of all files and directories
if(len(dir_to_check) > 0):
    # TODO make an catch on file not found error
    dir_list = os.listdir(dir_to_check)
else:
    dir_list = os.listdir()

# getting .sub files list
sub_file_list = []
for file in dir_list:
    if(len(file)>4):
        if (str(file[-4]) + str(file[-3]) + str(file[-2]) + str(file[-1])) == '.sub':
            sub_file_list.append(file)

# testprint TODO make acctual good print of items that get changed
for file in sub_file_list:
    print(file)