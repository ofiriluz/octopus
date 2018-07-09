import json
import os
import pprint
import re

class GithubFrameworkAnalyzer:
    def __init__(self):
        self.__req_callbacks = {
            'files': self.__files_req_callback,
            'folders': self.__folders_req_callback,
            'languages': self.__languages_req_callback,
            'extensions': self.__extensions_req_callback
        }

        self.__defs_callbacks = {
            'structure_rules': self.__structure_rules_defs_callback
        }

    def __recursive_structure_rules(self, repo, definition, curr_path, parts):
        hits = []
        # Check if path exists
        if os.path.exists(curr_path):
            hits.append((curr_path, True))
            # Since it exists, we can move forward, make sure there are more parts
            if len(parts) > 0:
                # Get the next part to add to the path
                next_part = parts.pop(0)
                # Check if the part has wildcards
                if '*' in next_part:
                    # List the current path and check if any folder / file meets the given regex wildcard
                    wildcard_next_path = os.path.join(curr_path, next_part)
                    # Switch the wildcards with .* for regex
                    wildcard_next_path = wildcard_next_path.replace('*', '.*')

                    for file in os.listdir(curr_path):
                        checked_path = os.path.join(curr_path, file)
                        if re.match()

                else:
                    # Just concat the part and recursive call
                    next_path = os.path.join(curr_path, next_part)
                    self.__recursive_structure_rules(repo, definition, next_path, parts)
        else:
            hits.append((curr_path, False))
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

        # Go over each tree item
        for tree_item in definition['tree_rules']:
            # Divide it into path parts
            norm_tree_path = os.path.normpath(tree_item)
            path_parts = norm_tree_path.split(os.sep)

            # Start going over the parts and create a list of paths to assert
            hits = self.__recursive_structure_rules(repo, definition, repo_root_path, path_parts)
            # for path_part in path_parts:
            # Check if wildcard exists on the path part and handle it
                


    def __files_req_callback(self, repo, req):
        repo_root_path = repo['path']

        # Check if each given file exists
        exists = True
        for file_val in req['values']:
            file_path = os.path.join(repo_root_path, file_val)
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                exists = False
                break
        return exists 

    def __folders_req_callback(self, repo, req):
        repo_root_path = repo['path']

        # Check if each given folder exists
        exists = True
        for folder_val in req['values']:
            folder_path = os.path.join(repo_root_path, folder_val)
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                exists = False
                break
        return exists

    def __languages_req_callback(self, repo, req):
        # Check if the repo has the given languages on the top K+3
        amount = req['operation_params']['amount']

        # Sort the langs by their sizes
        sorted_langs = sorted(repo['languages'], key=lambda x: x['size'])

        # Take top K
        sorted_langs = sorted_langs[:min(len(repo['languages'], amount))]

        # Check if sublist
        return all(lang in sorted_langs for lang in req['values'])

    def __extensions_req_callback(self, repo, req):
        # Get the repo path and recursive tail it
        repo_path = repo['path']
        amount = req['operation_params']['amount']

        extensions_dict = {}
        for root, dirs, files in os.walk(repo_path):
            for name in files:
                fname, ext = os.path.splitext(name)
                if ext not in extensions_dict.keys():
                    extensions_dict[ext] = 1
                else:
                    extensions_dict[ext] = extensions_dict[ext] + 1 
        # Create tuple list and sort it by sizes
        sorted_exts = sorted(list(extensions_dict.items()), lambda x: x[1])

        # Take top K
        sorted_exts = sorted_exts[:min(len(sorted_exts), amount)]

        # Check if sublist
        return all(lang in sorted_exts for lang in req['values'])

    def __get_repo_frameworks(self, repo):
        # In order to get the project frameworks we need to do the following:
        #   Each framework is defined by a meta json
        #   We run over all the known frameworks and check if any of the ueser's repos meet the requirements

        # List all the frameworks files
        framework_files = [os.path.join('frameworks', subdir) for subdir in os.listdir('frameworks')
                                                           if os.path.isfile(os.path.join('frameworks', subdir))] 

        frameworks = []
        for framework in framework_files:
            # Open the framework
            with open(framework, 'r') as f:
                framework_json = json.load(f)

                # Get the requirements
                framework_reqs = framework_json['framework_requirements']

                # Assert them according to the types
                allowed = True
                for req in framework_reqs:
                    if req in self.__req_callbacks.keys():
                        fw_res = self.__req_callbacks[req](repo, req)
                        if not fw_res:
                            if not req['assert']:
                                continue
                            allowed = False
                            break
                if allowed:
                    frameworks.append(framework)

        return frameworks

    def __get_repo_framework_score(self, repo, framework):
        # Go over the framework definition, and score each one based on the callback
        

    def analyze_repo_frameworks(self, repo):
        # Get the frameworks that were found for the repo
        frameworks = self.__get_repo_frameworks(repo)

        pprint.pprint(frameworks)

        # Get score for each framework
        framework_scores = {}
        for framework in frameworks:
            framework_scores[framework['name']] = self.__get_repo_framework_score(repo, framework)

        pprint.pprint(framework_scores)

        return framework_scores