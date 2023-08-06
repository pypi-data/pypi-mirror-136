from subprocess import call
call("pip install -q tqdm", shell=True)
import os
from tqdm.notebook import tqdm

class install:
    def __init__(self):
        self._install_code()
    def _install_code(self):
        if os.path.exists('i.txt'):
            filename = "i.txt"
        elif os.path.exists('requirements.txt'):
            filename = "requirements.txt"
        
        f = open(filename, "a")
        f.write("\n")
        f.close()

        f = open(filename, "r") 
        lst = [i[:-1] for i in f.readlines()]
        f.close()

        for i in tqdm(lst):
            if i[:4] == "npm:":
                call(f"npm install -g --silent {i[5:]}", shell=True)
            else:  
                call(f"pip install -q {i}", shell=True)    