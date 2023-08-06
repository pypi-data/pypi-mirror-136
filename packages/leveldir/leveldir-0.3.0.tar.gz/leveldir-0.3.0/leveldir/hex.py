# standard imports
import os
import logging

# external imports
from hexathon import valid as valid_hex

# local imports
from .base import LevelDir

logg = logging.getLogger(__name__)


def default_formatter(hx):
    return hx.upper()


class HexDir(LevelDir):

    def __init__(self, root_path, key_length, levels=2, prefix_length=0, formatter=default_formatter):
        super(HexDir, self).__init__(root_path, levels, key_length + prefix_length)
        #self.path = root_path
        self.key_length = key_length
        self.prefix_length = prefix_length
        self.__levels = levels + 2
        self.formatter = formatter


    def __check(self, key, content, prefix):
        l = len(key)
        if l != self.key_length:
            raise ValueError('expected key length {}, got {}'.format(self.key_length, l))
        l = len(prefix)
        if l != self.prefix_length:
            raise ValueError('expected prefix length {}, got {}'.format(self.prefix_length, l))
        if not isinstance(content, bytes):
            raise ValueError('content must be bytes, got {}'.format(type(content).__name__))
        if prefix != None and not isinstance(prefix, bytes):
            raise ValueError('prefix must be bytes, got {}'.format(type(content).__name__))


    def add(self, key, content, prefix=b''):
        self.__check(key, content, prefix)
        key_hex = key.hex()
        entry_path = self.to_filepath(key_hex)
        return self.__add(entry_path, key, content, key_hex, prefix=prefix)


    def __add(self, entry_path, key, content, display_key, prefix=b''):
        c = self.count()

        os.makedirs(os.path.dirname(entry_path), exist_ok=True)
        f = open(entry_path, 'wb')
        f.write(content)
        f.close()

        f = open(self.master_file, 'ab')
        if prefix != None:
            f.write(prefix)
        f.write(key)
        f.close()

        logg.debug('created new hexdir entry {} idx {} in {}'.format(display_key, c, entry_path)) 
    
        return (c, entry_path)


    def add_dir(self, file_key, key, content, prefix=b''):
        self.__check(key, content, prefix)
        key_hex = key.hex()
        entry_path = self.to_filepath(key_hex)
        entry_path = os.path.join(entry_path, file_key)
        return self.__add(entry_path, key, content, key_hex, prefix=prefix)


    def __cursor(self, idx):
        return idx * (self.prefix_length + self.key_length)


    def set_prefix(self, idx, prefix):
        l = len(prefix)
        if l != self.prefix_length:
            raise ValueError('expected prefix length {}, got {}'.format(self.prefix_length, l))
        if not isinstance(prefix, bytes):
            raise ValueError('prefix must be bytes, got {}'.format(type(content).__name__))
        cursor = self.__cursor(idx)
        f = open(self.master_file, 'rb+')
        f.seek(cursor)
        f.write(prefix)
        f.close()


    def get(self, idx):
        cursor = self.__cursor(idx)
        f = open(self.master_file, 'rb')
        f.seek(cursor)
        prefix = f.read(self.prefix_length)
        key = f.read(self.key_length)
        f.close()
        return (prefix, key)


    def to_subpath(self, hx):
        lead = ''
        for i in range(0, self.__levels, 2):
            lead += hx[i:i+2] + '/'
        return self.formatter(lead)


    def to_dirpath(self, hx):
        sub_path = self.to_subpath(hx)
        return os.path.join(self.path, sub_path)


    def to_filepath(self, hx):
        dir_path = self.to_dirpath(hx)
        file_path = os.path.join(dir_path, self.formatter(hx))
        return file_path
