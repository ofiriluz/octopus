
import os, sys
import shutil
from distutils.dir_util import copy_tree
class Exporter(object):


    '''
    target = {
        src= '../../'
        target= './../..'
    }
    '''
    def __init__(self,target):
        self.target = target
        dir = self.__get__target__name__()
        self.target['target_dir'] = os.path.join(self.target['target'], dir)

    # fetch the meta output from a given target
    def export_meta(self):

        # generate target folder from source to target target_path/target_name
        print('[+] creating destination folder {}'.format(self.target_dir()))
        os.makedirs(self.target_dir())

        # save target/input_meta.json

        dest = os.path.join(self.target_dir())
        src = os.path.join(self.src_dir())
        print('[+] creating input_meta.json')
        self.__copy__file(src,dest,FILE_NAME='input_meta.json')

        # save target/profile_meta.json

        dest = os.path.join(self.target_dir())
        src = os.path.join(self.src_dir())
        print('[+] creating profile_meta.json')
        self.__copy__file(src, dest, FILE_NAME='profile_meta.json')

        # save top level target/repositories folder
        print('[+] creating {}'.format(self.target_repos_dir()))
        os.makedirs(self.target_repos_dir())

        # save target/repositories_meta.json
        dest = os.path.join(self.target_repos_dir())
        src = os.path.join(self.src_repos_dir())
        self.__copy__file(src, dest, FILE_NAME='repositories_meta.json')

        # copy all the repositories outputs /target/repositories/some_repo/commits/*
        repos_dirs = self.get_all_repos_dirs()
        for r in repos_dirs:
            self.copy_repo_meta(r)

        #save /target/repositories/some_repo/some_repo_meta.json

        return True

    def src_dir(self):
        return self.target['src']

    def target_dir(self):
        return self.target['target_dir']

    # target/repositories
    def target_repos_dir(self):
        return os.path.join(self.target_dir(), 'repositories')

    # src/repositories
    def src_repos_dir(self):
        return os.path.join(self.src_dir(), 'repositories')

    # get list of full paths to repositories dirs src/repositories/repo1..repo2..
    def get_all_repos_dirs(self):

        src = os.path.join(self.src_repos_dir(),'repositories')
        target = os.path.join(self.target_repos_dir(), 'repositories')

        repos_names = [name for name in os.listdir(src)
                        if os.path.isdir(os.path.join(src, name))]

        result = [{'src':os.path.join(src,name),'target':os.path.join(target,name),'name':name} for name in repos_names]
        return result


    def copy_repo_meta(self,repos_dirs):

        # make dir
        os.makedirs(repos_dirs['target'])
        # copy r/r._meta.json file
        src = os.path.join(repos_dirs['src'])
        dest = os.path.join(repos_dirs['target'])
        self.__copy__file(src, dest, FILE_NAME=repos_dirs['name']+'_meta.json')
        # copy r/commits folder
        dest = os.path.join(dest,'commits')
        os.makedirs(dest)
        self.__copy__dir__(os.path.join(src,'commits'),dest)
        #TODO :: FINISH THE PROCESS OF COPYNG ALL THE COMMITS CONTENT - SOME WEIRD BUG BUT THE CODE ABOVE SDHOULD WORK
        return True

    def __get__target__name__(self):

        name =''
        if self.src_dir()[-1:] == '/':
            name = os.path.basename(self.src_dir()[:-1])
        else:
            name = os.path.basename(self.src_dir())
        return name

    def __copy__dir__(self,src_dir,target_dir):
        return copy_tree(src_dir, target_dir)

    def __touch__(self,filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write("")

    def __copy__file(self,src,target,FILE_NAME=None):

        if FILE_NAME != None:
            src = os.path.join(src,FILE_NAME)
            target = os.path.join(target,FILE_NAME)

        shutil.copyfile(src, target, follow_symlinks=True)


if __name__ == '__main__':

    target = {
        'src':'/home/wildermind/PycharmProjects/octopus/octopus/access_points/github_ap/scripts/all_junk/enigma_shit_ws',
        'target':'/home/wildermind/PycharmProjects/octopus/octopus/access_points/github_ap/scripts/all_junk/enigma_exporter_out'
    }
    exporter = Exporter(target)
    exporter.export_meta()
