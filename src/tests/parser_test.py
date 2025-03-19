import os
import pytest
from models.commit_parser import git_hub_commit_from_dict
import json

@pytest.fixture
def commit_file():
    file = os.path.join(os.path.dirname(__file__), 'assets/example_commit.json')
    with open(file, 'r') as f:
        return f.read()

def test_parse_json_commit_into_github_commit(commit_file):
    commit = json.loads(commit_file)
    print(commit)
    github_commit = git_hub_commit_from_dict(commit)
    expected_hash = "f97e3548e54cfc914c195d6d4d48792e4d021261"
    expected_repo =  "https://github.com/AUTOMATIC1111/stable-diffusion-webui"
    expected_lines = 2
    assert github_commit.hash_id == expected_hash
    assert github_commit.repository == expected_repo
    assert github_commit.lines == expected_lines
    