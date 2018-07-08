import os
import json
import numpy
import datetime
import pprint
from octopus.profiler.ap_profilers.access_point_profiler import AccessPointProfiler

class GitHubProfiler(AccessPointProfiler):
    def __init__(self,user_workspace_path):
        self.__user_workspace_path = user_workspace_path
        self.__user_metadata = None
        self.__user_repos_metadata = []
        self.__user_profiler_results = {}
        self.__weights = \
        { 
            'repo': 
            {
                'administirive': 0.2,
                'branches': 0.6,
                'fork': 0.2
            },
            'branch':
            {
                'rolling': 0.3,
                'importance': 0.3,
                'commits': 0.4
            },
            'commit': 
            {
                'sizes': 0.4,
                'changes': 0.6
            }
        }

    def __read_user_workspace(self):
        # Assert user workspace path
        if os.path.exists(os.path.join(self.__user_workspace_path, 'meta.json')):
            # Read the user metadata
            with open(os.path.join(self.__user_workspace_path, 'meta.json')) as metafile:
                self.__user_metadata = json.load(metafile)

            # Read all the repos metadata
            repos_path = os.path.join(self.__user_workspace_path, 'repos')
            repos_dirs = [os.path.join(repos_path, subdir) for subdir in os.listdir(repos_path)
                                                           if os.path.isdir(os.path.join(repos_path, subdir))] 

            # Iterate over all the repos
            for repo_dir in repos_dirs:
                # Read the metadata of the repo
                repo_meta_path = os.path.join(repo_dir, 'meta.json')
                if os.path.exists(repo_meta_path):
                    with open(repo_meta_path) as repo_metafile:
                        self.__user_repos_metadata.append(json.load(repo_metafile))

    def __init_profiler(self):
        self.__user_metadata = None
        self.__user_repos_metadata = []
        self.__user_profiler_results = {}

    def __calculate_repo_administrative_contribution(self, repo):
        # Calculate administrative activity score
        # Look at the repo issues and pull requests to see activity of the user
        # Basic score:  (SUM([CommentsOnPost()]/[SumCommentOnPost()])/
        #               ([Count(Issues)] + [Count(PullReqs)])
        administrative_contribution_score = 0.0
        posts_len = len(repo['issues']) + len(repo['pullreqs'])
        if posts_len == 0:
            return administrative_contribution_score

        for issue in zip(repo['issues'], repo['pullreqs']):
            comments_len = len(issue['comments'])
            user_comments_len = 0
            for comment in issue['comments']:
                if comment['author'] == self.__user_metadata['user']:
                    user_comments_len = user_comments_len + 1
            administrative_contribution_score = administrative_contribution_score + user_comments_len/comments_len

        # Normalize the sum between 0 and 1
        administrative_contribution_score = (1/posts_len)*(administrative_contribution_score-posts_len)+1

        return administrative_contribution_score

    def __calculate_rolling_branch_score(self, branch):
        #       Rolling codebase contribution:
        #           For each commit see the percentage changed per whole project
        #           Project it on all the commits to see the overall codebase contribution
        
        # For every commit, we need to check the size and code changes len before and after
        # The rolling score is an avg percentage of all the commits of the user based on the branch size and lines edited

        # [12%, 15%, 13%, ...]
        # 20 Changes
        # Max 400 files changeable
        # SUM() / MAX_FILES_CHANGEABLE()

        rolling_scores = []
        for commit in branch['commits']:
            # pprint.pprint(commit)
            changes = commit['file_changes']
            
            # The more changes across files, the better contribution
            changes_perc = 0.0
            for change in changes:
                # Read file line amount after commit
                lines = change['file_line_count']
                change_amount = change['file_changed_lines_count']
                actual_changes_len = lines - change_amount
                change_perc = actual_changes_len / lines
                changes_perc = changes_perc + change_perc
            commit_perc_score = changes_perc / commit['post_commit']['file_amount']
            rolling_scores.append(commit_perc_score)
        # Calculate the average deltas, this will give us the commitments to the branch overtime
        # Can be plotted later on
        drolling_scores = numpy.diff(rolling_scores)

        return numpy.average(drolling_scores)

    def __get_master_branch(self, repo):
        return next((branch for branch in repo['branches'] if branch['name'] == 'master'))

    def __calculate_branch_importance(self, repo, branch, master_branch):
        #       Branch importance to master
        #           Find merge commits
        #           Check stale branch commit date wise
        
        # Look at the master branch to try and find merge with the given branch
        # This will give us indication on how long ago was the last real usage of this branch
        # Another factor is to look at the last commit date compared to last master commit date
        # This will give us an indication if the branch is important or in use 

        # First look at the branch last commit vs master last commit of the user
        # Sorted recent to oldest
        last_branch_cmmmit = branch['commits'][0]
        last_master_commit = master_branch['commits'][0]
        last_branch_commit_time = datetime.datetime.strptime(last_branch_cmmmit['commit_time'], '%d.%m.%Y')
        last_master_commit_time = datetime.datetime.strptime(last_master_commit['commit_time'], '%d.%m.%Y')
        repo_creation_time = datetime.datetime.strptime(repo['creation_time'], '%d.%m.%Y')

        date_diff = (last_branch_commit_time - last_master_commit_time).seconds
        # Give a min max in date and convert it
        min_date_diff = 0
        max_date_diff = (datetime.datetime.now() - repo_creation_time).seconds

        # Convert to actual factor representation
        norm_date_diff = date_diff / (max_date_diff - min_date_diff)

        # Try and find commits which are merge related on the given branch
        # This will give us an indication of branch activity over the period
        # The activity will be dropped down depending on the date diff, to lower the importance of this branch
        merge_dates = []
        for commit in master_branch['commits']:
            if commit['is_merge_commit']:
                # Found a merged commit from the branch, save the merge date
                merge_dates.append(datetime.datetime.strptime(commit['commit_time'], '%d.%m.%Y'))
        # Calculate the date diffs, and average them, this will give us average diff on master merge
        # Which means how active the branch was within the master branch
        merge_diffs = numpy.diff(merge_dates)
        merge_median = numpy.median(merge_diffs)
        return merge_median * norm_date_diff

    def __calculate_commit_contribution(self, commit, branch, repo):
        #       - For each commit produce:
        #           Commit Size in bytes compared to branch size
        #               If commit size reduces the branch size, this means removal
        #               Negative score is allowed for now
        #           Amount of Diffs on commit (May indicate debugging)
        #           Commit contribution score:
        #               (Commit Size / Branch Size)*Wc1 + (DiffsLen)*Wc2 
        commit_size = commit['post_commit']['branch_size'] - commit['pre_commit']['branch_size']
        branch_size = commit['post_commit']['branch_size']
        line_diffs = sum([file_change['file_changed_lines_count'] for file_change in commit['file_changes']])
        overall_lines = sum([file_change['file_line_count'] for file_change in commit['file_changes']])
        commit_contribution = (commit_size / branch_size) * self.__weights['commit']['sizes'] + (line_diffs / overall_lines) * self.__weights['commit']['changes']
        return commit_contribution

    def __calculate_branch_contribution(self, branch, repo):
        rolling_score = self.__calculate_rolling_branch_score(branch)
        branch_importance_factor = self.__calculate_branch_importance(repo, branch, self.__get_master_branch(repo))
        commits_score = 0.0
        for commit in branch['commits']:
            commits_score = commits_score + self.__calculate_commit_contribution(commit, branch, repo)
        
        # Normalize score between 0 and 1
        commits_score = (1/len(branch['commits'])-0)*(commits_score-len(branch['commits']))+1
        
        return rolling_score * self.__weights['branch']['rolling'] + branch_importance_factor * self.__weights['branch']['importance'] + commits_score * self.__weights['branch']['commits']

    def __calculate_repo_contribution(self, repo):
        administrative_score = self.__calculate_repo_administrative_contribution(repo)
        is_forked = repo['is_forked']
        branches_score = 0.0
        for branch in repo['branches']:
            branches_score = branches_score + self.__calculate_branch_contribution(branch, repo)

        # Normalize score between 0 and 1
        branches_score = (1/len(repo['branches'])-0)*(branches_score-len(repo['branches']))+1

        # Final repo score
        repo_score = (administrative_score*self.__weights['repo']['administirive'] + branches_score*self.__weights['repo']['branches']) * (max(self.__weights['repo']['fork'], 1-is_forked))

        return repo_score

    def __calculate_contribution_score(self):
        # Contribution score of a user consists of the following weighted params:
        # - For each repo produce:
        #   - For each branch produce:
        #       - For each commit produce:
        #           Commit Size in bytes compared to branch size
        #           Amount of Diffs on commit (May indicate debugging)
        #           New code files
        #           Commit contribution score:
        #               (Commit Size / Branch Size)*Wc1 + (DiffsLen)*Wc2 + (NewCodeFiles)*Wc3
        #       Commit Score => Normalized sum of commit scores
        #       Commits Amount for the checked user and overall commits
        #       Rolling codebase contribution:
        #           For each commit see the percentage changed per whole project
        #           Project it on all the commits to see the overall codebase contribution
        #       Branch importance to master
        #           Find merge commits
        #           Check stale branch commit date wise
        #       Branch contribution score:
        #           (Rolling Codebase Contribution)*Wb1 + (Commit Score)*Wb2 + (Branch Importance Score)*Wb3
        #   Branch Score => Normalized sum of branch scores
        #   Repo User administirive activity (Issues, Pull Reqs, Wiki)
        #   Repo fork demoralization factor
        #   Repo Score:
        #       (Branch Score * Wr1 + Repo administrative * Wr2)*(Wr3*IsForked())
        # Contribution score => Normalized sum of all repo scores
        
        # Go over every repo and calculate repo score
        contribution_scores = []
        for repo in self.__user_repos_metadata:
            contribution_scores.append(self.__calculate_repo_contribution(repo))
        
        contribution_score = numpy.linalg.norm(contribution_scores)
        print(contribution_score)

    def __calculate_user_scores(self):
        # Calculate contribution score to own repos
        self.__calculate_contribution_score()

    def do_profiling(self):
        # Clear old profiling results
        self.__init_profiler()

        # Read all the information 
        self.__read_user_workspace()

        # pprint.pprint(self.__user_metadata)
        # pprint.pprint(self.__user_repos_metadata)

        # Perform simple starting scoring before moving into the repos themselves
        self.__calculate_user_scores()

if __name__ == '__main__':
    ofir_meta_file = 'D:\\Octopus\\octopus\\profiler\\ap_profilers\\github\\ofir_iluz'
    git_profiler = GitHubProfiler(ofir_meta_file)
    git_profiler.do_profiling()
