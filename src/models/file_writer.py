import json
import os
import glob

class FileWriter:

    def cleanFolder(self, path: str):
        # delete all .jsonl files in the folder
        files = glob.glob(os.path.join(path, '*.jsonl'))
        for f in files:
            os.remove(f)

    def writeJsonFile(self,path: str,data: dict):
        with open(path, 'a') as f:
            json_data = json.dumps(data)
            f.write(json_data + '\n')