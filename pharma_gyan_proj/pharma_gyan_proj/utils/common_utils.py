import datetime
import random
import re
# from jsonschema import Draft4Validator
import string
import requests
import base64


def get_random_uuid(length=20):
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return ran


def get_uuid_digits(length):
    ran = ''.join(random.choices(string.digits, k=length))
    return ran


def get_uuid(length):
    ran = ''.join(random.choices(string.ascii_lowercase, k=length))
    return ran


# def validate_json_schema(json_schema, input_data):
#     """Validates the input data against  provided json_schema rules

#     Args:
#         json_schema (object) : Json schema containing the rules
#         input_data : The input data

#     Returns:
#        list : List of all errors that come in the validation

#     """
#     validator = Draft4Validator(json_schema)
#     errors = sorted(validator.iter_errors(input_data), key=lambda e: e.path)
#     return errors


def nested_path_get(obj, path_str, strict=False, mode='GET', default_return_value=None):
    """ gets value from an object though a provided path string

    Args:
        obj (obj) : The object containing the data
        path_str ( str) : Dotted path to the target, e.g. mykey.mysecondary_key.my_tertiarykey
        strict (bool) : If True, method will throw an exception if no value exists at the provided
                        path i.e. the path is invalid. Else, the method returns None if there
                        is no value at provided path
        mode (str): the function used to fetch path_str.('POP' or 'GET')
        default_return_value (anything): default return value

    Returns:
        Value at the provided nested path

    Examples:
        >>> obj = { 'success':True,'data':{ 'rank':'student','age':20 }}
        >>> nested_path_get(obj,'data.rank')
        'student'
        >>> nested_path_get(obj,'data.profession', strict=False)
        # Returns None
        >>> nested_path_get(obj,'data.profession', strict=True)
        # raises exception

    """

    nested_keys = path_str.split(".")
    for index, key in enumerate(nested_keys):
        if re.match(r'^[-\w|]+(\.[-\w|]+)?(\.[-\w|]+)?(\.[-\w|]+)?$', key) is None:
            raise Exception(f"{key} is invalid path str")

        try:
            if mode == "POP" and index == len(nested_keys) - 1:
                # if pop is required, pop object at last nested key level
                obj = obj.pop(key, default_return_value)
            else:
                obj = obj[key]
        except Exception:
            if strict is True:
                raise
            else:
                return default_return_value
    return obj


def nested_path_put(obj, path_str, value):
    nested_keys = path_str.split(".")
    obj_orig = obj
    for index, key in enumerate(nested_keys):
        if index == len(nested_keys) - 1:
            print(f"\t\tkey = {key}, value = {value}")
            obj[key] = value
            break
        obj = obj[key]
    print(f"\tobj_orig = {obj_orig}")
    return obj_orig

def get_today_date():
    utc_time = datetime.datetime.utcnow()
    return datetime.datetime(day=utc_time.day, month=utc_time.month, year=utc_time.year)

def url_to_base64(image_url):
    try:
        # Fetch the image data from the URL
        response = requests.get(image_url)
        if response.status_code == 200:
            # Convert image data to base64 encoding
            base64_data = base64.b64encode(response.content).decode('utf-8')
            # Format the base64 string as data URI
            data_uri = f"data:image/jpeg;base64,{base64_data}"
            return data_uri
        else:
            print(f"Failed to fetch image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching image: {str(e)}")
        return None