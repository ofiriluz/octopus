import os
import json
import pprint
from octopus.profiler.ap_profilers import AccessPointProfiler
from octopus.profiler.ap_profilers.github import GithubContributionScorer, GithubFrameworkAnalyzer

class GitHubProfiler(AccessPointProfiler):
    def __init__(self,user_workspace_path):
        self.__user_workspace_path = user_workspace_path
        self.__user_metadata = None
        self.__user_repos_metadata = []
        self.__user_profiler_results = {}
        self.__contribution_scorer = GithubContributionScorer()
        self.__framework_analyzer = GithubFrameworkAnalyzer()

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

    def do_profiling(self):
        # Clear old profiling results
        self.__init_profiler()

        # Read all the information 
        self.__read_user_workspace()

        # Perform simple contribution score, revolves around 0.0-1.0
        contribution_score = self.__contribution_scorer.get_contribution_score(self.__user_metadata, self.__user_repos_metadata)

        repos_fw_scores = []
        for repo in self.__user_repos_metadata:
            repo_frameworks_scores = self.__framework_analyzer.analyze_repo_frameworks(repo)
            repos_fw_scores.append(repo_frameworks_scores)

        # For now the profiling score is only the contribution, more to come
        return contribution_score

if __name__ == '__main__':
    ofir_meta_file = 'D:\\Octopus\\octopus\\profiler\\ap_profilers\\github\\ofir_iluz'
    git_profiler = GitHubProfiler(ofir_meta_file)
    git_profiler.do_profiling()
