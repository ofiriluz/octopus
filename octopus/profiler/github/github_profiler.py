import os
import json
import pprint
from octopus.profiler import Profiler
from octopus.profiler.github import GithubContributionScorer, GithubFrameworkAnalyzer
from octopus.data_access.accessors.filesystem.github_fs_accessor import GithubFSAccessor

class GithubProfiler(Profiler):
    def __init__(self):
        self.__user_workspace_path = None
        self.__user_metadata = None
        self.__user_repos_metadata = []
        self.__user_profiler_results = {}
        self.__contribution_scorer = GithubContributionScorer()
        self.__framework_analyzer = GithubFrameworkAnalyzer()
        self.__github_accessor = None

    def __init_profiler(self):
        self.__user_metadata = None
        self.__user_repos_metadata = []
        self.__user_profiler_results = {}

    def do_profiling(self, logger, query, controllers):
        # Set the workspace path from the given query
        if not 'workspace_path' in query.keys():
            return {}
        self.__github_accessor = GithubFSAccessor(query['workspace_path'])
        # Clear old profiling results
        self.__init_profiler()

        # Read all the information 
        self.__user_metadata = self.__github_accessor.read_user_metadata()
        self.__user_repos_metadata = self.__github_accessor.read_user_repos_metadata()

        # Do the frame scoring
        # repos_fw_scores = []
        for repo in self.__user_repos_metadata:
            # Read the repo branch commits and add them 
            repo['branches'] = self.__github_accessor.read_repo_commits(repo['repo_local_path'])
            # repo_frameworks_scores = self.__framework_analyzer.analyze_repo_frameworks(repo)
            # repos_fw_scores.append(repo_frameworks_scores)

        # Perform simple contribution score, revolves around 0.0-1.0
        contribution_score = self.__contribution_scorer.get_contribution_score(self.__user_metadata, self.__user_repos_metadata)

        # For now the profiling score is only the contribution, more to come
        return {'contribution_score': contribution_score, 'framework_scores': repos_fw_scores}

if __name__ == '__main__':
    ofir_meta_file = 'D:\\Octopus\\octopus\\profiler\\ap_profilers\\github\\ofir_iluz'
    git_profiler = GithubProfiler(ofir_meta_file)
    scores_result = git_profiler.do_profiling()
    pprint.pprint(scores_result)
