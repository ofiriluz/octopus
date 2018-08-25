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
import os
from octopus.access_points.auth_keys import GITHUB_PERSONAL_ACCOESS_TOKEN

class Inpr(object):
    def __init__(self,is_issue,raw_inpr):
        self._is_issue = is_issue
        self.raw_inpr = raw_inpr
        self.raw_comments = None
        self.raw_events = None
    def is_issue(self):
        return self._is_issue

    def is_pull_request(self):
        return not self.is_issue()
    def get_inpr_type(self):
        if self.is_issue():
            return 'issue'
        else:
            return 'pr'
    def export(self):
        exported = {}
        exported['type'] = self.get_inpr_type()
        exported['title'] = self.raw_inpr['title']
        exported['body'] = self.raw_inpr['body']
        exported['author'] = self.raw_inpr['user']['login']
        exported['comments_num'] = self.raw_inpr['comments']
        exported['created_at'] = self.raw_inpr['created_at']
        exported['created_at'] = None
        exported['state'] = self.raw_inpr['state']
        if exported['state'] == 'closed':
            exported['closed_by'] = self.raw_inpr['closed_by']['login']
        # handle comments {name,time}
        comments = []
        for c in self.raw_comments:
             comments.append({'author':c['user']['login'],
                              'created_at':c['created_at'],
                              'body' : c['body']})
        exported['comments'] = comments
        # TODO:: currently no handle events - ignored.
        return exported

    def get_comments_url(self):
        return self.raw_inpr['comments_url']

    def get_events_url(self):
        return self.raw_inpr['events_url']

    def set_raw_comments(self,comments):
        self.raw_comments = comments

    def set_raw_events(self,events):
        self.raw_events = events

class InprTracker(object):
    def __init__(self,options, API_ACCESS_TOKEN):
        self.API_ACCESS_TOKEN = API_ACCESS_TOKEN
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
    def run_inpr_and_export(self,callback = None):
        inprs = self.run_inpr(callback)
        exported = {}
        exported['pr'] = []
        exported['issue'] = []
        for o in inprs:
            e = o.export()
            if e['type'] == 'issue':
                exported['issue'].append(e)
            else:
                exported['pr'].append(e)
        return exported

    def run_inpr(self,callback = None):
        #get Inprs before parsing just wrapper object with raw inprs
        inprs = self.__get_raw_inprs()
        with_comments = self.god['with_comments']
        with_events = self.god['with_events']

        for inpr in inprs:
            if with_comments:
                curl = inpr.get_comments_url()
                # get comments
                com = self.__GET__JSON(curl)
                inpr.set_raw_comments(com)
            if with_events:
                eurl = inpr.get_events_url()
                # get events
                ev = self.__GET__JSON(eurl)
                inpr.set_raw_events(ev)
        return inprs

    def __get_raw_inprs(self,callback = None):
        nprs = []
        search_type = self.god['search_type']
        if search_type == 'G' or search_type == 'S': #G= (1,0) or S = (x,0)
            # handle while ok search
            ok = True
            id_counter = self.god['search_range'][0]
            while ok:
                inprObj = self.__fetch_inpr(id_counter)
                if inprObj == None:
                    ok = False
                    break
                nprs.append(inprObj)
                id_counter += 1

        elif search_type == 'R':
            for id in range(self.god['search_range'][0],self.god['search_range'][1]):
                inprObj = self.__fetch_inpr(id)
                if inprObj != None:
                    nprs.append(inprObj)

        elif search_type == 'E':
            for id in list(self.god['search_range']):
                inprObj = self.__fetch_inpr(id)
                if inprObj != None:
                    nprs.append(inprObj)
        else:
            raise Exception

        return nprs

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

    # authenthication : https://stackoverflow.com/questions/17622439/how-to-use-github-api-token-in-python-for-requesting
    def __GET__JSON(self, url):
        headers = {'Authorization': 'token ' + GITHUB_PERSONAL_ACCOESS_TOKEN}
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print('err {} u {}'.format(response.status_code,url))
            return None
    def dump_result(self,target_file,result):

        if not os.path.exists(os.path.dirname(target_file)):
            os.makedirs(os.path.dirname(target_file))

        with open(target_file, 'w') as outfile:
            json.dump(result, outfile, indent=4)

    def __fetch_inpr(self, id):
        url = self.god['source_url'] + str(id)
        inpr = self.__GET__JSON(url)
        is_issue = False
        if inpr is None:
            return None
        if 'pull_request' not in inpr:
            is_issue = True

        # build initial inpr
        inprObj = Inpr(is_issue,inpr)
        return inprObj

def test_full_flow():
    options = {
        'pull_url' : None ,
        'issues_url' : 'https://api.github.com/repos/enigmampc/enigma-core/issues/',
        'repo_name' :  '',
        'profile_name' : '',
        'with_events' : False,
        'with_comments' : True,
        'id_range' : (2,3),
        'id_start' : None,
        'id_explicit' : None
    }
    tracker = InprTracker(options,GITHUB_PERSONAL_ACCOESS_TOKEN)
    nprs = tracker.run_inpr_and_export()
    for i in nprs['issue']:
        print(i)
    print('----- {}'.format(len(nprs)))
    for pr in nprs['pr']:
        print(pr)
    path = '/home/wildermind/PycharmProjects/octopus/archive/isan_exporter_out/isan_ws/repositories/repositories/enigma-core/inprs.json'

    tracker.dump_result(path,nprs)

if __name__ == '__main__':
    test_full_flow()
