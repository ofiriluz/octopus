Octopus
=======

Design
-------
<img src="docs/Octopus Design.png"
     alt="Markdown Monster icon" />

Ongoing Tasks
--------------
- ### Ofir ###
    - **task_manager** - Done development, tested [16.6.2018]
    - **infra.logger** - Done development, tested [16.6.2018]
    - **database** - 
    Working under the following URLs - 
    https://www.compose.com/articles/using-graphql-with-mongodb/
    https://github.com/nmaro/graphql-mongodb-example
        - DB Structure:
            - ProfileQuery
            - AccessPoint => InterfaceCollection[_id, query_id, access_point_name, access_point_path]
                - Twitter
                - Facebook
                - Reddit
                - Wiki
                - ...
            - Profile
            - 
            ```js
            Example ProfileQuery:
            {
                "_id": ...,
                "query": "x x", // Query is basiclly the full name or the url to the picture and so on
                "query_hints": {}, // Extra hints dict that the user gives
                "query_ip": "", // IP of the user
                "search_time": "dt", // Datetime of the search
                "access_points": { // Dict of resulting access points, this can be added and changed, note that each AP can contain multiple results in the case of unknown
                    "twitter": ["_id"],
                    "facebook": ["_id"],
                    ...
                },
                "profiler_results": ["_id", "_id",...] // Different profiler results foreign keys, may contain multiple profiler results from the access points
            } 
            ```
            - Profiler Example is still unknown
            - AccessPoint are dependent on the access point itself and the info it supplies

        - Each access point will have a graphql type and resolver
        - All of the type / resolvers will be added to the main dict which will be used by the Query resolver to reflect outside the access point

- ### Isan ###
    - **twitter access_point** - given an existing twitter user   name return all profile + tweets - DONE [21.6.18] 
    - **github access_point** - In progress
    The github access point should provide the following for the profiler:
        - argparse util with the ability to give the following params:
            - name to find in git
            - whether to clone the repos or only generate metadata
            - max repo size (so if a repo is big, it will ignore it)
            - meta info output path which has the following
                - meta.json - contains information on the user level
                    - list of repos
                    - user information
                    - any other special info that can be used
                - repos/_repo_name_/repo
                - repos/_repo_name_/meta.json - contains info about the specific repo
                    - clone path (or failure if too big or didnt work)
                    - git log / history (either seperate file or not)
                    - is_fork
                    - issues information
                    - pull requests information
                    - has_wiki
                    - branches information
                    - contributers information
                    - code types (guess github only gives the primary)
        - All of the information above will be outputted from the github api
        - The info will be used on the github_profiler later on to provide the following:
            - commit sizes
            - contribution score to repos
            - originality (forks or not and level of editing)
            - actual code contribution level
            - familiraity score of each repo
            - organization score for each repo
            - git conventions score for each repo
            - issues handling and pull request handling score for each repo
            - contribution to foreign repos score
            - celeberity score
        - All of the info will be saved to the DB
