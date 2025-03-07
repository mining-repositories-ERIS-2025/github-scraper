import os
import json

class FileReader:
    def readJsonLines(self, folder_path: str):
        for filename in os.listdir(folder_path):
            if filename.endswith('.jsonl'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as f:
                    for line in f:
                        yield json.loads(line)