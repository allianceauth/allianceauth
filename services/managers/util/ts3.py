import socket
import logging


class ConnectionError():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__(self):
        return 'Error connecting to host %s port %s' % (self.ip, self.port)


ts3_escape = {'/': r"\/",
              ' ': r'\s',
              '|': r'\p',
              "\a": r'\a',
              "\b": r'\b',
              "\f": r'\f',
              "\n": r'\n',
              "\r": r'\r',
              "\t": r'\t',
              "\v": r'\v'}


class TS3Proto():
    bytesin = 0
    bytesout = 0

    _connected = False

    def __init__(self):
        self._log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        pass

    def connect(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, port))
        except:
            # raise ConnectionError(ip, port)
            raise
        else:
            self._sock = s
            self._sockfile = s.makefile('r', 0)

        data = self._sockfile.readline()
        if data.strip() == "TS3":
            self._sockfile.readline()
            self._connected = True
            return True

    def disconnect(self):
        self.send_command("quit")
        self._sock.close()
        self._sock = None
        self._connected = False
        self._log.info('Disconnected')

    def send_command(self, command, keys=None, opts=None):
        cmd = self.construct_command(command, keys=keys, opts=opts)
        self.send('%s\n' % cmd)

        data = []

        while True:
            resp = self._sockfile.readline()
            resp = self.parse_command(resp)
            if not 'command' in resp:
                data.append(resp)
            else:
                break

        if resp['command'] == 'error':
            if data and resp['keys']['id'] == '0':
                if len(data) > 1:
                    return data
                else:
                    return data[0]
            else:
                return resp['keys']['id']

    def construct_command(self, command, keys=None, opts=None):
        """
        Constructs a TS3 formatted command string
        Keys can have a single nested list to construct a nested parameter
        @param command: Command list
        @type command: string
        @param keys: Key/Value pairs
        @type keys: dict
        @param opts: Options
        @type opts: list
        """

        cstr = [command]

        # Add the keys and values, escape as needed        
        if keys:
            for key in keys:
                if isinstance(keys[key], list):
                    ncstr = []
                    for nest in keys[key]:
                        ncstr.append("%s=%s" % (key, self._escape_str(nest)))
                    cstr.append("|".join(ncstr))
                else:
                    cstr.append("%s=%s" % (key, self._escape_str(keys[key])))

        # Add in options
        if opts:
            for opt in opts:
                cstr.append("-%s" % opt)

        return " ".join(cstr)

    def parse_command(self, commandstr):
        """
        Parses a TS3 command string into command/keys/opts tuple
        @param commandstr: Command string
        @type commandstr: string
        """

        if len(commandstr.split('|')) > 1:
            vals = []
            for cmd in commandstr.split('|'):
                vals.append(self.parse_command(cmd))
            return vals

        cmdlist = commandstr.strip().split(' ')
        command = None
        keys = {}
        opts = []

        for key in cmdlist:
            v = key.strip().split('=')
            if len(v) > 1:
                # Key
                if len > 2:
                    # Fix the stupidities in TS3 escaping
                    v = [v[0], '='.join(v[1:])]
                key, value = v
                keys[key] = self._unescape_str(value)
            elif v[0][0] == '-':
                # Option
                opts.append(v[0][1:])
            else:
                command = v[0]

        d = {'keys': keys, 'opts': opts}
        if command:
            d['command'] = command
        return d

    @staticmethod
    def _escape_str(value):
        """
        Escape a value into a TS3 compatible string
        @param value: Value
        @type value: string/int
        """

        if isinstance(value, int): return "%d" % value
        value = value.replace("\\", r'\\')
        for i, j in ts3_escape.iteritems():
            value = value.replace(i, j)
        return value

    @staticmethod
    def _unescape_str(value):
        """
        Unescape a TS3 compatible string into a normal string
        @param value: Value
        @type value: string/int
        """

        if isinstance(value, int): return "%d" % value
        value = value.replace(r"\\", "\\")
        for i, j in ts3_escape.iteritems():
            value = value.replace(j, i)
        return value


    def send(self, payload):
        if self._connected:
            self._log.debug('Sent: %s' % payload)
            self._sockfile.write(payload)


class TS3Server(TS3Proto):
    def __init__(self, ip, port, id=0, sock=None):
        """
        Abstraction class for TS3 Servers
        @param ip: IP Address
        @type ip: str
        @param port: Port Number
        @type port: int
        """
        TS3Proto.__init__(self)

        if not sock:
            if self.connect(ip, port) and id > 0:
                self.use(id)
        else:
            self._sock = sock
            self._sockfile = sock.makefile('r', 0)
            self._connected = True

    def login(self, username, password):
        """
        Login to the TS3 Server
        @param username: Username
        @type username: str
        @param password: Password
        @type password: str
        """
        d = self.send_command('login', keys={'client_login_name': username, 'client_login_password': password})
        if d == 0:
            self._log.info('Login Successful')
            return True
        return False

    def serverlist(self):
        """
        Get a list of all Virtual Servers on the connected TS3 instance
        """
        if self._connected:
            return self.send_command('serverlist')

    def gm(self, msg):
        """
        Send a global message to the current Virtual Server
        @param msg: Message
        @type ip: str
        """
        if self._connected:
            return self.send_command('gm', keys={'msg': msg})

    def use(self, id):
        """
        Use a particular Virtual Server instance
        @param id: Virtual Server ID
        @type id: int
        """
        if self._connected and id > 0:
            self.send_command('use', keys={'sid': id})