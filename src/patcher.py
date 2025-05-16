from models.bcolor import bcolors
from io import BytesIO
from collections import Counter
import tokenize
import re
import ast

class Patcher:
    def __init__(self):
        self.err_count = 0
        self.total_count = 0
        self.current_file_is_error = False
        
    def patch_file(self, file: dict) -> dict:
        patched_file = {}
        modified_file = file.get('modified_file')
        
        if modified_file is not None:
            self.total_count +=1
            added_tokens = self.tokenize_lines(modified_file.get("added_lines", []))
            deleted_tokens = self.tokenize_lines(modified_file.get("deleted_lines", []))
            if self.current_file_is_error:
                self.err_count += 1
                self.current_file_is_error = False
            token_diff = dict()

            for key in added_tokens.keys() | deleted_tokens.keys():
                val = added_tokens.get(key,0) - deleted_tokens.get(key,0)
                if val == 0:
                    continue
                token_diff[key] = added_tokens.get(key,0) - deleted_tokens.get(key,0)

            patched_file = file.copy()
            patched_file['token_changes'] = {
                'added_tokens': dict(added_tokens),
                'deleted_tokens': dict(deleted_tokens),
                'token_diff': token_diff
            }
            
            print(bcolors.OKGREEN + f"Writing added and deleted tokens to file for {file['hashId']}" + bcolors.ENDC)
        
        return patched_file

    def tokenize_lines(self, lines, deleted_lines=None):
        token_counts = Counter()
        
        for idx, (i, line) in enumerate(lines):
            deleted_line = deleted_lines[idx][1] if deleted_lines and idx < len(deleted_lines) else None
            tokens = self.extract_tokens(line, deleted_line)
            token_counts.update(tokens)

        return dict(sorted(token_counts.items(), key=lambda item: item[1], reverse=True))


    def extract_tokens(self, code, deleted_line=None):
        tokens = []
        try:
            cleaned_code = code.strip()
            if not cleaned_code:
                return tokens

            try:
                parsed = ast.parse(cleaned_code)
                for node in ast.walk(parsed):
                    if isinstance(node, ast.Call):
                        for kw in node.keywords:
                            if isinstance(kw.value, ast.Constant) and kw.value.value in {True, False}:
                                tokens.append(f"{kw.arg}={kw.value.value}")
            except SyntaxError:
                pass

            fake_file = BytesIO(f'\n{cleaned_code}'.encode('utf-8'))
            token_generator = tokenize.tokenize(fake_file.readline)
            for token in token_generator:
                if token.type == tokenize.NAME:
                    tokens.append(token.string)

        except (tokenize.TokenError, SyntaxError, LookupError, UnicodeError) as e:
            self.current_file_is_error = True
            print(bcolors.FAIL + f"Failed to tokenize line: {code}" + bcolors.ENDC)
            print(bcolors.FAIL + str(e) + bcolors.ENDC)

        return tokens

