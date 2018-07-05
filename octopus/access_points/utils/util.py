class Util(object):

    # turn to  pretty dictionary object and print
    @staticmethod
    def pretty_print_dict(d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                Util.pretty_dict(value, indent + 1)
            else:
                print('\t' * (indent + 1) + str(value))
