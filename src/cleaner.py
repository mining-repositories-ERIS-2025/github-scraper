from models.bcolor import bcolors

class Cleaner:
    def clean_file(self, file: dict) -> dict:
        cleaned_file = {}
        modified_file = file.get('modified_file')

        if modified_file is not None:
            added_lines = modified_file.get("added_lines", [])
            deleted_lines = modified_file.get("deleted_lines", [])

            if len(added_lines) == 0 and len(deleted_lines) == 0:
                print(bcolors.FAIL + f"Skipping {file['hashId']} due to empty added and deleted lines" + bcolors.ENDC)
                return cleaned_file

            for key, value in file.items():
                if key in ['repository', 'hashId', 'msg']:
                    cleaned_file[key] = value

            cleaned_file['modified_file'] = {
                'added_lines': added_lines,
                'deleted_lines': deleted_lines
            }
            print(bcolors.OKGREEN + f"Writing {file['hashId']} to cleaned file" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + f"Skipping {file['hashId']}" + bcolors.ENDC)
        
        return cleaned_file