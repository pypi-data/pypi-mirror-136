"""This is a file type identifier"""


def identifier(path1, path2):
    """Identifies type of file and returns it"""
    if 'csv' in str(path1) and 'csv' in str(path2):
        return "csv"
    elif 'dat' in str(path1) and 'dat' in str(path2):
        return "dat"
    elif 'json' in str(path1) and 'json' in str(path2):
        return "json"
    else:
        print("""Format not suported or multiple formats used.
        Please use a single format on both files""")
        return False
