# standard imports
import math
import os
import logging

# local imports
from .base import LevelDir

logg = logging.getLogger(__name__)


class NumDir(LevelDir):

    def __init__(self, root_path, thresholds=[1000]):
        thresholds = self.__thresholds_sanity(thresholds)
        super(NumDir, self).__init__(root_path, len(thresholds), 8)
        self.thresholds = thresholds
        fi = os.stat(self.master_file)
        self.entry_length = 8


    def __thresholds_sanity(self, thresholds):
        if len(thresholds) == 0:
            raise ValueError('thresholds must have at least one value')
        last_t = thresholds[0]
        for i in range(len(thresholds) - 1):
            if thresholds[i+1] > last_t:
                raise ValueError('thresholds must have diminishing order')
        return thresholds


    def to_dirpath(self, n): 
        c = n 
        x = 0
        d = []
        v = 0
        logg.debug('dirpath {}'.format(n))
        for t in self.thresholds:
            x = math.floor(c / t)
            y = x * t
            v += y
            d.append(str(v))
            c -= y
        return os.path.join(self.path, *d) 
      

    def to_filepath(self, n):
        path = self.to_dirpath(n)
        return os.path.join(path, str(n))


    def add(self, n, content, prefix=b''):
        entry_path = self.to_filepath(n)

        os.makedirs(os.path.dirname(entry_path), exist_ok=True)

        f = open(entry_path, 'wb')
        f.write(content)
        f.close()

        f = open(self.master_file, 'ab')
        f.write(n.to_bytes(8, byteorder='big'))
        f.close()

        c = self.count()

        logg.debug('created new numdir entry {} idx {} in {}'.format(str(n), c, entry_path)) 
