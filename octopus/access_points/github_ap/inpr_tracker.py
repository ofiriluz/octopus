''' INPR = Issues N Pull Requests Tracker

*{The issues url is working for both issues and pr id
the pr's url is working only for pr id}

**{ issues url
https://api.github.com/repos/{profile_name}/{repo_name}/issues/{#id}
    pulls_url
https://api.github.com/repos/{profile_name}/{repo_name}/pulls/{#id}}

***{
There are X search types:
- R id_range, S - id_start, E - id_explicit, G- Genesis to end (1 to inf }

    options = {
        pull_url : '' // if None then get both issues and pulls due to *
        issues_url : '' // if None then repo_name and profile_name must be present to handle default URL
        repo_name :  '' // if None issues_url must not be none
        profile_name : '' //if None issues_url must not be none
        with_events : bool // if True fetch events as well
        with_comments : bool // if True fetch comments
        id_range : (start,num) //Optional, start =9 , num = 10 will go in range of ids (9,19)
        id_start : min // Optional which id to start, if no id_range -> will go until the end of inprs
        id_explicit : [] // Optional, fetch specific inprs [2,4,14,22]
    }
'''

import requests
import json
class Inpr(object):
    def __init__(self,is_issue,raw_inpr):
        self.is_issue = is_issue
        self.raw_inpr = raw_inpr
    def is_issue(self):
        return self.is_issue

class InprTracker(object):
    def __init__(self,options):
        self.g = None
        self.callback = None
        self.options = options
        self.god = {}
        self.god['is_inpr'] = False
        self.god['source_url'] = None
        self.god['with_comments'] = False
        self.god['with_events'] = False
        self.god['search_type'] = ''
        self.god['search_range'] = ()
        self.build(options)


    def build(self,options):
        # inprs or pulls ?
        build_url = False
        url_source = 'pull_url'

        # check if should build url or not, if True then will fetch inprs
        if options['pull_url'] and options['issues_url'] is None:
            build_url = True

        # create god.source_url

        if build_url:
            self.god.source_url = self.__url(options['profile_name'], options['repo_name'])
            self.god.is_inpr = True
        else:
            if options['pull_url'] is None:
                self.god['is_inpr'] = True
                url_source = 'issues_url'
            self.god['source_url'] = options[url_source]
        # comments & events
        self.god['with_comments'] = options['with_comments']
        self.god['with_events'] = options['with_events']
         # search type and range
        type , range = self.__type_n_range(options)
        self.god['search_type'] = type
        self.god['search_range'] = range
        return self

    def run_inpr(self,callback = None):
        nprs = []
        if self.god['search_type'] == 'G'or self.god['search_type'] == 'S':
            # handle while ok search
            ok = True
            id_counter = self.
            while ok:
                inprObj = self.__fetch_inpr(id_counter)
                if inprObj == None:
                    ok = False
                    break
                nprs.append(inprObj)


        pass

    def __url(self,profile_name,repo_name, inpr = True):
        #https://api.github.com/repos/{profile_name}/{repo_name}/issues/{#id}
        if inpr:
            return 'https://api.github.com/repos/' + profile_name + '/' + repo_name + '/issues'
        else:
            return 'https://api.github.com/repos/' + profile_name + '/' + repo_name + '/pulls'

    # - R id_range, S - id_start, E - id_explicit}, G - genesis to end
    def __type_n_range(self,options):
        search_type = ''
        range = 0
        if options['id_range'] is not None:
            search_type = 'R'
            range = (int(options['id_range'][0]), int(options['id_range'][0]) + int(options['id_range'][1]))
        elif options['id_start'] is not None:
            search_type = 'S'
            # seach from start to end
            range = (options['id_start'],0)
        elif options['id_explicit'] is not None:
            search_type = 'E'
            range = tuple(options['id_explicit'])
        else:
            search_type = 'G'
            range (1,0)

        return search_type, range


    def __GET__JSON(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print('err {} u {}'.format(response.status_code,url))
            return None

    def __fetch_inpr(self, id):
        url = self.god['source_url'] + id
        inpr = self.__GET__JSON(url)
        is_issue = False
        if inpr is None:
            return None
        # pr or issue
        if inpr['pull_request'] is not None:
            is_issue = True

        # build initial inpr
        inprObj = Inpr(is_issue,inpr)

        return inprObj

'''options = {
        pull_url : '' // if None then get both issues and pulls due to *
        issues_url : '' // if None then repo_name and profile_name must be present to handle default URL
        repo_name :  '' // if None issues_url must not be none
        profile_name : '' //if None issues_url must not be none
        with_events : bool // if True fetch events as well
        with_comments : bool // if True fetch comments
        id_range : (start,num) //Optional, start =9 , num = 10 will go in range of ids (9,19)
        id_start : min // Optional which id to start, if no id_range -> will go until the end of inprs
        id_explicit : [] // Optional, fetch specific inprs [2,4,14,22]
    }'''
if __name__ == '__main__':
    options = {
        'pull_url' : None ,
        'issues_url' : 'https://api.github.com/repos/enigmampc/enigma-core/issues/',
        'repo_name' :  '',
        'profile_name' : '',
        'with_events' : False,
        'with_comments' : False,
        'id_range' : (2,10),
        'id_start' : None,
        'id_explicit' : None
    }
    tracker = InprTracker(options)
    tracker.run_inpr()
