import os
import json
import pprint
from octopus.profiler import Profiler
from octopus.profiler.github import GithubContributionScorer, GithubFrameworkAnalyzer, GithubEventsAnalyzer
from octopus.data_access.accessors.filesystem.github_fs_accessor import GithubFSAccessor

class GithubProfiler(Profiler):
    def __init__(self):
        self.__user_workspace_path = None
        self.__user_metadata = None
        self.__user_repos_metadata = []
        self.__user_profiler_results = {}
        self.__contribution_scorer = GithubContributionScorer()
        self.__framework_analyzer = GithubFrameworkAnalyzer()
        self.__events_analyzer = GithubEventsAnanlyzer()
        self.__github_accessor = None

    def __init_profiler(self):
        self.__user_metadata = None
        self.__user_repos_metadata = []
        self.__user_profiler_results = {}

    def do_profiling(self, logger, query, controllers):
        # Set the workspace path from the given query
        self.__github_accessor = GithubFSAccessor(query['workspace_path'], logger)

        # Clear old profiling results
        logger.info("Initializing profiler")
        self.__init_profiler()

        # Read all the information 
        logger.info("Reading user metadata")
        self.__user_metadata = self.__github_accessor.read_user_metadata()

        logger.info("Reading user repo metadata")
        self.__user_repos_metadata = self.__github_accessor.read_user_repos_metadata()

        logger.info("Reading additional repo information")
        self.__github_accessor.acquire_additional_repos_info(self.__user_repos_metadata)

        # Perform simple contribution score, revolves around 0.0-1.0
        logger.info('Calculating user contribution score')
        contribution_score = self.__contribution_scorer.get_contribution_score(query, self.__user_repos_metadata)

        # Do the framework scoring
        logger.info('Calculating user framework scores for repos')
        repos_fw_scores = []
        for repo in self.__user_repos_metadata:
            repo_frameworks_scores = self.__framework_analyzer.analyze_repo_frameworks(repo)
            repos_fw_scores.append(repo_frameworks_scores)

        # For now the profiling score is only the contribution, more to come
        return {'contribution_score': contribution_score, 'framework_scores': repos_fw_scores}