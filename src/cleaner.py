from models.bcolor import bcolors

class Cleaner:
    def __init__(self):
        self.err_count = 0
        self.total_count = 0
        
    def clean_file(self, file: dict) -> dict:
        cleaned_file = {}
        modified_file = file.get('modified_file')
        self.total_count += 1
        if modified_file is not None:
            added_lines = modified_file.get("added_lines", [])
            deleted_lines = modified_file.get("deleted_lines", [])

            if len(added_lines) == 0 and len(deleted_lines) == 0:
                print(bcolors.FAIL + f"Skipping {file['hashId']} due to empty added and deleted lines" + bcolors.ENDC)
                self.err_count += 1
                return cleaned_file

            for key, value in file.items():
                if key in ['repository', 'hashId', 'msg', 'repository_stars']:
                    cleaned_file[key] = value

            cleaned_file['modified_file'] = {
                'added_lines': added_lines,
                'deleted_lines': deleted_lines
            }
            print(bcolors.OKGREEN + f"Writing {file['hashId']} to cleaned file" + bcolors.ENDC)
        else:
            self.err_count += 1
            print(bcolors.FAIL + f"Skipping {file['hashId']}" + bcolors.ENDC)
        
        return cleaned_file