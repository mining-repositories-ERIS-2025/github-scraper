from models.bcolor import bcolors
from io import BytesIO
from collections import Counter
import tokenize

class Patcher:
    def patch_file(self, file: dict) -> dict:
        patched_file = {}
        modified_file = file.get('modified_file')
        
        if modified_file is not None:
            added_tokens = self.tokenize_lines(modified_file.get("added_lines", []))
            deleted_tokens = self.tokenize_lines(modified_file.get("deleted_lines", []))
            
            patched_file = file.copy()
            patched_file['token_changes'] = {
                'added_tokens': dict(added_tokens),
                'deleted_tokens': dict(deleted_tokens)
            }
            
            print(bcolors.OKGREEN + f"Writing added and deleted tokens to file for {file['hashId']}" + bcolors.ENDC)
        
        return patched_file

    def tokenize_lines(self, lines):
        token_counts = Counter()
        for _, line in lines:
            tokens = self.extract_tokens(line)
            token_counts.update(tokens)

        return dict(sorted(token_counts.items(), key=lambda item: item[1], reverse=True))

    def extract_tokens(self, code):
        tokens = []
        try:
            cleaned_code = code.strip()
            if not cleaned_code:
                return tokens
            
            fake_file = BytesIO(f'\n{cleaned_code}'.encode('utf-8'))
            token_generator = tokenize.tokenize(fake_file.readline)
            for token in token_generator:
                if token.type == tokenize.NAME:
                    tokens.append(token.string)

        except (tokenize.TokenError, SyntaxError, LookupError, UnicodeError) as e: 
            print(bcolors.FAIL + f"Failed to tokenize line: {code}" + bcolors.ENDC)
            print(bcolors.FAIL + e + bcolors.ENDC)

        return tokens
