#!/usr/bin/env python
import logging
import json
from urlparse import parse_qs

def augment_bracket(string):
    if not string.endswith('}'):
        string = string + '}'
    if not string.startswith('{'):
        string = '{' + string
    return string

def split_data(data):
    """
    split a long string which contains several commands to split a list commond, for example:

    >>> docs = '{"host": "thales.bu.edu", "password": "", "user": "anonymous", "event": "set_ftp_info"}{"directory": ".", "pattern": "assword", "suffix": [".txt"], "event": "set_file_filter"}{"event": "search_and_upload"}'
    >>> print split_data(docs)
    ['{"host": "thales.bu.edu", "password": "", "user": "anonymous", "event": "set_ftp_info"}', '{"directory": ".", "pattern": "assword", "suffix": [".txt"], "event": "set_file_filter"}', '{"event": "search_and_upload"}']
    """
    split = data.rsplit('}{')
    if len(split) == 1: return split
    return [augment_bracket(s) for s in split]

class UnknownEventException(Exception):
    pass

class CMD(object):
    """Command Meta Description.
    Define a set of commands that can be run.
    """
    def __init__(self, desc=None):
        self.desc = desc
        self._set_logger()

    def _set_logger(self):
        logging.basicConfig()
        self.logger = logging.getLogger(self.name)
        # self.logger.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.WARNING)

    def _trigger(self, event_name, *argv, **kwargv):
        """trigger an event, event hander is a class member function"""
        self.logger.debug('%s has been triggered'%(event_name))
        getattr(self, event_name)(*argv, **kwargv)

    def dispatcher(self, sock, data):
        """data may contain one or more command
        Args:

            - **sock**: the socket that receive the data.
            - **data**: data is a sequence of json encode string. "event" key
                is required and is the name of the command that will be run
                a example is: {"password": ["1234"], "event": ["verify_master"]}
        Returns:
            None
        Raises:
            UnknownEventException
        """
        self.logger.debug('dispatcher recv data' + data)
        if not data:
            return
        s_data = split_data(data)
        if len(s_data) > 1:
            self.logger.debug('there are %i commands in this data'%(len(s_data)))
            for one_data in s_data:
                self.dispatcher(sock, one_data)
            return
        else:
            data = s_data[0]

        try:
            dt_data = self._load_json(data)
        except:
            print('load error')
            import pdb;pdb.set_trace()
        if isinstance(dt_data['event'], list):
            event_name = dt_data['event'][0]
        elif isinstance(dt_data['event'], str) or isinstance(dt_data['event'], unicode):
            event_name = dt_data['event']
        else:
            print type(dt_data['event'])
            raise UnknownEventException('Unknown event type')
        del dt_data['event']
        self.logger.debug('event_name will be trigged: ' + event_name)
        self._trigger(event_name, sock, dt_data)

    def _cmd_to_json(self, cmd_str): return json.dumps(parse_qs(cmd_str))
    def _dump_json(self, data): return json.dumps(data)
    def _load_json(self, js): return json.loads(js)

    def install(self, node):
        """ install the command set to node. """
        if self._is_okay(node):
            pass
        self.node = node
        node.cmd_set = self

    def start(self):
        """start the command set, execuate the *start_action* specifed in **desc**
        """
        self._trigger(self.desc['start_action'])

    def get_state(self): return self.node.state
    def set_state(self, val): self.node.set_state(val)
    state = property(get_state, set_state)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

