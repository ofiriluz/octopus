import requests
import json
from github import Github
from octopus.access_points.auth_keys import GITHUB_PERSONAL_ACCOESS_TOKEN
from octopus.access_points.utils.util import Util
from octopus.access_points.github_ap.types_cake import Input
from octopus.access_points.github_ap.scripts.cloner import clone_repo,get_branches,get_all_branches
from octopus.access_points.github_ap.scripts.commits_dif import versions,checkout_to


class GithubAPI(object):

    def __init__(self,token):
        self.input = {}
        self.g = Github(token)
        self.with_https = False

    def __with__https(self,url):
        if self.with_https:
            return url
        url = url.replace("https", "http")
        print('new url {}'.format(url))
        return url

    # input: search query (i.e a user name)
    # output: a list of user objects
    def search(self,query):
        print('get HERE @#%$#^#%@$')
        users = [self.g.get_user(user.login) for user in self.g.search_users(query)]
        print('AND HERE #@$#%Y^UTRYTEWRTRYGRYETR')
        return users
    # get all commits metadata
    # https://api.github.com/repos/ofiriluz/octopus/commits
    # it returnes some branches, checked enigma-core and found master and develop commits there but not other branches.
    def get_commits_metadata(self, profile_name, repo_name):

        url = 'https://api.github.com/repos/'+ profile_name + '/' + repo_name + '/commits'
        url = self.__with__https(url)
        response = requests.get(url)
        if response.status_code == 200:
            return [self.__build_commit_metadata(c) for c in response.json()]
        else:
            return None

    def __build_commit_metadata(self,commit):
        parsed_commit = {}
        # login github user
        parsed_commit['login'] = commit['author']['login']
        # the human nickname
        parsed_commit['full_name'] = commit['commit']['author']['name']
        # commiter email => important because the commit logs has only email
        parsed_commit['email'] = commit['commit']['author']['email']
        # the date of the commit
        parsed_commit['date'] = commit['commit']['author']['date']
        # the commit message
        parsed_commit['meesage'] = commit['commit']['message']
        # the commit id == sha
        parsed_commit['id'] = commit['sha']
        return parsed_commit

    # input: a user object
    # output : user repositories
    def get_repos(self, user):
        return self.__build_repositories(user.get_repos())
    # get user profile metadata https://api.github.com/users/Isan-Rivkin
    # !!! IMPORTANT !!! this function expects an existing Github name it does not perform search
    def get_user_profile(self,username, url_profile ='https://api.github.com/users/'):
        url = url_profile + username
        url = self.__with__https(url)
        response = requests.get(url)

        if response.status_code == 200:

            json_format = json.loads(response.text)
            json_format['status_code'] = response.status_code
            parsed_profile = self.__build_user_profile(json_format)
            return parsed_profile
        else:

            return None

    # build user profile metadata
    def __build_user_profile(self,raw_profile):
        return {
            "login": raw_profile['login'],
            "avatar_url": raw_profile['avatar_url'],
            "url": raw_profile['url'],
            "followers_url": raw_profile['followers_url'],
            "following_url": raw_profile['following_url'],
            "gists_url": raw_profile['gists_url'],
            "starred_url": raw_profile['starred_url'],
            "subscriptions_url": raw_profile['subscriptions_url'],
            "organizations_url": raw_profile['organizations_url'],
            "repos_url": raw_profile['repos_url'],
            "events_url": raw_profile['events_url'],
            "received_events_url": raw_profile['received_events_url'],
            "type": raw_profile['type'],
            "name": raw_profile['name'],
            "company": raw_profile['company'],
            "location": raw_profile['location'],
            "email": raw_profile['email'],
            "hireable": raw_profile['hireable'],
            "bio": raw_profile['bio'],
            "public_repos": raw_profile['public_repos'],
            "public_gists": raw_profile['public_gists'],
            "followers": raw_profile['followers'],
            "following": raw_profile['following'],
            "created_at": raw_profile['created_at'],
            "updated_at": raw_profile['updated_at']
        }

    # build dictionary from https://api.github.com/users/Isan-Rivkin/repos
    def __build_repositories(self,repos):
        repositoroes = []
        for repo in repos:
            repositoroes.append({
                # repo url
                'url' : repo.html_url,
                # Sokoban
                'name': repo.name,
                # Isan-Rivkin/Sokoban
                'full_name': repo.full_name,
                # owner info
                'owner': {
                    # profile metadata => covers all metadata about profile https://api.github.com/users/Isan-Rivkin
                    'profile_url' : repo.owner.url,
                    # type organization or User
                    'type': repo.owner.type,
                    # meta-data about all the owners repos
                    'repos_url': repo.owner.repos_url,
                    # the current repo owner (if its fork then the forker is the owner
                    'current_owner': repo.owner.login,
                    # organizations url
                    'organizations_url': repo.owner.organizations_url,
                    # the parent owner if it's forke then it's the the owner original
                    'parent_owner': repo.parent if repo.parent is not None else None
                },
                # size of the repo in bytes
                'size' : repo.size,
                # issues url + number [1...to issue num] will return all data regarding the issue
                # https://api.github.com/repos/ofiriluz/octopus/issues/1
                'issues_url': repo.issues_url,
                # boolean : defines if the user enabled issue for the repo
                'has_issues': repo.has_issues,
                # number of open issue
                'open_issues' : repo.open_issues,
                # url get all the languages that are used by the repo
                # key = language name , value = size in bytes
                'languages' : repo.languages_url,
                # the last commit=update date in the repo, each commit will recieve new date
                'pushed_at' : repo.pushed_at,
                # created at initially
                'created_at' : repo.created_at,
                # watchers count
                'watchers_count' : repo.watchers_count,
                # is this repo a fork ?
                'is_fork' : repo.fork,
                # did anyone fork this repo ?
                'forkes_count' : repo.forks_count,
                # clone url
                'clone_url' : repo.clone_url,
                # commits url
                'commits_url' : repo.commits_url,
                # default_branch (master)
                'default_branch': repo.default_branch,
                # the actuall programming languages type->size
                # to be filled later in the process
                'languages_dict' : None
            })
        return repositoroes

    # build the request
    # input: dictionary input from the client
    # - store the input
    # - create the source dir with the id at the target dir
    # - set the api states

    def build(self,input):
        self.input = Input(input)
        self.input.generate_target()

    def run(self):
        # store the input file
        self.__handle__input__file__()

        users = self.search(self.input.user_name())
        print('search returned #{} users.'.format(len(users)))
        for u in users:
            full = {}
            header = {}
            body = {}

            # user profile name
            login = u.login
            print('[+] Starting fetch process for {}'.format(login))
            header['profile'] = self.get_user_profile(login)

            # store profile meta data
            self.__handle__user__profile__(header['profile'])

            # get user repos metadata
            body['repositories']  = self.get_repos(u)
            #TODO:: create a meta file for all repos with general info like amout of repos and names repositories_meta.json

            for repo in body['repositories']:
                self.__handle__repo__(repo, login)


    # git clone repo
    # clone branches
    def __handle__repo__(self,repo, profile_name):
        print('[+] Starting repo process for {}'.format(repo['name']))

        # repo too big
        if repo['size'] != 0 and self.input.repo_size_limit() > repo['size']:
            return None

        #TODO::1 refactor the code to use filters instead of small bits of params with if else.
        #TODO::2 allow a sequential mode where it is possible to clone repo and then filter if it's bad and delete
        #TODO:: this will help in case where the whole repo's are too big.
        '''
        - 
        - running the access point in a full mode
        '''
        if self.input.is_full_mode():

            # store meta-data for each repo
            self.__handle__repo__meta__(repo)

            # git clone repo
            print('[+] cloning repository {}'.format(repo['name']))
            clone_dir = self.input.clone_dir(repo['name'],create = True)
            print('clone dir moeon {}'.format(clone_dir))
            clone_repo(
                repo['url'],
                clone_dir ,
                is_bear = False)

            # TODO:: add to repo_name_meta.json the branches list
            # - get branch name
            # - handle commits logic
            # - for each branch execute the following:
            # - if branch is_interesting(filter):
            #   - git checkout branch
            # - for each checkout branch:
            #   - analyze and dump commits into branch_name_commits.json

            # branches = self.get_branches_list( clone_dir)
            # # TODO:: store into file commits_meta inside /repo_name/commits/commits_meta.json
            # #commits_meta = self.get_commits_metadata(profile_name, input['name'])
            #
            # for branch in branches:
            #
            #     self.__handle__branches__(repo['name'],clone_dir,branch)

        elif self.input.is_light_mode():
            pass
        return self

    def __handle__branches__(self, repo_name,repo_path, branch_name):

        if self.__is__interesting__branch(repo_path,branch_name):

            print('[+] Handling branch {} for repo {}'.format(branch_name,repo_name))

            # checkout the branch
            checkout_to(repo_path,branch_name)
            # calls a script inside commits_diff.py to analyze commits
            commits_stats = versions(repo_path,branch_name)
            # save the commits in the target dir /repo_name/commits/branch_name_commits.json
            commits_dir = self.input.commits_dir(repo_name, create = True)
            target_file = os.path.join(commits_dir,branch_name+'_commits.json')

            with open(target_file, 'w') as outfile:
                json.dump(commits_stats, outfile, indent=4)

    def __is__interesting__branch(self, repo_path, branch_name):
        # TODO:: This method should use a filter that was input by the requester. in self.input['branch_filter']
        return True

    def __handle__repo__meta__(self,repo):
        meta_file = self.input.repo_meta(repo['name'],create=True)
        repo['pushed_at'] = str(repo['pushed_at'])
        repo['created_at'] = str(repo['created_at'])

        # fetch the language dictionary from repo['languages'] url
        repo = self.__handle__repo__language__(repo)

        with open(meta_file, 'w') as outfile:
            json.dump(repo, outfile,  indent= 4)

    def __handle__repo__language__(self,repo):
        url = repo['languages']
        self.__with__https(url)
        response = requests.get(url)
        if url is not None and response.status_code == 200:
            repo['languages_dict'] = response.json()
            return repo
        else:
            print('[-] failed to fetch languages for {}'.format(repo['name']))
            return None

    def __handle__user__profile__(self,profile):

        meta_file = self.input.profile_meta_path()

        with open(meta_file, 'w') as outfile:
            json.dump(profile, outfile,  indent= 4)

    def __handle__input__file__(self):

        meta_file = self.input.input_meta_path()

        with open(meta_file, 'w') as outfile:
            json.dump(self.input.input, outfile,  indent= 4)

    def get_branches_list(self, path):
        res = get_all_branches(path)
        return res

    #TODO:: finish THE FULL PROCESS OF GETTING RAW DATA IS THIS FUNCTION
    def execute_fetching_process(self,username,repo_size_limit, mode = 'full'):
        users = self.search(username)
        print('search returned #{} users.'.format(len(users)))
        for u in users:

            header = {}
            body = {}
            # get user profile
            login = u.login
            print('[+] Starting fetch process for {}'.format(login))
            header['profile'] = self.get_user_profile(login)
            # get user repos metadata
            repositories = self.get_repos(u)
            # body['repositories] golds object of metainfo about each repo
            body['repositories'] = repositories
            # get commits meta-data
            for repo in repositories:
                if self.current_mode == 'light':
                    body['commits'] = self.get_commits_metadata(login,repo.name)
                elif self.current_mode == 'full':
                    return




