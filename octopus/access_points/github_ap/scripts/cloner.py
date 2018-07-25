import subprocess
import re
from argparse import ArgumentParser
import sys
import os
from git import Git
import git

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

def __get__HEAD__(branches):

    for branch in branches:
        idx = branch.find('HEAD')
        name_idx = branch.rfind('/')
        branch = branch[name_idx + 1:]
        not_head = -1
        if idx != not_head:
            return branch

    # no HEAD
    return None

def __parse__branch__(branch):
    if len(branch) < 1:
        return ''
    idx = branch.find('HEAD')
    name_idx = branch.rfind('/')
    branch = branch[name_idx+1:]
    not_head = -1
    regex = re.compile('[^\w\\-\\.]')
    branch = regex.sub('', branch)
    return branch

def __parse__branches__(branches):
    parsed = branches.decode('utf-8').split('\n')

    head = __parse__branch__(__get__HEAD__(parsed))

    parsed = [__parse__branch__(b) for b in parsed]

    parsed = [b.strip() for b in parsed]
    parsed = [b for b in parsed if b]
    parsed.append(head)
    parsed = set(parsed)
    parsed = [__to__object__(b,head) for b in parsed]
    return list(parsed)

def __to__object__(branch_name,head):
    if branch_name == head:
        return {'is_head': True, 'name' : branch_name}
    return {'is_head': False, 'name' : branch_name}
def get_all_branches(path):
    try:
        cmd = ['git', '-C', path, 'branch', '-a']
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return __parse__branches__(out)
    except Exception as e:
        print(e)
        return None

def get_branches(path):
    os.chdir(path)

    ## end new
    branches = []
    try:
        g = Git()
        branches = g.branch()

        print('branches object {}'.format(branches.replace('g','')))
        names = branches.split(' ')
        print(names)

    except Exception as e:
        print(e)


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


