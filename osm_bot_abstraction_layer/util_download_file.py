import os
import subprocess

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
        # https://docs.python.org/3/library/subprocess.html
        try:
            with open(filepath, "w") as outfile:
                subprocess.run(["curl", "-L", download_url], check=True, stdout=outfile)
        except subprocess.CalledProcessError as e:
            print(e)
            print(e.returncode)
            print(e.stderr)
            print(e.cmd)
            if os.path.isfile(filepath):
                print("It was not supposed to happen, has some other program created this file?")
            return download_file_if_not_present_already(download_url, directory, filename)
    else:
        print(filepath, "downloaded already")