###https://github.com/PyGithub/PyGithub
# or using an access token
#g = Github(GITHUB_PERSONAL_ACCOESS_TOKEN)

def test1():
    # Then play with your Github objects:
    # for repo in g.get_user().get_repos():
    #     print(repo.name)

    users = g.search_users('ofir iluz')
    for u in users:
        print(u.login)
        return u.login
        repos = g.get_user(u.login).get_repos()
        count = 0
        for repo in repos:
            print('==================================')
            count += 1
            print(repo.name)
            # not enough it only represents 1 language for example in a nodejs project it could show only HTML
            print(repo.language)
            # the current repo owner (if its fork then the forker is the owner
            print(repo.owner.login)
            # the parent owner if it's forke then it's the the owner original
            print("####################")
            if repo.parent is not None:
                print(repo.parent)
            print("####################")
            # pushed at
            print(repo.pushed_at)
            # watchers count
            print(repo.watchers_count)
            # is this repo  a fork ?
            print(repo.fork)
            # did anyone fork this repo ?
            print(repo.forks_count)

        print('repos #{}'.format(count))

def test_get_all_user_repos_meta(username):
    api = GithubAPI(GITHUB_PERSONAL_ACCOESS_TOKEN)
    user_name = username
    users = api.search(user_name)
    for u in users:
        repos = api.get_repos(u)
        Util.pretty_print_dict(repos[0])
        print('user {} , repos # {}'.format(u.name, len(repos)))

