from typing import List, Union, Any, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    return x


def from_int(x: Any) -> int:
    return x

def from_float(x: Any) -> float:
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    return [f(y) for y in x]


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class ModifiedFile:
    filename: str
    cyclomatic_complexity: int
    added_lines: List[List[Union[int, str]]]
    deleted_lines: List[List[Union[int, str]]]

    def __init__(self, filename: str, cyclomatic_complexity: int, added_lines: List[List[Union[int, str]]], deleted_lines: List[List[Union[int, str]]]) -> None:
        self.filename = filename
        self.cyclomatic_complexity = cyclomatic_complexity
        self.added_lines = added_lines
        self.deleted_lines = deleted_lines

    @staticmethod
    def from_dict(obj: Any) -> 'ModifiedFile':
        assert isinstance(obj, dict)
        filename = from_str(obj.get("filename"))
        cyclomatic_complexity = from_int(obj.get("cyclomatic_complexity")) | -1
        added_lines = from_list(lambda x: from_list(lambda x: from_union([from_int, from_str], x), x), obj.get("added_lines"))
        deleted_lines = from_list(lambda x: from_list(lambda x: from_union([from_int, from_str], x), x), obj.get("deleted_lines"))
        return ModifiedFile(filename, cyclomatic_complexity, added_lines, deleted_lines)

    def to_dict(self) -> dict:
        result: dict = {}
        result["filename"] = from_str(self.filename)
        result["cyclomatic_complexity"] = from_int(self.cyclomatic_complexity)
        result["added_lines"] = from_list(lambda x: from_list(lambda x: from_union([from_int, from_str], x), x), self.added_lines)
        result["deleted_lines"] = from_list(lambda x: from_list(lambda x: from_union([from_int, from_str], x), x), self.deleted_lines)
        return result


class GitHubCommit:
    repository: str
    repository_stars: int
    hash_id: str
    msg: str
    author: str
    author_timestamp: float
    author_timezone: int
    lines: int
    modified_file: ModifiedFile

    def __init__(self, repository: str, repository_stars: int, hash_id: str, msg: str, author: str, author_date: str, author_timestamp: int, author_timezone: int, lines: int, modified_file: ModifiedFile) -> None:
        self.repository = repository
        self.repository_stars = repository_stars
        self.hash_id = hash_id
        self.msg = msg
        self.author = author
        self.author_date = author_date
        self.author_timestamp = author_timestamp
        self.author_timezone = author_timezone
        self.lines = lines
        self.modified_file = modified_file

    @staticmethod
    def from_dict(obj: Any) -> 'GitHubCommit':
        #assert isinstance(obj, dict)
        repository = from_str(obj.get("repository"))
        repository_stars = from_int(obj.get("repository_stars"))
        hash_id = from_str(obj.get("hashId"))
        msg = from_str(obj.get("msg"))
        author = from_str(obj.get("author"))
        author_timestamp = from_float(obj.get("author_timestamp"))
        author_timezone = from_int(obj.get("author_timezone"))
        lines = from_int(obj.get("lines"))
        modified_file = ModifiedFile.from_dict(obj.get("modified_file"))
        return GitHubCommit(repository, repository_stars, hash_id, msg, author, author_timestamp, author_timezone, lines, modified_file)

    def to_dict(self) -> dict:
        result: dict = {}
        result["repository"] = from_str(self.repository)
        result["repository_stars"] = from_int(self.repository_stars)
        result["hashId"] = from_str(self.hash_id)
        result["msg"] = from_str(self.msg)
        result["author"] = from_str(self.author)
        result["author_timestamp"] = from_float(self.author_timestamp)  # Changed from from_int to from_float
        result["author_timezone"] = from_int(self.author_timezone)
        result["lines"] = from_int(self.lines)
        result["modified_file"] = to_class(ModifiedFile, self.modified_file) if self.modified_file is not None else None
        return result


def git_hub_commit_from_dict(s: Any) -> GitHubCommit:
    return GitHubCommit.from_dict(s)


def git_hub_commit_to_dict(x: GitHubCommit) -> Any:
    return to_class(GitHubCommit, x)
