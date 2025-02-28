import requests
from bs4 import BeautifulSoup
from pydriller import Repository
from tqdm import tqdm
import json
from datetime import datetime, timedelta
from models.commit_parser import GitHubCommit, ModifiedFile

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

KEYWORDS = ["fix", "bug", "error"]

class GitScraper:
    def gitstar_ranking_generator(this,pages: int):
        """Generator function to fetch repositories from GitStar ranking pages."""
        for page in range(1, pages + 1):
            url = f"https://gitstar-ranking.com/repositories?page={page}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Failed to fetch page {page}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", class_="list-group-item paginated_item")

            for link in links:
                href = link.get("href")
                repo_url = f"https://github.com{href}" if href else "Unknown"

                # Extract language
                language_div = link.find("div", class_="repo-language")
                language = language_div.find("span").text.strip() if language_div else "Unknown"

                # Extract star count
                star_span = link.find("span", class_="stargazers_count pull-right")
                star_count = star_span.text.strip().replace(",", "") if star_span else "0"

                yield (repo_url, language, int(star_count) if star_count.isdigit() else 0)

    def git_scrape(this):
        repository_rank = 0
        one_year_ago = datetime.now() - timedelta(days=365)
        commit_count = 0
        commit_limit = 10000

        for repo in this.gitstar_ranking_generator(1):
            repository_rank += 1

            if repo[1] != "Python":
                print(bcolors.WARNING + f"{repository_rank}> Repository {repo[0]} is not Python skipping" + bcolors.ENDC)
                continue
            print(bcolors.OKBLUE + f"{repository_rank}> Fetching repository: {repo[0]} " + bcolors.ENDC)

            commit_count = 0
            for commit in Repository(repo[0], since=one_year_ago).traverse_commits():
                if commit_count >= commit_limit:
                    break
                commit_count += 1

                try:
                    modified_file = None

                    if commit.lines < 10: # This is a suitable filter for initial raw data collection
                        if sum(1 for file in commit.modified_files if file.filename.endswith('.py')) == 1:
                            file = next(file for file in commit.modified_files if file.filename.endswith('.py'))

                            modified_file = ModifiedFile(
                                filename=file.filename,
                                cyclomatic_complexity=file.complexity,
                                added_lines=file.diff_parsed["added"],
                                deleted_lines=file.diff_parsed["deleted"]
                            )

                            print("\n")
                            print(bcolors.OKCYAN + "____COMMIT____")
                            print(bcolors.OKBLUE + file.filename)
                            print(bcolors.OKCYAN + "|‾‾‾‾‾‾‾‾‾‾‾‾‾")
                            print(bcolors.OKCYAN + "|> Added")
                            for added in file.diff_parsed["added"]:
                                print(bcolors.OKGREEN + "| ln {0:<4}: {1}".format(added[0], added[1]))
                            print(bcolors.OKCYAN + "|> Removed")
                            for deleted in file.diff_parsed["deleted"]:
                                print(bcolors.FAIL + "| ln {0:<4}: {1}".format(deleted[0], deleted[1]))
                            print(bcolors.OKCYAN + "|_____________" + bcolors.ENDC)

                    commit_object = GitHubCommit(
                        repository=repo[0], 
                        repository_stars=repo[2], 
                        hash_id=commit.hash, 
                        msg=commit.msg, 
                        author=commit.author.name, 
                        author_date=commit.author_date, 
                        author_timestamp=commit.author_date.timestamp(), 
                        author_timezone=commit.author_timezone, 
                        lines=commit.lines, 
                        modified_file=modified_file
                    )
                    
                    print(commit_object)

                except Exception as e:
                    print(bcolors.FAIL + f"Error processing commit {commit.hash}: {e}")
