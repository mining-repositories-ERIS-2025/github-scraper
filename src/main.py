import math
import os
from cleaner import Cleaner
from models.graph import Graph
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
    plot = Graph()
    frequency_dict = {}

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

        found_keyword = False
        # map to category
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in commit_message:
                    file['category'] = category
                    file['keyword_used'] = keyword
                    
                    plot.add_to_frequency_dict(category)

                    categorized_messages[category].append(file)
                    found_keyword = True
            if found_keyword != False:
                filewriter.writeJsonFile(f'./data_stages/4_categorized/commits_{category}.jsonl', file)
                found_keyword = False
                break
    
    plot.plot_histogram(title='Bug Category Frequency')

def categorized_type_5():
    filewriter = FileWriter()
    filereader = FileReader()
    plot = Graph()
  
    for file in filereader.readJsonLines('./data_stages/4_categorized'):

        category = file['category']
        if file.get('token_changes').get('token_diff') == None:
            file['token_changes']['token_diff'] = eval_commit_dif(file['token_changes']['added_tokens'], file['token_changes']['deleted_tokens'])
            print(f"No token diff found for added {file['token_changes']['added_tokens']} and deleted {file['token_changes']['deleted_tokens']}, calculated {file['token_changes']['token_diff']}")
        change = helper_boolean(file['token_changes'], file['msg'])
        plot.add_to_frequency_dict(change)

        if change != None:
            file['patch_type'] = change
            filewriter.writeJsonFile(f'./data_stages/5_categorized_patch/commits_{category}.jsonl', file)
            continue
        else:
            file['patch_type'] = "unknown"
            filewriter.writeJsonFile(f'./data_stages/5_categorized_patch/commits_unknown.jsonl', file)
            continue
    plot.plot_histogram(title='Patch Type Frequency')


def helper_boolean(token_changes: list[str], commit_msg: str):
    try:
        diffs = token_changes['token_diff']
    except:
        print(token_changes)
        os.exit(1)
    adds = token_changes['added_tokens']
    dels = token_changes['deleted_tokens']

    ## if typo in commit msg
    if "typo" in commit_msg.lower():
        return "typo fix"

    ## boolean change
    if diffs.get("true",0) > 0 and diffs.get("false",0) > 0:
        return "boolean change"

    ## closure check
    if diffs.get("if",0) > 0 and diffs.get("done",0) > 0:
        return "check closure"

    ## null check
    if diffs.get("None",0) > 0 and diffs.get("is",0) > 0:
        return "null check"

    ## collision avoidance using hash or random
    if diffs.get("hash",0) > 0 or diffs.get("random",0) > 0:
        return "collision avoidance"

    if diffs.get("dtype",0) > 0 or diffs.get("astype",0) > 0:
        return "explicit typing"

    if diffs.get("lock", 0) > 0 or diffs.get("mutex",0) > 0:
        return "thread lock"

    if diffs.get("close",0) > 0 or diffs.get("open",0) > 0:
        return "open/close resource"
    
    if diffs.get("detach",0) > 0:
        return "Free GPU memory"

    ## try except
    if diffs.get("try",0) > 0 or diffs.get("except",0) > 0:
        #if diffs.get("OverflowError",0) > 0:
            #return "try-except OverflowError"
        return "try-except"

    ## scoping change
    if diffs.get("import",0) > 0:
        return "libary change"

    ## thread cancelling
    if diffs.get("cancel",0) > 0:
        return "thread cancelling"

    ## condition logic
    if diffs.get("and",0) > 0 or diffs.get("&&",0) > 0:
        return "conditional tighten"
    if diffs.get("and",0) < 0 or diffs.get("&&",0) < 0:
        return "conditional loosen"
    if diffs.get("or",0) > 0 or diffs.get("||",0) > 0:
        return "conditional loosen"
    if diffs.get("or",0) < 0 or diffs.get("||",0) < 0:
        return "conditional tighten"  
    if diffs.get("not",0) != 0:
        return "conditional negate"

    ## ensuring cleanup
    if diffs.get("finally",0) > 0:
        return "ensure cleanup"

    ## check if values are being populated, ie var = None -> var = "value"
    if diffs.get("None",0) < 0:
        return "value population"

    ## conditional change
    if diffs.get("if",0) != 0:
        return "conditional change"

    ## function creation
    if diffs.get("def",0) > 0:
        return "function creation"

    ## code deletion
    if diffs.get("del",0) != 0:
        return "object deletion"

    ## filter changes
    if diffs.get("filter",0) != 0:
        return "filter change"

    ## SQL based fix
    if diffs.get("sqlalchemy",0) != 0 or diffs.get("sqlite3",0) != 0 or diffs.get("psycopg2",0) != 0 or diffs.get("pymysql",0) != 0:
        return "sql fix"
    
    ## numpy based fix
    if diffs.get("numpy",0) != 0 or diffs.get("np",0) != 0 or diffs.get("ndarray",0) != 0:
        return "numpy fix"

    ## regex based fix
    if diffs.get("re",0) != 0 or diffs.get("regex",0) != 0 or diffs.get("match",0) != 0 or "regex" in commit_msg.lower():
        return "regex fix"

    ## if the fix was solved be only deleting code
    if len(adds) == 0 and len(dels) != 0:
        return "code deletion"

    ## if the change was made but was not registered by the parser
    if len(diffs) == 0:
        return "no syntax change"

    return None

def eval_commit_dif(added_lines: dict[str, int], deleted_lines: dict[str, int]) -> dict[str, int]:
    token_diff = dict()
    for key in added_lines.keys() | deleted_lines.keys():
        val = added_lines.get(key,0) - deleted_lines.get(key,0)
        if val == 0:
            continue
        token_diff[key] = added_lines.get(key,0) - deleted_lines.get(key,0)
    return token_diff



if __name__ == '__main__':
    main()
