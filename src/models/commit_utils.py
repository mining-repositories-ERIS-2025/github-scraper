
def eval_commit_diff(added_lines: dict[str, int], deleted_lines: dict[str, int]) -> dict[str, int]:
        token_diff = dict()
        for key in added_lines.keys() | deleted_lines.keys():
            val = added_lines.get(key, 0) - deleted_lines.get(key, 0)
            if val == 0:
                continue
            token_diff[key] = val
        return token_diff