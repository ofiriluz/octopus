import subprocess
from argparse import ArgumentParser
import sys
import os
from git import Git

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def clone_repo(remote,target,is_bear):

    if is_bear:
        subprocess.call(['git', 'clone', remote, '--bare', target])
    else:
        subprocess.call(['git', 'clone', remote, target])

def get_branches(path):
    os.chdir(path)
    branches = []
    try:
        g = Git()
        branches = g.branch()
        #branches = subprocess.check_output(['git', 'branch','-a'])
        print('branches object {}'.format(branches.replace('g','')))
        names = branches.split(' ')
        print(names)
        for branch in branches:
            print('###########')
            print(branch)
    except Exception as e:
        print(e)

    print('mkay?')

if __name__ == "__main__":
    '''
        This script simply clones or clone --bare the a repo.
        inputs: 
        @-r : remote repo url 
        @-o : target path to store the repo 
        @-b optional --bare, by default set to true 
        ============================================
        The script will clone the repo and store it in the dir.
        in case of an error will exit with the code 1
    '''
    try:
        parser = ArgumentParser()

        parser.add_argument("-r", "--remote", dest="remote_repo_url",
                            help="URL of the remote repository", metavar="URL")

        parser.add_argument("-o", "--out", dest="target_repo_dir",
                            help="The target dir to store the repo", metavar="PATH")

        parser.add_argument("-b", "--bare",dest="bear", type=str2bool, nargs='?', default=True,
                            const=True, help="Activate bare mode.")

        parser.add_argument("--all", dest="is_all_branches", type=str2bool, nargs='?', default=False,
                            const=True, help="Clone all branchs.")

        args = parser.parse_args()

        is_bear = args.bear
        target = args.target_repo_dir
        remote = args.remote_repo_url
        is_all_branches = args.is_all_branches
        if is_all_branches:
            get_branches(target)
        else:
            clone_repo(remote, target, is_bear)

    except:
        print('[Err] in cloner.py')
        sys.exit(1)