def test_get_user_profile(username):
    api = GithubAPI(GITHUB_PERSONAL_ACCOESS_TOKEN)
    response = api.get_user_profile(username=username)
    #print(response)
    return response

def test_get_commits_metadata(repo_name, profile_name):
    api = GithubAPI(GITHUB_PERSONAL_ACCOESS_TOKEN)
    json_commits = api.get_commits_metadata(profile_name,repo_name)
    for commit in json_commits:
        print(commit)
        print('-----------------------------')

def test_mix():
    name = test1()
    profile = test_get_user_profile(name)
    test_get_all_user_repos_meta(name)

    # print(profile)
    # commits = test_get_commits_metadata('octopus',name)

def test_input():
    input = {}
    input['id'] = 'hello_world_ws'
    input['mode'] = 'full'
    input['target_dir'] = 'D:\TESTS_OCTO'
    input['repo_size_limit'] = 0
    input['branches_num'] = 0
    input['branches_names'] = ['all']
    input['user_name'] = 'yardenmol'
    input['branches_num'] = 0
    input['branches_names'] = ['all']
    api = GithubAPI(GITHUB_PERSONAL_ACCOESS_TOKEN)
    # prepeare the api
    api.build(input)
    # run
    api.run()

def test_branches():
    api = GithubAPI(GITHUB_PERSONAL_ACCOESS_TOKEN)
    api.get_branches_list(None,'/home/wildermind/PycharmProjects/octopus/octopus/access_points/github_ap/scripts/all_junk/hello_world_ws/repositories/repositories/PlanWayManagerWebsite/PlanWayManagerWebsite')


def test_commits_stats():
    repo ='/home/wildermind/PycharmProjects/octopus/octopus/access_points/github_ap/scripts/all_junk/hello_world_ws/repositories/repositories/PlanWayManagerWebsite/PlanWayManagerWebsite'
    commits_stats = versions(repo, 'master')
    # yield
    l = [s for s in commits_stats]
    print(l)

if __name__ == "__main__":
    #test_branches()
    test_input()
    #test_commits_stats()

