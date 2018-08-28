import numpy
import dateutil.parser

class GithubEventsAnalyzer:
    def __init__(self):
        self.__activity_min_max = [0, 129600*60] # 90 Days in minutes
        self.__activity_bins = 5

    def __analyze_activity(self, user_events):
        # Analyze activity date based
        # Add the time diffs between each event 
        # Activity is considered to be the more condensed the vector is distance wise
        # Which means that over a min max function, the histogram bins will be more dense

        # Sort the events date wise
        sorted_events = sorted(user_events, key=lambda e: e['timestamp'])

        # Calculate the events date diffs
        event_diffs = numpy.diff([dateutil.parser.parse(x['timestamp']) for x in sorted_events])

        # Calculate the histogram bins 
        histo = numpy.histogram(event_diffs, bins=self.__activity_bins, range=self.__activity_min_max)


    def analyze_user_events(self, user_meta):
        