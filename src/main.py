import math
from cleaner import Cleaner
from patcher import Patcher
from combined_scraper import GitScraper
from models.bcolor import bcolors
from models.commit_parser import git_hub_commit_to_dict
from models.file_writer import FileWriter
from models.file_reader import FileReader


def main():
    print(bcolors.OKBLUE + "Select an option:" + bcolors.ENDC)
    print(bcolors.OKCYAN + "1. Run scraping" + bcolors.ENDC)
    print(bcolors.OKCYAN + "2. Run cleaning" + bcolors.ENDC)
    print(bcolors.OKCYAN + "3. Run patching" + bcolors.ENDC)
    print(bcolors.OKCYAN + "4. Run catagorizing bug type" + bcolors.ENDC)
    print(bcolors.OKCYAN + "5. Run catagorizing patch type" + bcolors.ENDC)
    choice = input(bcolors.OKBLUE + "Enter the number of the function to run: " + bcolors.ENDC)

    if choice == '1':
        print(bcolors.OKBLUE + "Running scraping..." + bcolors.ENDC)
        raw_1()
    elif choice == '2':
        print(bcolors.OKBLUE + "Running cleaning..." + bcolors.ENDC)
        cleaned_2()
    elif choice == '3':
        print(bcolors.OKBLUE + "Running patching..." + bcolors.ENDC)
        patched_3()
    elif choice == '4':
        print(bcolors.OKBLUE + "Running categorizing..." + bcolors.ENDC)
        categorized_bug_4()
    elif choice == '5':
        print(bcolors.OKBLUE + "Running categorizing..." + bcolors.ENDC)
        categorized_type_5()
    else:
        print(bcolors.FAIL + "Invalid choice" + bcolors.ENDC)

def raw_1():
    scraper = GitScraper()
    filewriter = FileWriter()

    scrap_index = 0
    for scrap in scraper.git_scrape():
        scrap_index += 1
        if scrap.modified_file is None:
            print(bcolors.OKBLUE + f"{scrap_index} > Scraping Commit:"+bcolors.OKCYAN+f" {scrap.msg} ")
        else:
            print(bcolors.OKBLUE + f"{scrap_index} > Scraping Commit:"+bcolors.OKGREEN+f" {scrap.msg} "+bcolors.OKGREEN+f" {scrap.modified_file.filename} ")

        file_index = math.ceil(scrap_index / 10000)
        filewriter.writeJsonFile(f'./data_stages/1_raw/commits_{file_index:04}.jsonl', git_hub_commit_to_dict(scrap))

def cleaned_2():
    filewriter = FileWriter()
    filereader = FileReader()

    clean_index = 0
    for file in filereader.readJsonLines('./data_stages/1_raw'):
        cleaned_file = Cleaner().clean_file(file)
        if cleaned_file == {}:
            continue

        clean_index += 1
        file_index = math.ceil(clean_index / 10000)
        filewriter.writeJsonFile(f'./data_stages/2_cleaned/commits_cleaned_{file_index:04}.jsonl', cleaned_file)

def patched_3():
    filewriter = FileWriter()
    filereader = FileReader()

    patch_index = 0
    for file in filereader.readJsonLines('./data_stages/2_cleaned'):
        patched_file = Patcher().patch_file(file)
        if patched_file == {}:
            continue

        patch_index += 1
        file_index = math.ceil(patch_index / 10000)
        filewriter.writeJsonFile(f'./data_stages/3_patched/commits_patched_{file_index:04}.jsonl', patched_file)

def categorized_bug_4():
    filewriter = FileWriter()
    filereader = FileReader()

    categories = {
                  'null pointer exceptions': [' null ', "null-pointer", "null pointer", "nullpointer" 'seg', ' npe'], 
                  'overflows': [' overflow '],
                  'race conditions': [' race ', 'mutex '," deadlock "], 
                  'memory leaks': ['memory leak', 'memory-leak']
                  }

    categorized_messages = {key: [] for key in categories.keys()}
    for file in filereader.readJsonLines('./data_stages/3_patched'):
        # get commit message
        commit_message = file.get('msg').lower()


        # map to category
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in commit_message:
                    file['category'] = category
                    file['keyword_used'] = keyword
                    categorized_messages[category].append(file)
                    filewriter.writeJsonFile(f'./data_stages/4_categorized/commits_{category}.jsonl', file)
    
def categorized_type_5():
    filewriter = FileWriter()
    filereader = FileReader()
  
    for file in filereader.readJsonLines('./data_stages/4_categorized'):

        diffs = file['token_changes']['token_diff']
        category = file['category']

        change = helper_constrain_or_loosen(diffs)
        if change != None:
            file['patch_type'] = change
            filewriter.writeJsonFile(f'./data_stages/5_categorized_patch/commits_{category}.jsonl', file)
            continue
        change = helper_nullcheck(diffs)
        if change != None:
            file['patch_type'] = change
            filewriter.writeJsonFile(f'./data_stages/5_categorized_patch/commits_{category}.jsonl', file)
            continue



def helper_try_except(diffs: list[str]):
    if diffs.get("try") > 0 and diffs.get("except") > 0:
        if diffs.get("OverflowError") > 0:
            return "try-except OverflowError"
        return "try-except"
    return None

def helper_collison(diffs: list[str]):
    if diffs.get("hash") > 0 or diffs.get("random") > 0:
        return "collision avoidance"
    return None

def helper_checkclosure(diffs: list[str]):
    if diffs.get("if",0) > 0 and diffs.get("done",0) > 0:
        return "check closure"
    return None

def helper_nullcheck(diffs: list[str]):
    if diffs.get("None",0) > 0 and diffs.get("is",0) > 0:
        return "null check"
    return None

def helper_constrain_or_loosen(diffs: list[str]):
    if diffs.get("and",0) > 0:
        return "Conditional tighten"
    if diffs.get("and",0) < 0:
        return "Conditional loosening"
    if diffs.get("or",0) > 0:
        return "Conditional loosen"
    if diffs.get("or",0) < 0:
        return "Conditional tighten"    
    return None


if __name__ == '__main__':
    main()