
from dataclasses import dataclass
import json
import os
import sys

import pandas as pd
from ydata_profiling import ProfileReport
import sweetviz as sv


@dataclass
class CommitEntry:
    repo: str
    commit_hash: str
    stars: int
    success: bool = False

@dataclass
class RepoResult:
    patched: list[CommitEntry]
    raw: list[CommitEntry]
    repo_name: str
    repo_stars: int

def get_commit_entries_from_jsonl(file_path: str) -> list[CommitEntry]:
    """
    Reads a JSONL file and returns a list of CommitEntry objects.
    
    Args:
        file_path (str): Path to the JSONL file.
        
    Returns:
        list[CommitEntry]: List of CommitEntry objects.
    """
    commit_entries = []
    
    with open(file_path, 'r') as file:
        for line in file:
            print(line)
            line = line.strip()
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {line}, file: {file_path}")
                
                sys.exit(1)
            
            stars = 0
            if 'repository_stars' in data:
                stars = data['repository_stars']
            else:
                print(f"Warning: 'repository_stars' not found in {file_path}")                
            
            commit_entry = CommitEntry(
                repo=data['repository'],
                commit_hash=data['hashId'],
                stars=stars,
            )
            commit_entries.append(commit_entry)
    
    return commit_entries

def get_all_files_in_directory(directory: str) -> list[str]:
    """
    Returns a list of all files in the specified directory.
    
    Args:
        directory (str): Path to the directory.
        
    Returns:
        list[str]: List of file paths.
    """
    file_paths = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    
    return file_paths

def check_commit_for_success(raw_commits: list[CommitEntry], patched_commits: list[CommitEntry]) -> list[CommitEntry]:
    """
    Compares two lists of commit entries and marks them as successful if they are present in both lists.
    
    Args:
        raw_commits (list[CommitEntry]): List of raw commit entries.
        patched_commits (list[CommitEntry]): List of patched commit entries.
        
    Returns:
        list[CommitEntry]: List of successful commit entries.
    """
    checked_commits = []
    
    for raw_commit in raw_commits:
        for patched_commit in patched_commits:
            if raw_commit.commit_hash == patched_commit.commit_hash:
                raw_commit.success = True
        checked_commits.append(raw_commit)    
    
    return checked_commits

def create_repo_results_from_checked_commits(checked_commits: list[CommitEntry]) -> list[RepoResult]:
    """
    Groups commit entries by repository and creates RepoResult objects.
    
    Args:
        checked_commits (list[CommitEntry]): List of checked commit entries.
        
    Returns:
        list[RepoResult]: List of RepoResult objects.
    """
    repo_results = {}
    
    for commit in checked_commits:
        if commit.repo not in repo_results:
            repo_results[commit.repo] = RepoResult(patched=[], raw=[], repo_name=commit.repo, repo_stars=commit.stars)
        
        if commit.success:
            repo_results[commit.repo].patched.append(commit)
        else:
            repo_results[commit.repo].raw.append(commit)
    
    # Remove repos with no patched commits
    for repo in list(repo_results.keys()):
        if len(repo_results[repo].patched) == 0:
            del repo_results[repo]
    
    return list(repo_results.values())


cleaned_files = get_all_files_in_directory('./data_stages/2_cleaned/')

all_cleaned_commits = []

all_patched_files = get_all_files_in_directory('./data_stages/5_categorized_patch/')

all_patched_commits = []

for file in cleaned_files:
    all_cleaned_commits.extend(get_commit_entries_from_jsonl(file))
    
for file in all_patched_files:
    all_patched_commits.extend(get_commit_entries_from_jsonl(file))

checked_commits = check_commit_for_success(all_cleaned_commits, all_patched_commits)

repo_results = create_repo_results_from_checked_commits(checked_commits)


patch_raw_ratios = []
for repo in repo_results:
    if len(repo.patched) == 0:
        patch_raw_ratios.append(0)
    else:
        patch_raw_ratios.append(len(repo.patched) / len(repo.raw))

repo_result_df = pd.DataFrame({
    'no_of_patched_commits': [len(repo.patched) for repo in repo_results],
    'no_of_cleaned_commits': [len(repo.raw) for repo in repo_results],
    'patched_commit_ratio': patch_raw_ratios,
    'repo_name': [repo.repo_name for repo in repo_results],
    'repo_stars': [repo.repo_stars for repo in repo_results],
})

profile = ProfileReport(repo_result_df, title="Pandas Profiling Report", explorative=True)

repo_result_df.to_csv("./graphs/repo_results.csv", index=False)

profile.to_file("./graphs/eda_report.html")
# requires patching venv/lib/python3.10/site-packages/sweetviz/graph_numeric.py, by commenting out lines with warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
report = sv.analyze(repo_result_df)
report.show_html("./graphs/eda_report_sweetviz.html", open_browser=False)
print("EDA reports generated successfully.")