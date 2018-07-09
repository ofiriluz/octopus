## Imports
import os
import git
from argparse import ArgumentParser
import pprint
import json
import sys

## Module Constants
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
EMPTY_TREE_SHA   = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def versions(path, branch='master'):
    """
    This function returns a generator which iterates through all commits of
    the repository located in the given path for the given branch. It yields
    file diff information to show a timeseries of file changes.
    """

    # Create the repository, raises an error if it isn't one.
    repo = git.Repo(path)

    # Iterate through every commit for the given branch in the repository

    for commit in repo.iter_commits(branch):

        # Determine the parent of the commit to diff against.
        # If no parent, this is the first commit, so use empty tree.
        # Then create a mapping of path to diff for each file changed.
        parent = commit.parents[0] if commit.parents else EMPTY_TREE_SHA
        diffs  = {
            diff.a_path: diff for diff in commit.diff(parent)
        }

        # The stats on the commit is a summary of all the changes for this
        # commit, we'll iterate through it to get the information we need.
        for objpath, stats in commit.stats.files.items():

            # Select the diff for the path in the stats
            diff = diffs.get(objpath)

            # If the path is not in the dictionary, it's because it was
            # renamed, so search through the b_paths for the current name.
            if not diff:
                for diff in diffs.values():
                    if diff.b_path == path and diff.renamed:
                        break

            # Update the stats with the additional information
            stats.update({
                'object': os.path.join(path, objpath),
                'commit': commit.hexsha,
                'author': commit.author.email,
                'timestamp': commit.authored_datetime.strftime(DATE_TIME_FORMAT),
                'size': diff_size(diff),
                'type': diff_type(diff),
            })

            yield stats


# initial
# def diff_size(diff):
#     """
#     Computes the size of the diff by comparing the size of the blobs.
#     """
#     if diff.b_blob is None and diff.deleted_file:
#         # This is a deletion, so return negative the size of the original.
#         return diff.a_blob.size * -1
#
#     if diff.a_blob is None and diff.new_file:
#         # This is a new file, so return the size of the new value.
#         return diff.b_blob.size
#
#     # Otherwise just return the size a-b
#     return diff.a_blob.size - diff.b_blob.size



# this script waas modified due to mistake with the deleted and new files => it's OK and working now :)

def diff_size(diff):
    """
    Computes the size of the diff by comparing the size of the blobs.
    """
    if diff.b_blob is None and diff.deleted_file:
        # This is a new file, so return the size of the new value.
        return diff.a_blob.size

    if diff.a_blob is None and diff.new_file:
        # This is a deletion, so return negative the size of the original.
        return diff.b_blob.size * -1

    # Otherwise just return the size a-b
    return diff.a_blob.size - diff.b_blob.size


def diff_type(diff):
    """
    Determines the type of the diff by looking at the diff flags.
    """
    if diff.renamed: return 'R' # renaming of a file
    if diff.deleted_file: return 'A' # adding new_file
    if diff.new_file: return 'D' # deleting a file
    return 'M' # modiyfing a file

def test_compare_commits(a,b):
    if a['timestamp'] != b['timestamp']:
        return False
    if a['commit'] != b['commit']:
        return False
    if a['size'] != b['size']:
        return False
    if a['type'] != b['type']:
        return False


    return True

if __name__ == "__main__":
    '''
        This script will parse a git repo (mirrored / --bare is fine as well).
        The input params are: 
        @input -p : path of the git repo 
        @input -o : default std, output file destination 
        @input -b : default master, branch name
        ======================================================
        The commits are order in an array where 
        -commits[0] = latest commit  (most recent) 
        -commits[len(commits)-1] = the first commit ever made (oldest)
        =======================================================
        Each object represens 1 file inside a commit. 
        for exmaple:
        if commit with sha '1234' had 2 file in the commit then 2 objects would appear 
        with the id/sha 1234  
        =======================================================
        Each object in the list is a JSON file with info containing:
        - author = email 
        - commit = sha 
        - deletions = number of deleted lines 
        - insertions = number of new inserted lines 
        - lines = total sum of lines changed deletions + insertions 
        - object = path to the specific file that was changfed 
        - size = the size in bytes of the changes, if its a deletion commit then negative size of the total deleted bytes 
        - timestamp => 2018-07-06T01:32:36+0300
        - type = A (new file) ,M (modified file) ,D (deleted file) ,R (renamed file) 
    '''
    # shell vars argument parsing

    try:
        parser = ArgumentParser()

        parser.add_argument("-p", "--path", dest="path_name",
                            help="repository path (can be mirrored)", metavar="PATH")

        parser.add_argument("-o", "--out", dest="output_path",
                            help="output path to save the result, default = std", metavar="PATH")

        parser.add_argument("-b", "--branch", dest="branch_name",
                            help="branch name to lookup, default = master", metavar="BRANCH_NAME")

        args = parser.parse_args()

        path = args.path_name
        output = args.output_path
        branch = args.branch_name

        # if -b was empty then default branch is master

        if branch == None:
            branch = 'master'

        # if output was empty then out to std

        if output == None:
            output = 'std'

        # the commits data we need

        stats = versions(path, branch)

        # handle output

        l = [s for s in stats]

        if output == 'std':
            pprint.pprint(l)
        else:
            with open(output, 'w') as outfile:
                json.dump(l, outfile, indent=4, sort_keys=True)
            print('loading repo from branch: {} at: {} and storing to: {} '.format(branch, path, output))

    except:
        sys.exit(1)