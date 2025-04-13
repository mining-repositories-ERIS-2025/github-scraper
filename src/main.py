import math
from cleaner import Cleaner
from models.graph import BarGraph, FrequencyMatrix
from patcher import Patcher
from combined_scraper import GitScraper
from models.bcolor import bcolors
from models.commit_parser import git_hub_commit_to_dict
from models.commit_utils import eval_commit_diff
from models.patch_classifier import classify_patch
from models.file_writer import FileWriter
from models.file_reader import FileReader
from selecter import Selector


def main():
    options = [
        ("Scraping", raw_1),
        ("Cleaning", cleaned_2),
        ("Patching", patched_3),
        ("Categorizing bug type", categorized_bug_4),
        ("Categorizing patch type", categorized_type_5),
        ("Frequency table", frequency_table_6),
    ]

    selector = Selector(options)
    selector.run()

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
    filewriter.cleanFolder(f'./data_stages/2_cleaned/')
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
    filewriter.cleanFolder(f'./data_stages/3_patched/')
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
    plot = BarGraph()

    categories = {
                'null pointer exceptions': [
                    ' null ', 
                    'null-pointer', 
                    'null pointer', 
                    'nullpointer',
                    'seg', 
                    ' npe'
                ], 
                'overflows': [
                    ' overflow'
                ],
                'race conditions': [
                    ' race ',
                    'mutex ',
                    ' deadlock '
                ], 
                'memory leaks': [
                    'memory leak', 
                    'memory-leak'
                ],
                'logical errors': [
                    ['indentation ', ' error '],
                    ' edge case ',
                    ' logic ',
                    ' fix error ',
                    ' infinite loop ',
                    'infinite-loop'
                ],
                'import errors': [
                    [' import',' error '],
                    'importerror'
                ],
                'division by zero': [
                    ' division by zero ', 
                    'divide by zero', 
                    'zero division'
                ],
                'network errors': [
                    ['error', ' network '],
                    ['error', ' socket '],
                    'network error', 
                    'networkerror',
                ],
                'prevented exception error': [
                    [' exception ', ' prevent '],
                    [' exception ', ' fix '],
                ],
                'unhandled exception error': [
                    [' exception ', ' add '],
                    [' exception ', ' raise '],
                    [' exception ', ' include '],
                    [' exception ', ' another '],
                    [' exception ', ' raise'],
                    [' exception ', ' correct '],
                    [' exception ', ' use '],
                    [' exception ', ' catch '],
                    [' exception ', ' make '],
                    [' exception ', ' handle '],
                    [' exception ', ' broaden'],
                ],
    }

    categorized_messages = {key: [] for key in categories.keys()}
    
    filewriter.cleanFolder(f'./data_stages/4_categorized/')
    for file in filereader.readJsonLines('./data_stages/3_patched'):
        # get commit message
        commit_message: str = file.get('msg').lower()

        found_keyword = False
        # map to category
        for category, keywords in categories.items():
            for outer_keyword in keywords:
                inner_index = 0
                outer_index = 0

                ## is nested array
                if isinstance(outer_keyword, list):
                    found_inner = True
                    for inner_keyword in outer_keyword:
                        if inner_keyword not in commit_message:
                            found_inner = False
                            break
                        if inner_keyword in commit_message:
                            print(bcolors.OKGREEN +f"Found keyword {inner_keyword} in commit message: {commit_message.split()}")
                            for idx, word in enumerate(commit_message.split()):
                                if word in inner_keyword:
                                    inner_index = idx
                                    break
                    if found_inner == True:
                        file['category'] = category
                        file['keyword_used'] = outer_keyword
                        
                        plot.add_to_frequency_dict(category)

                        categorized_messages[category].append(file)
                        found_keyword = True
                        break
                        
                ## Is not nested array
                else:
                    if outer_keyword in commit_message:
                        file['category'] = category
                        file['keyword_used'] = outer_keyword
                        
                        plot.add_to_frequency_dict(category)

                        categorized_messages[category].append(file)
                        print(bcolors.OKGREEN + f"Found keyword {outer_keyword} in commit message: {commit_message}")
                        for idx, word in enumerate(commit_message.split()):
                            if word in outer_keyword:
                                outer_index = idx
                                break
                        found_keyword = True
                        break
            
            index_diff = abs(inner_index - outer_index)

            has_inner = inner_index != 0 and outer_index != 0

            if has_inner or index_diff > 3:
                found_keyword = False

            if found_keyword != False:
                filewriter.writeJsonFile(f'./data_stages/4_categorized/commits_{category}.jsonl', file)
                found_keyword = False
                break
    
    plot.plot_histogram(title='Bug Category Frequency')

def categorized_type_5():
    filewriter = FileWriter()
    filereader = FileReader()
    plot = BarGraph()
  
    filewriter.cleanFolder(f'./data_stages/5_categorized_patch/')
    for file in filereader.readJsonLines('./data_stages/4_categorized'):

        category = file['category']
        if file.get('token_changes').get('token_diff') == None:
            file['token_changes']['token_diff'] = eval_commit_diff(file['token_changes']['added_tokens'], file['token_changes']['deleted_tokens'])
            print(f"No token diff found for added {file['token_changes']['added_tokens']} and deleted {file['token_changes']['deleted_tokens']}, calculated {file['token_changes']['token_diff']}")
        change = classify_patch(file['token_changes'], file['msg'])
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

def frequency_table_6():
    filereader = FileReader()
    plot = FrequencyMatrix()

    for file in filereader.readJsonLines('./data_stages/5_categorized_patch'):
        plot.add_to_frequency_dict(file.get('patch_type'), file.get('category'))
    plot.plot_matrix(title="Frequency Matrix Norm",normalize=True)
    plot.plot_matrix(title="Frequency Matrix")


if __name__ == '__main__':
    main()
