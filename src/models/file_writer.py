import json

class FileWriter:
    def writeJsonFile(self,path: str,data: dict):
        with open(path, 'a') as f:
            json_data = json.dumps(data)
            f.write(json_data + '\n')