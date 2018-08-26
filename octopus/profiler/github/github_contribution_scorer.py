import numpy
import datetime

class GithubContributionScorer:
    def __init__(self):
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
                'rolling': 0.4,
                'importance': 0.2,
                'commits': 0.4
            },
            'commit': 
            {
                'sizes': 0.4,
                'changes': 0.6
            }
        }

    def __get_master_branch(self, repo):
        return next((branch for branch in repo['branches'] if branch['name'] == 'master'))

    def __calculate_repo_administrative_contribution(self, repo, query):
        # Calculate administrative activity score
        # Look at the repo issues and pull requests to see activity of the user
        # Basic score:  (SUM([CommentsOnPost()]/[SumCommentOnPost()])/
        #               ([Count(Issues)] + [Count(PullReqs)])
        administrative_contribution_score = 0.0
        posts = repo['issues'] + repo['pullreqs']
        posts_len = len(posts)
        if posts_len == 0:
            return administrative_contribution_score

        for post in posts:
            comments_len = len(post['comments'])
            if comments_len == 0:
                continue
            user_comments_len = 0
            for comment in post['comments']:
                if comment['author'] == query['name']:
                    user_comments_len = user_comments_len + 1
            administrative_contribution_score += user_comments_len/comments_len

        # Normalize the sum between 0 and 1
        administrative_contribution_score = (1/posts_len)*(administrative_contribution_score-posts_len)+1

        return administrative_contribution_score

    def __calculate_rolling_branch_score(self, branch, query):
        # - Rolling codebase contribution:
        #    For each commit see the percentage changed per whole project
        #      Project it on all the commits to see the overall codebase contribution
        
        # For every commit, we need to check the size and code changes len before and after
        # The rolling score is an avg percentage of all the commits of the user based on the branch size and lines edited

        # [12%, 15%, 13%, ...]
        # 20 Changes
        # Max 400 files changeable
        # SUM() / MAX_FILES_CHANGEABLE()


        # "insertions": 3,
        # "size": 28,
        # "timestamp": "2018-08-20T16:48:39+0000",
        # "author": "ubuntu@ip-172-31-37-173.eu-west-3.compute.internal",
        # "object": "/home/wildermind/PycharmProjects/octopus/octopus/access_points/github_ap/scripts/all_junk/isan_ws/repositories/repositories/aws_instance_home_page/aws_instance_home_page/public/my_page.html",
        # "type": "M",
        # "deletions": 3,
        # "commit": "f3d728a0731d769277bcae27c494471391c5fe63",
        # "lines": 6

        rolling_scores = []
        for commit in branch['commits']:
            # Check if this the queried user commit
            if commit['author'] == query['name'] or commit['email'] == query['email']]: 
                changes = commit['file_changes']
                
                # The more changes across files, the better contribution
                changes_perc = 0.0
                for change in changes:
                    if change['lines'] != 0 and change['file_line_count'] != 0:
                        # Read file line amount after commit
                        lines = change['file_line_count']
                        change_amount = change['lines']
                        change_perc = change_amount / lines
                        changes_perc = changes_perc + change_perc
                commit_perc_score = changes_perc / commit['post_commit']['file_amount']
                rolling_scores.append(commit_perc_score)
        # Calculate the average deltas, this will give us the commitments to the branch overtime
        # Can be plotted later on
        drolling_scores = numpy.diff(rolling_scores)

        return numpy.average(drolling_scores)

    def __calculate_branch_importance(self, repo, branch, master_branch):
        # Look at the master branch to try and find merge with the given branch
        # This will give us indication on how long ago was the last real usage of this branch
        # Another factor is to look at the last commit date compared to last master commit date
        # This will give us an indication if the branch is important or in use 

        # First look at the branch last commit vs master last commit of the user
        # Sorted oldest to recent
        last_branch_cmmmit = branch['commits'][-1]
        last_master_commit = master_branch['commits'][-1]
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
        # merge_dates = []
        # for commit in master_branch['commits']:
        #     if commit['is_merge_commit']:
        #         # Found a merged commit from the branch, save the merge date
        #         merge_dates.append(datetime.datetime.strptime(commit['commit_time'], '%d.%m.%Y'))
        # # Calculate the date diffs, and average them, this will give us average diff on master merge
        # # Which means how active the branch was within the master branch
        # merge_diffs = numpy.diff(merge_dates)
        # merge_median = numpy.median(merge_diffs)
        # return merge_median * norm_date_diff
        return norm_date_diff

    def __calculate_commit_contribution(self, commit, branch, repo):
        # - For each commit produce:
        #   Commit Size in bytes compared to branch size
        #     If commit size reduces the branch size, this means removal
        #   Negative score is allowed for now
        #     Amount of Diffs on commit (May indicate debugging)
        #       Commit contribution score:
        #         (Commit Size / Branch Size)*Wc1 + (DiffsLen)*Wc2 
        commit_size = commit['post_commit']['branch_size'] - commit['pre_commit']['branch_size']
        branch_size = commit['post_commit']['branch_size']
        line_diffs = sum([file_change['line'] for file_change in commit['file_changes']])
        overall_lines = sum([file_change['file_line_count'] for file_change in commit['file_changes']])
        commit_contribution = (commit_size / branch_size) * self.__weights['commit']['sizes'] + (line_diffs / overall_lines) * self.__weights['commit']['changes']
        return commit_contribution

    def __calculate_branch_contribution(self, branch, repo, query):
        # Calculates rolling score overtime on the branch commits according to perc changes
        rolling_score = self.__calculate_rolling_branch_score(branch, query)

        # Calculates the factor of the branch to the master branch
        branch_importance_factor = self.__calculate_branch_importance(repo, branch, self.__get_master_branch(repo))

        commits_score = 0.0
        for commit in branch['commits']:
            if commit['author'] == query['name'] or commit['email'] == query['email']]:
                commits_score = commits_score + self.__calculate_commit_contribution(commit, branch, repo)
        
        # Normalize score between 0 and 1 according to commit amount
        # Can be normalized like this cuz max score is 1 for each commit
        commits_score = (1/len(branch['commits']))*(commits_score-len(branch['commits']))+1
        
        return rolling_score * self.__weights['branch']['rolling'] \
         + branch_importance_factor * self.__weights['branch']['importance'] + commits_score * self.__weights['branch']['commits']

    def __calculate_repo_contribution(self, repo, query):
        administrative_score = self.__calculate_repo_administrative_contribution(repo, query)
        # administrative_score = 0.0
        is_forked = repo['is_fork']
        branches_score = 0.0
        for branch in repo['branches']:
            branches_score = branches_score + self.__calculate_branch_contribution(branch, repo, query)

        # Normalize score between 0 and 1 according to len of repos
        # Since max is K repos its fine to normalize it by branch size
        branches_score = (1/len(repo['branches']))*(branches_score-len(repo['branches']))+1

        # Final repo score is the weighted score of each part
        # Everything is factored by if the repo is forked by 1-Wfork
        repo_score = (administrative_score*self.__weights['repo']['administirive'] + branches_score*self.__weights['repo']['branches']) * (1-min(self.__weights['repo']['fork'], is_forked))

        return repo_score

    def get_contribution_score(self, query, user_repos):
        # Go over every repo and calculate repo score
        contribution_scores = []
        for repo in user_repos:
            contribution_scores.append(self.__calculate_repo_contribution(repo, query))
        
        # Normalize it
        contribution_score = numpy.linalg.norm(contribution_scores)

        return contribution_score
