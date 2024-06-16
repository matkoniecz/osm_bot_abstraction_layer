import os

def download_file_if_not_present_already(download_url, directory, filename):
    filepath = directory + filename
    if directory[-1] != "/":
        filepath = directory + "/" + filename
    if os.path.isdir(directory) == False:
        print(directory, "is not directory!")
        raise Exception(directory + " is not directory!")
    if os.path.isdir(filepath):
        print(filepath, "is directory!")
        raise Exception(filepath + " is directory!")
    if os.path.isfile(filepath) != True:
        # -L follows redirects
        command = 'curl -L "' + download_url + '" > "' + filepath + '"'
        print(command)
        os.system(command)
    else:
        print(filepath, "downloaded already")
