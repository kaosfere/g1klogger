from SimConnect import *
import simdata.vars
import pprint


class Connection:
    def __init__(self, cache_time=1000):
        self.cache_time = cache_time
        self._conn = SimConnect()
        self._req = AircraftRequests(self._conn, _time=0)  # self.cache_time)
        self._variables = []
        self._create_vars()

    def _create_vars(self):
        for var in simdata.vars.vars:
            var.load(self._req)
            self._variables.append(var)
        # pprint.pprint(self._variables)

    @property
    def variables(self):
        return self._variables
