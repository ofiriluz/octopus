
import os, sys
from os.path import expanduser

class Input(object):
    '''
    Input:
        - id
        - user name
        - mode : {light,full}
        - target_dir
        - repo_size_limit : {0, any num}
        - repos_list : ['all']
        - repos_ignore : ['some_repo_to_ignore']
        - repos_num : {0, any num}
        - branches_num : {0,any num},
        - branches_names : ['all', 'master', 'develop',...]
    '''
    def __init__(self, input):

        self.input = input
        self.root_dirs = []
        self.root_files = []
        if not os.path.exists(self.target_dir()):
            raise ValueError('No such workspace {}.'.format(self.target_dir()))

    # store the input into a json => target_dir/input.json
    def id(self):
        return self.input['id']

    def is_full_mode(self):
        return self.input['mode'] == 'full'

    def is_light_mode(self):
        return self.input['mode'] == 'light'
    def mode(self):
        return self.input['mode']

    def user_name(self):
        return self.input['user_name']

    def mode(self):
        return self.input['mode']

    def target_dir(self):
        return self.input['target_dir']

    def repo_size_limit(self):
        return self.input['repo_size_limit']

    def branches_num(self):
        return self.input['branches_num']

    def branches_names(self):
        return self.input['branches_names']

    def repos_list(self):
        return self.input['repos_list']

    def repos_num(self):
        return self.input['repos_num']

    ''' all dir related methods '''
    # path/id
    def profile_dir(self):
        result_dir = os.path.join(self.target_dir(),self.id())
        return result_dir
    # path/id/repositories
    def repos_high_dir(self):
        result_dir = os.path.join(self.profile_dir(), 'repositories')
        return result_dir

    # path/id/repositories/repositories
    def repos_dir(self):
        result_dir = os.path.join(self.repos_high_dir(),'repositories')
        return result_dir

    # path/id/repositories/repositories/{name}
    def repo_by_name_high_dir(self,name,create = False):
        result_dir = os.path.join(self.repos_dir(),name)

        if create:
            os.makedirs(result_dir)

        return result_dir

    # path/id/repositories/repositories/{repo_name}/{repo_name}
    def clone_dir(self,repo_name,create = False):

        result_dir = os.path.join(self.repo_by_name_high_dir(repo_name),repo_name)

        if create:
            os.makedirs(result_dir)

        return result_dir

    # path/id/repositories/repositories/{repo_name}/commits
    def commits_dir(self,repo_name, create = False):
        result_dir = os.path.join(self.repo_by_name_high_dir(repo_name), 'commits')
        if create and not os.path.exists(result_dir):
            os.makedirs(result_dir)
        return result_dir

    # path/id/profile_meta.json
    def profile_meta_path(self):
        return os.path.join(self.profile_dir(),'profile_meta.json')

    # path/id/input_meta.json
    def input_meta_path(self):
        return os.path.join(self.profile_dir(), 'input_meta.json')

    # path/id/repositories/repositories_meta.json
    def repos_high_meta(self):
        return os.path.join(self.repos_high_dir(), 'repositories_meta.json')

    #  path/id/repositories/repositories/{name}/{name}_meta.json
    def repo_meta(self,repo_name, create = False):
        # path/id/repositories/repositories/{name}
        repo = self.repo_by_name_high_dir(repo_name,create=False)
        if create:
            os.makedirs(repo)

        result_dir = os.path.join(repo, repo_name + '_meta.json')
        if create:
            self.__touch__(result_dir)

        return result_dir

    def generate_target(self):

        # move to the workspace
        os.chdir(self.target_dir())
        # create id folder + profile.json
        profile = self.profile_meta_path()
        self.__touch__(profile)
        # crate input.json
        input = self.input_meta_path()
        self.__touch__(input)
        # repository meta.json
        repos = self.repos_high_meta()
        self.__touch__(repos)


    def __touch__(self,filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write("")


            '''
            Input:
                - id
                - user name
                - mode : {light,full}
                - target_dir
                - repo_size_limit : {0, any num}
                - repos_list : ['all']
                - repos_num : {0, any num}
                - branches_num : {0,any num},
                - branches_names : ['all', 'master', 'develop',...]
            '''

if __name__ == "__main__":
    input = {}
    input['id'] = 'hello_world_ws'
    input['mode'] = 'full'
    input['target_dir'] = '/home/wildermind/PycharmProjects/octopus/octopus/access_points/github_ap/scripts'
    input['repo_size_limit'] = 0
    input['branches_num'] = 0
    input['branches_names'] = ['all']
    input['user_name'] = 'isan_rivkin'
    input['branches_num'] = 0
    input['branches_names'] = ['all']
    input = Input(input)
    input.generate_target()
























