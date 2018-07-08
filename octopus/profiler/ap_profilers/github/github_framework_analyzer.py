import json
import os
import pprint

class GithubFrameworkAnalyzer:
    def __init__(self):
        self.__req_callbacks = {
            'files': self.__files_req_callback,
            'folders': self.__folders_req_callback,
            'languages': self.__languages_req_callback,
            'extensions': self.__extensions_req_callback
        }

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

    def __get_master_branch(self, repo):
        return next((branch for branch in repo['branches'] if branch['name'] == 'master'))

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
        pass

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