import re
import json
import os, sys

class JSONSanitizer:
    def __init__(self):
        pass

    @staticmethod
    def sanitize_string_by_dict(json_str, dict_name, dict_values):
        # Find matches of {<DICT_NAME>['some key']}
        sanitized_json = json_str
        regex = re.compile('\\{' + dict_name + '\\[.*\\]\\}')
        for match in regex.finditer(json_str):
            # Strip the brackets
            stripped_match = re.sub('\\{|\\}', '', match.group(0))
            stripped_match = re.sub(dict_name, 'dict_values', stripped_match)
            # This will throw an exception when the key does not exist
            value = eval(stripped_match)
            # Set the value in the final json
            sanitized_json = sanitized_json.replace(match.group(0), value)
        return sanitized_json

if __name__ == "__main__":
    # Read json
    with open('octopus/profiler/ap_profilers/github/frameworks/cmake_cpp.json', 'r') as f:
        data = f.read()
        y = JSONSanitizer.sanitize_string_by_dict(data, 'repo', {'name': 'x'})
        print(y)