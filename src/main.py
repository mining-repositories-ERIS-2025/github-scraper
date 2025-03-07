import math
from cleaner import Cleaner
from combined_scraper import GitScraper
from models.bcolor import bcolors
from models.commit_parser import git_hub_commit_to_dict
from models.file_writer import FileWriter
from models.file_reader import FileReader


def main():
    print(bcolors.OKBLUE + "Select an option:" + bcolors.ENDC)
    print(bcolors.OKCYAN + "1. Run scraping" + bcolors.ENDC)
    print(bcolors.OKCYAN + "2. Run cleaning" + bcolors.ENDC)
    choice = input(bcolors.OKBLUE + "Enter the number of the function to run: " + bcolors.ENDC)

    if choice == '1':
        print(bcolors.OKBLUE + "Running scraping..." + bcolors.ENDC)
        raw_1()
    elif choice == '2':
        print(bcolors.OKBLUE + "Running cleaning..." + bcolors.ENDC)
        cleaned_2()
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

if __name__ == '__main__':
    main()