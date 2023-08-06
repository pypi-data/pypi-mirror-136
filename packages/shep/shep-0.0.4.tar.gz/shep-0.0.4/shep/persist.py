# local imports
from .state import State


class PersistedState(State):

    def __init__(self, factory):
        self.__store_factory = factory
        self.__stores = {}


    def __store_add(self, k, v):
        if self.
