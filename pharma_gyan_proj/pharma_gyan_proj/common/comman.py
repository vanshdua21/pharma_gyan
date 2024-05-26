import re


def is_valid_alpha_numeric_space_under_score(name):
    if name.strip() == "_":
        return False
    regex = '^[a-zA-Z0-9 _]+$'
    if re.fullmatch(regex, name):
        return True
    else:
        return False