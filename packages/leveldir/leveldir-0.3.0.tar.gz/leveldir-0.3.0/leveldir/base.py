# standard imports
import os
import stat


class LevelDir:

    def __init__(self, root_path, levels, entry_length):
        self.path = root_path
        self.levels = levels 
        self.entry_length = entry_length
        fi = None
        self.__prepare_directory(self.path)

        self.__verify_directory()

        self.master_file = os.path.join(self.path, '.master')


    def have(self, k):
        fp = self.to_filepath(k)
        try:
            os.stat(fp)
        except FileNotFoundError:
            return False
        return True


    def __verify_directory(self):
        fi = os.stat(self.path)
        if not stat.S_ISDIR(fi.st_mode):
            raise ValueError('{} is not a directory'.format(self.path))
        #f = os.listdir(self.path)
        #os.listdir(self.path)
        #f.close()
        return True


    def count(self):
        fi = os.stat(self.master_file)
        c = fi.st_size / self.entry_length
        r = int(c)
        if r != c: # TODO: verify valid for check if evenly divided
            raise IndexError('master file not aligned')
        return r


    @classmethod
    def __prepare_directory(cls, path):
        os.makedirs(path, exist_ok=True)
        state_file = os.path.join(path, '.master')
        try:
            os.stat(state_file)
        except FileNotFoundError:
            f = open(state_file, 'w')
            f.close()
        return state_file
