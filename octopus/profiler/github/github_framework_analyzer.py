import json
import os
import pprint
import re
import fnmatch
from collections import defaultdict
from octopus.infra.json.json_sanitizer import JSONSanitizer

DEFAULT_MIN_FW_SCORE = 0.75
TILDA_FACTOR = 0.95

class GithubFrameworkAnalyzer:
    def __init__(self):
        self.__req_callbacks = {
            'files': self.__files_req_callback,
            'folders': self.__folders_req_callback,
            'languages': self.__languages_req_callback,
            'extensions': self.__extensions_req_callback
        }

        self.__ops_callbacks = {
            'top': self.__top_ops_callback,
            'exists': self.__exists_ops_callback
        }

        self.__defs_callbacks = {
            'structure_rules': self.__structure_rules_defs_callback
        }

    def __exists_ops_callback(self, base_path, values, is_folder):
        score = 1.0

        for file_val in values:
            stripped_file_val = re.sub('^(!|\\?|~)', '', file_val)
            file_path = os.path.join(base_path, stripped_file_val)
            exists = True
            if not os.path.exists(file_path):
                exists = False
            elif not ((is_folder and os.path.isdir(file_path)) or (not is_folder and os.path.isfile(file_path))):
                exists = False
            if file_val.startswith('!'):
                if not exists:
                    score *= 0.0
                    break
            elif file_val.startswith('~'):
                if not exists:
                    score *= TILDA_FACTOR
            else:
                if not exists:
                    score -= 1.0/len(values)

        return score

    def __top_ops_callback(self, amount, objects_list, sort_key, map_key, values):
        # Create sorted top K
        sorted_top_keys = list(map(map_key, sorted(objects_list, key=sort_key)[:min(len(objects_list), amount)]))

        # Calculate the top score
        # If !, then multiply by 0 or 1, if ? or no marker then remove 1/len from the final score
        score = 1.0
        for value in values:
            stripped_value = re.sub('^(!|\\?|~)', '', value)
            if value.startswith('!'):
                if not stripped_value in sorted_top_keys:
                    score *= 0.0
                    break
            elif value.startswith('~'):
                if not stripped_value in sorted_top_keys:
                    score *= TILDA_FACTOR
            else:
                if not stripped_value in sorted_top_keys:
                    score -= 1.0/len(values)
        return score

    def __recursive_structure_rules(self, repo, definition, curr_path, parts):
        hits = defaultdict(list)
        # Check if path exists
        if os.path.exists(curr_path):
            hits[curr_path].append(True)
            # Since it exists, we can move forward, make sure there are more parts
            if len(parts) > 0:
                # Get the next part to add to the path
                next_part = parts.pop(0)
                many_parts = []
                # Split the part if many is specified
                if 'MANY' in next_part:
                    many_partitioned_str = next_part.partition('MANY')
                    values_str = re.sub('\\(|\\)', '', many_partitioned_str[2])
                    many_parts = many_parts + [many_partitioned_str[0] + value.strip() for value in values_str.split(',')]
                else:
                    many_parts.append(next_part)
                # Check if the part has wildcards
                for part in many_parts:
                    if '*' in part:
                        # List the current path and check if any folder / file meets the given regex wildcard
                        wildcard_next_path = os.path.join(curr_path, part)
                        for file in os.listdir(curr_path):
                            checked_path = os.path.join(curr_path, file)
                            match = fnmatch.fnmatch(checked_path, wildcard_next_path)

                            if match:
                                # Found a valid path, recurse it
                                hits_res = self.__recursive_structure_rules(repo, definition, checked_path, parts)
                                for i,j in hits_res.items():
                                    hits[i].extend(j)
                            else:
                                hits[checked_path].append(False)
                    else:
                        # Just concat the part and recursive call
                        next_path = os.path.join(curr_path, part)
                        hits_res = defaultdict(list, self.__recursive_structure_rules(repo, definition, next_path, parts))
                        for i,j in hits_res.items():
                            hits[i].extend(j)
        else:
            hits[curr_path].append(False)
        return hits

    def __structure_rules_defs_callback(self, repo, definition):
        # Two opts:
        #   Full path each given tree item, and recursive on the entire file structure, check if every item has a regex in the tree items
        #       This is hits overall
        #   Go over every tree item, if a part has a wildcard, try and list everything in the path so far that fits the path and the wildcards
        #       This is hits per slash
        #       Every path addition check if that path exists, and for every wildcard fit, go inside it aswell

        # Take the tree rules and score them based on hit count
        # Note that ** are treated as all the folders recursive and * means one step
        repo_root_path = repo['path']

        final_score = 0.0

        # Go over each tree item
        for tree_item in definition['tree_rules']:
            # Divide it into path parts
            norm_tree_path = os.path.normpath(tree_item)
            path_parts = norm_tree_path.split(os.sep)

            # Recursive hits
            hits = self.__recursive_structure_rules(repo, definition, repo_root_path, path_parts)
            # Erase the first since its the repo itself, doesnt matter
            del hits[repo_root_path]

            # Calculate score for this tree item
            weight = 1.0/len(definition['tree_rules'])
            hit_count_factor = len(list(filter(lambda x: True in x, hits.values()))) / len(hits)
            final_score = final_score + (weight * hit_count_factor)
            
        return final_score

    def __files_req_callback(self, repo, req):
        operation = req['operation']

        repo_root_path = repo['path']

        if operation == 'exists':
            return self.__ops_callbacks[operation](repo_root_path, req['values'], False)

        return 0.0

    def __folders_req_callback(self, repo, req):
        operation = req['operation']

        repo_root_path = repo['path']

        if operation == 'exists':
            return self.__ops_callbacks[operation](repo_root_path, req['values'], True)

        return 0.0

    def __languages_req_callback(self, repo, req):
        operation = req['operation']

        amount = req['operation_params']['amount']
        langs_list = repo['languages']
        sort_key = lambda x: x['size']
        map_key = lambda x: x['name']
        values = req['values']

        if operation == 'top':
            return self.__ops_callbacks[operation](amount, langs_list, sort_key, map_key, values)

        return 0.0

    def __extensions_req_callback(self, repo, req):
        # Get the repo path and recursive tail it
        repo_path = repo['path']

        extensions_dict = {}
        for root, dirs, files in os.walk(repo_path):
            for name in files:
                fname, ext = os.path.splitext(name)
                if ext not in extensions_dict.keys():
                    extensions_dict[ext] = 1
                else:
                    extensions_dict[ext] = extensions_dict[ext] + 1 

        operation = req['operation']
        
        extensions_list = list(extensions_dict.items())
        amount = req['operation_params']['amount']
        sort_key = lambda x: x[1]
        map_key = lambda x: x[0]
        values = req['values']

        if operation == 'top':
            return self.__ops_callbacks[operation](amount, extensions_list, sort_key, map_key, values)

        return 0.0

    def __get_repo_frameworks(self, repo):
        # In order to get the project frameworks we need to do the following:
        #   Each framework is defined by a meta json
        #   We run over all the known frameworks and check if any of the ueser's repos meet the requirements

        # List all the frameworks files
        TEMP_PATH = 'octopus\\profiler\\ap_profilers\\github\\frameworks'
        framework_files = [os.path.join(TEMP_PATH, subdir) for subdir in os.listdir(TEMP_PATH)
                                                           if os.path.isfile(os.path.join(TEMP_PATH, subdir))] 

        frameworks = []
        for framework in framework_files:
            # Open the framework
            with open(framework, 'r') as f:
                # Sanitize the json first
                data = JSONSanitizer.sanitize_string_by_dict(f.read(), 'repo', repo)

                # Load the json
                framework_json = json.loads(data)

                # Get the requirements
                framework_reqs = framework_json['framework_requirements']

                # Assert them according to the types
                current_score = 1.0
                for req in framework_reqs:
                    if req['type'] in self.__req_callbacks.keys():
                        current_score = current_score * self.__req_callbacks[req['type']](repo, req)
                if current_score >= DEFAULT_MIN_FW_SCORE:
                    frameworks.append(framework_json)

        return frameworks

    def __get_repo_framework_score(self, repo, framework):
        # Go over the framework definition, and score each one based on the callback
        final_score = 0.0

        for definition in framework['framework_definitions']:
            if definition['type'] in self.__defs_callbacks.keys():
                final_score = final_score + self.__defs_callbacks[definition['type']](repo, definition)

        return final_score / len(framework['framework_definitions'])

    def analyze_repo_frameworks(self, repo):
        # Get the frameworks that were found for the repo
        frameworks = self.__get_repo_frameworks(repo)

        # Get score for each framework
        framework_scores = {}
        for framework in frameworks:
            framework_scores[framework['name']] = self.__get_repo_framework_score(repo, framework)

        return framework_scores
