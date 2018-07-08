import subprocess
from argparse import ArgumentParser
import sys

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

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
                            const=True, help="Activate nice mode.")

        args = parser.parse_args()

        is_bear = args.bear
        target = args.target_repo_dir
        remote = args.remote_repo_url


        if is_bear:
            subprocess.call(['git', 'clone', remote, '--bare', target])
        else:
            subprocess.call(['git', 'clone', remote, target])

    except:
        print('[Err] in cloner.py')
        sys.exit(1)


