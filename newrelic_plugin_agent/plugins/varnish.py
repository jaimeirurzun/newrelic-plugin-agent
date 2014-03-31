"""
Varnish Support

"""
import logging
import re
import subprocess

from newrelic_plugin_agent.plugins import base

LOGGER = logging.getLogger(__name__)

PATTERN = re.compile("^(?P<stat>[\w_\(\)\.,]*)\s+(?P<psa>\d*)\s+"
                     "(?P<psan>[\d.]*)\s(?P<desc>[\w\., /]*)$", re.M)

class Varnish(base.Plugin):

    GUID = 'com.meetme.newrelic_varnish_agent'

    METRICS = {
        'client_conn': ('Totals/Client/Connections', 'gauge', ''),
        'client_drop': ('Totals/Client/Drops', 'gauge', ''),
        'client_req': ('Totals/Client/Requests', 'gauge', ''),
        'cache_hit': ('Totals/Cache/Hits', 'gauge', 'hits'),
        'cache_hitpass': ('Totals/Cache/Hitpasses', 'gauge', 'hits'),
        'cache_miss': ('Totals/Cache/Misses', 'gauge', 'hits'),
    }

    def poll(self):
        """This method is called after every sleep interval. If the intention
        is to use an IOLoop instead of sleep interval based daemon, override
        the run method.

        """
        LOGGER.info('Polling %s', self.__class__.__name__)
        self.initialize()

	try:
            data = subprocess.Popen([self.config.get('bin'), '-1'], stdout=subprocess.PIPE).communicate()[0]
        except Exception:
            LOGGER.error('%s could not connect, skipping poll interval',
                         self.__class__.__name__)
            return

        if data:
            self.add_datapoints(data)
            self.finish()
        else:
            self.error_message()

    def add_datapoints(self, data):
        matches = PATTERN.findall(data)
        if matches:
            for line in matches:
                key, value = line[:2]
                if key in self.METRICS.keys():
                    metric, nature, unit = self.METRICS[key]
                    method = 'add_{0}_value'.format(nature)
                    getattr(self, method)(metric, unit, int(value))
        else:
            LOGGER.debug('Stats output: %r', data)
