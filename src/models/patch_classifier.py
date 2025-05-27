import os

def classify_patch(token_changes: list[str], commit_msg: str):
    try:
        diffs = token_changes['token_diff']
    except:
        print(token_changes)
        os.exit(1)
    adds = token_changes['added_tokens']
    dels = token_changes['deleted_tokens']

    ## boolean change
    if diffs.get("true",0) > 0 and diffs.get("false",0) > 0:
        return "boolean change"

    ## null check
    if diffs.get("None",0) > 0 and diffs.get("is",0) > 0:
        return "null check"

    ## collision avoidance using hash or random
    if diffs.get("hash",0) > 0 or diffs.get("random",0) > 0 or diffs.get("yield",0) != 0:
        return "collision avoidance"
    if diffs.get("lock", 0) > 0 or diffs.get("mutex",0) > 0 or diffs.get("cancel",0) > 0:
        return "collision avoidance"

    if diffs.get("dtype",0) > 0 or diffs.get("astype",0) > 0:
        return "explicit typing"

    if diffs.get("close",0) > 0 or diffs.get("open",0) > 0 or diffs.get("detach",0) > 0:
        return "open/close resource"

    ## try except
    if diffs.get("try",0) > 0 or diffs.get("except",0) > 0:
        return "try-except"

    for key in diffs.keys():
        if "Error" in key and diffs.get(key,0) > 0:
            return "change exception type"
        if "Exception" in key and diffs.get(key,0) > 0:
            return "Broaden exception type"

    ## condition logic
    if diffs.get("and",0) > 0 or diffs.get("&&",0) > 0:
        return "conditional tighten/loosen"
    if diffs.get("and",0) < 0 or diffs.get("&&",0) < 0:
        return "conditional tighten/loosen"
    if diffs.get("or",0) > 0 or diffs.get("||",0) > 0:
        return "conditional tighten/loosen"
    if diffs.get("or",0) < 0 or diffs.get("||",0) < 0:
        return "conditional tighten/loosen"  
    if diffs.get("not",0) != 0:
        return "conditional negate"

    ## ensuring cleanup
    if diffs.get("finally",0) > 0:
        return "ensure cleanup"

    if diffs.get("None",0) < 0 or diffs.get("int",0) > 0 or diffs.get("float",0) != 0 or diffs.get("uint16",0) != 0 or diffs.get("uint32",0) != 0 or diffs.get("int16",0) != 0 or diffs.get("int32",0) != 0:
        return "variable related change" 

    ## conditional change
    if diffs.get("if",0) != 0:
        return "conditional add/remove"

    ## function creation
    if diffs.get("def",0) > 0:
        return "function creation"
    
    ## numpy/regex based fix
    if diffs.get("numpy",0) != 0 or diffs.get("np",0) != 0 or adds.get("np",0) != 0 or adds.get("numpy",0) != 0:
        return "libary related fix"
    if diffs.get("re",0) != 0 or diffs.get("regex",0) != 0 or diffs.get("match",0) != 0 or "regex" in commit_msg.lower():
        return "libary related fix"
    if diffs.get("sqlalchemy",0) != 0 or diffs.get("sqlite3",0) != 0 or diffs.get("psycopg2",0) != 0 or diffs.get("pymysql",0) != 0:
        return "libary related fix"
    
    ## if time.sleep is used to fix race
    if diffs.get("time",0) != 0 or diffs.get("sleep",0) != 0 or diffs.get("timeout",0) != 0:
        return "time related fix"
    
        ## if time.sleep is used to fix race
    if diffs.get("str",0) != 0:
        return "string related fix"
    
    if adds.get("import",0) > 0 or dels.get("import",0) > 0:
        return "import change"
    if diffs.get("as",0) > 0 and diffs.get("with",0) > 0:
        return "import change"

    ## types not really fitting elsewhere
    if diffs.get("del",0) != 0:
        return "misc change"
    if diffs.get("filter",0) != 0:
        return "misc change"
    if "typo" in commit_msg.lower():
        return "misc change"

    ## if the fix was solved be only deleting code
    if len(adds) == 0 and len(dels) != 0:
        return "code deletion"

    ## if the change was made but was not registered by the parser
    if len(diffs) == 0:
        return "no syntax change"

    return None