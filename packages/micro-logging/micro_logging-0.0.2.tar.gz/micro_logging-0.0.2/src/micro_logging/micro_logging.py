import logging
import json

class Log():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    # ability to print out the fields
    def show(self):
        print(self.__dict__)
    # ability to add any custom fields
    def add(self,**kwargs):
        self.__dict__.update(kwargs)
    # ability to remove any fields
    def remove(self,field):
        del self.__dict__[field]
    # reset the logs after runtime
    def reset(self):
        self.__dict__ = {}

