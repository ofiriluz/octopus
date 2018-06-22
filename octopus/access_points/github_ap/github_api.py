from github import Github
from octopus.access_points.auth_keys import GITHUB_PERSONAL_ACCOESS_TOKEN

###https://github.com/PyGithub/PyGithub
# or using an access token
g = Github(GITHUB_PERSONAL_ACCOESS_TOKEN)

if __name__ == "__main__":

    # Then play with your Github objects:
    # for repo in g.get_user().get_repos():
    #     print(repo.name)


    users = g.search_users('isan rivkin')
    for u in users:
        print(u.login)
        repos = g.get_user(u.login).get_repos()
        count = 0
        for repo in repos:
            count += 1
            print(repo.name)
            print(repo.language)
            # the current repo owner (if its fork then the forker is the owner
            print(repo.owner.login)
            # the parent owner if it's forke then it's the the owner original
            print(repo.owner.parent)
            # pushed at
            print(repo.pushed_at.datetime)
            # watchers count
            print(repo.watchers_count)
            # is this repo  a fork ?
            print(repo.fork)
            # did anyone fork this repo ?
            print(repo.forks_count)

        print('repos #{}'.format(count))
