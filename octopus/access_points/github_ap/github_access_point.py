from octopus.access_points.access_point import AccessPoint


class GithubAccessPoint(AccessPoint):
    def __init__(self):
        pass

    def resolve_query(self, logger, query, controllers):
        logger.info('Hello World')
        return {}











# from github_api import GithubAPI

# from octopus.access_points.auth_keys import GITHUB_PERSONAL_ACCOESS_TOKEN
# from octopus.access_points.github_ap.scripts.cloner import *
# from octopus.access_points.github_ap.scripts.commits_dif import *
# import subprocess
# from argparse import ArgumentParser
# import sys

# def str2bool(v):
#     if v.lower() in ('yes', 'true', 't', 'y', '1'):
#         return True
#     elif v.lower() in ('no', 'false', 'f', 'n', '0'):
#         return False
#     else:
#         raise argparse.ArgumentTypeError('Boolean value expected.')

# def init_parser():
#     parser = ArgumentParser()

#     parser.add_argument("-u", "--user", dest="user_name",
#                         help="Github user name", metavar="USERNAME")

#     parser.add_argument("-f", "--full", dest="full_repos", type=str2bool, nargs='?', default=False,
#                         const=True, help="default=false, full repos download (=True) or bare (=False).")

#     parser.add_argument("-o", "--out", dest="target_repo_dir",
#                         help="The target dir to store the data", metavar="PATH")


#     parser.add_argument('-s',"--size-limit", type=int,dest="size_limit", default=0,
#                         help="limit the allowed size for a repo", metavar="REPO_SIZE")

#     return parser.parse_args()


# if __name__ == '__main__':

#     '''
#     @input: user name, full_repo clones?, target path, limit repo size
#     '''
#     parser = init_parser()

#    '''
#    @ --------------- part A --------------- 
#    @ -- This section is reponsible for gettig all the data in a raw form. 
#    @ -- It is responsible for prepearing the raw data for parsin in Part B. 
#    @ -- First, fetch all the meta-info  organized in some way. 
#    @ -- Second, heuristics that cross multiple requests and manipulate the data  
#    '''

