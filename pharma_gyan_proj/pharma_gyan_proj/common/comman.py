import re


def is_valid_alpha_numeric_space_under_score(name):
    if name.strip() == "_":
        return False
    regex = '^[a-zA-Z0-9 _]+$'
    if re.fullmatch(regex, name):
        return True
    else:
        return False


def get_latest_id_list_of_dict(list_of_dict):
    # Dictionary to store the maximum id for each unique_id
    max_id_dict = {}

    # Iterate through the list of dictionaries
    for d in list_of_dict:
        unique_id = d.unique_id
        id_value = d.id

        # If unique_id is not in the dictionary or current id is greater than the stored id
        if unique_id not in max_id_dict or id_value > max_id_dict[unique_id].id:
            max_id_dict[unique_id] = d

    # Extract the dictionaries with the maximum id for each unique_id
    result = list(max_id_dict.values())

    # Print the result
    return result
