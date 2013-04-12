#!/usr/bin/env python
"""
This file defines the ServerCMD [ Server Command Meta Description ]
"""
from CMD import CMD
import copy

## Default Parameter Settings
server_desc = {
        'initial' : 'waiting',
        'start_action' : 'initialize',
        'srv_addr':'127.0.0.1',
        'srv_port':3333,
        'request_timeout':10,
        }

BOT_MASTER_PASSWORD = '1234'

class ServerCMD(CMD):
    name =  'server_cmd'
    def __init__(self, desc=server_desc):
        CMD.__init__(self, desc)

    def _is_okay(self, node): return True

    def start(self):
        self.initialize()

    @property
    def addr(self): return self.desc['srv_addr']

    @property
    def port(self): return self.desc['srv_port']

    def initialize(self):
        """ initialize the server.
        If the server is real node. It will call Accept method in blocking way.
        if the server is simulated. It will set the SetAcceptCallBack
        """
        self.srv_sock = self.node.create_sock({'type':'server', 'proto':'tcp'})
        self.node.bind(self.srv_sock, (self.addr, self.port))
        self.node.listen(self.srv_sock, 5)

        if self.node.NODE_TYPE.startswith('real'):
            while True:
                client_sock, address = self.node.accept(self.srv_sock)
                self._trigger('recv_request_conn', client_sock, address)
        elif self.node.NODE_TYPE.startswith('sim'):
            self._sim_node_init()
        else:
            raise Exception("Unknown Node Type")

    def _sim_node_init(self):
        """initialize for ns3 simulated node, ns3 sim node doesn't support blocking mode
        instead we need to set the callback"""
        self.logger.debug('sim_node initialization')
        def connect_request(sock, addr):
            self.logger.info(' receive connect_request at sock [%s] from [%s]'%(str(sock), str(addr)))
            return True

        def connect_created(client_sock, address):
            self.logger.info('connect_created for client sock [%s] and address[%s]'%(str(client_sock), str(address)))
            self.node.sockets[client_sock] = {'type':'client', 'proto': 'tcp'}
            self._trigger('recv_request_conn', client_sock, address)

        self.srv_sock.SetAcceptCallback(connect_request, connect_created)

    def recv_request_conn(self, client_sock, address):
        """call back for receive the connection request
        """
        self.logger.info('receive request from addr: %s'%(str(address)))
        self.node.send(client_sock, 'connect_ack')
        # self.node.recv(client_sock, 512, self.dispatcher,
        self.node.recv(client_sock, 512, self.node.dispatcher,
                threaded=True)

    def dispatcher(self, sock, data):
        """just enclosure of CMD dispatcher"""
        try:
            CMD.dispatcher(self, sock, data)
        except Exception as e:
            self.logger.error('unknow message: %s from %s'%(data, self.node.sockets[sock]))
            self.logger.exception("\n----------------\n the error is: \n" + \
                    str(e) + \
                    "\n----------------\n")
            self.node.send(sock, 'you have sent me a unknown message')

    def verify_master(self, sock, data):
        """verify the identity of the master"""
        if data['password'][0] == BOT_MASTER_PASSWORD:
            self.logger.info( 'bot master password verfied' )
            self.node.set_master_sock(sock)
            self.node.send(sock, self._cmd_to_json('event=echo;msg=verifed, hi master, what you want to do?'))


    def echo_bots(self, sock, data):
        """send echo command to all bots"""
        self.logger.info('start to echo_bots' )
        new_data = copy.deepcopy(data)
        new_data['event'] = ['echo']
        for client_sock in self.node.client_socks:
            self.node.send(client_sock, self._dump_json(new_data))

    def disconnect(self, sock):
        self.logger.info('receive disconnect request')
        return False
