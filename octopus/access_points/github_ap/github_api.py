from github import Github
from octopus.access_points.auth_keys import GITHUB_PERSONAL_ACCOESS_TOKEN
from octopus.access_points.utils.util import Util

class GithubUser(object):
    def __init__(self):
        pass


class GithubAPI(object):

    def __init__(self,token):

        self.g = Github(token)

    # input: search query (i.e a user name)
    # output: a list of user objects
    def search(self,query):
        users = [self.g.get_user(user.login) for user in self.g.search_users(query)]
        return users

    # input: a user object
    # output : user repositories
    def get_repos(self, user):
        return self.__build_repositories(user.get_repos())

    def __build_repositories(self,repos):
        repositoroes = []
        for repo in repos:
            repositoroes.append({
                'name' : repo.name,
                # not enough it only represents 1 language for example in a nodejs project it could show only HTML
                'view_language' : repo.language,
                # the current repo owner (if its fork then the forker is the owner
                'current_owner' : repo.owner.login,
                # the parent owner if it's forke then it's the the owner original
                'parent_owner' :  repo.parent if repo.parent is not None else None,
                # ?
                'pushed_at' : repo.pushed_at,
                # watchers count
                'watchers_count' : repo.watchers_count,
                # is this repo a fork ?
                'is_fork' : repo.fork,
                # did anyone fork this repo ?
                'forkes_count' : repo.forks_count,
                # clone url
                'clone_url' : repo.clone_url
            })
        return repositoroes


###https://github.com/PyGithub/PyGithub
# or using an access token
g = Github(GITHUB_PERSONAL_ACCOESS_TOKEN)

def test1():
    # Then play with your Github objects:
    # for repo in g.get_user().get_repos():
    #     print(repo.name)

    users = g.search_users('isan_rivkin')
    for u in users:
        print(u.login)
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
            if repo.parent is not None:
                print(repo.parent)
            # pushed at
            print(repo.pushed_at)
            # watchers count
            print(repo.watchers_count)
            # is this repo  a fork ?
            print(repo.fork)
            # did anyone fork this repo ?
            print(repo.forks_count)

        print('repos #{}'.format(count))


if __name__ == "__main__":
    #TODO:: extract this https://api.github.com/users/Isan-Rivkin/repos url == repos object below (same same)
    #TODO : createt a normal repo obj with metadata and code
    #TODO : seperate the data object into user, repos (ea repo: owner, meta, code)

    api = GithubAPI(GITHUB_PERSONAL_ACCOESS_TOKEN)
    user_name = 'isan_rivkin'
    users = api.search(user_name)
    for u in users:
        repos = api.get_repos(u)
        Util.pretty_print_dict(repos[0])
        print('user {} , repos # {}'.format(u.name,len(repos)))