from github import Github
from octopus.access_points.auth_keys import GITHUB_PERSONAL_ACCOESS_TOKEN
# First create a Github instance:

# or using an access token
g = Github(GITHUB_PERSONAL_ACCOESS_TOKEN)

if __name__ == "__main__":

    # Then play with your Github objects:
    # for repo in g.get_user().get_repos():
    #     print(repo.name)


    users = g.search_users('isan rivkin')
    for u in users:
        print(u.login)
        