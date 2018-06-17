Octopus
=======

Ongoing Tasks:
- ### Ofir ###
    - **task_manager** - Done development, tested
    - **infra.logger** - Done development, need to add tests
    - **database** - 
    Working under the following URLs - 
    https://www.compose.com/articles/using-graphql-with-mongodb/
    https://github.com/nmaro/graphql-mongodb-example
        - DB Structure:
            - Query
            - AccessPoint => InterfaceCollection[_id, query_id, access_point_name, access_point_path]
                - Twitter
                - Facebook
                - Reddit
                - Wiki
                - ...
            - Profiler
            - Example Query:
            ```json
            {
                "_id": "...",
                "query": "x x", // Query is basiclly the full name or the url to the picture and so on
                "query_hints": {}, // Extra hints dict that the user gives
                "query_ip": "", // IP of the user
                "search_time": "dt", // Datetime of the search
                "access_points": { // Dict of resulting access points, this can be added and changed, note that each AP can contain multiple results in the case of unknown
                    "twitter": ["_id"],
                    "facebook": ["_id"]
                },
                "profiler_results": ["_id", "_id",...] // Different profiler results foreign keys, may contain multiple profiler results from the access points
            } 
            ```
            - Profiler Example is still unknown
            - AccessPoint are dependent on the access point itself and the info it supplies

        - Each access point will have a graphql type and resolver
        - All of the type / resolvers will be added to the main dict which will be used by the Query resolver to reflect outside the access point

- ### Isan ###
    - **twitter access_point** - given an existing twitter user   name return all profile + tweets - DONE 
    **TODO** - free search (for when not knowing the exact twitter name
- ### Both ###
    - Merge isan's access points with the task manager and write a definition file for the access points
