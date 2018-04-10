import telnetlib
import logging


class ConnectionError:
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


class TS3Proto:
    bytesin = 0
    bytesout = 0

    EOL = b'\n\r'

    def __init__(self):
        self._log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        self._conn = None
        self._connected = False

    def connect(self, ip, port):
        try:
            self._conn = telnetlib.Telnet(host=ip, port=port, timeout=5)
            self._connected = True
        except:
            # raise ConnectionError(ip, port)
            raise

        data = self._conn.read_until(self.EOL)
        if data.strip() == "TS3":
            self._conn.read_very_eager()  # Clear buffer
            self._connected = True
            return True

    def disconnect(self):
        if self._connected:
            try:
                self.send("quit")
                self._conn.close()
            except:
                self._log.exception('Error while disconnecting')
            self._connected = False
            self._log.info('Disconnected')
        else:
            self._log.info("Not connected")

    def send_command(self, command, keys=None, opts=None):
        cmd = self.construct_command(command, keys=keys, opts=opts)

        # Clear read buffer of any stray bytes
        self._conn.read_very_eager()

        # Send command
        self.send('%s\n' % cmd)

        data = []

        max_loop = 10000
        while True:
            resp = self._conn.read_until(self.EOL)
            resp = self.parse_command(resp.decode('utf-8'))
            if 'command' in resp:
                break
            else:
                data.append(resp)
            max_loop -= 1
            # Prevent infinite loops
            if max_loop <= 0:
                self._log.error("Maximum loop counter reached, aborting to prevent infinite loop.")
                break

        # Clear read buffer of any stray bytes
        self._conn.read_very_eager()

        if resp['command'] == 'error':
            if resp['keys']['id'] == '0':
                if data:
                    if len(data) > 1:
                        return data
                    else:
                        return data[0]
                else:
                    return resp['keys']['id']
            else:
                raise TeamspeakError(resp['keys']['id'])

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
                if len(v) > 2:
                    # Fix the stupidities in TS3 escaping
                    v = [v[0], '='.join(v[1:])]
                key, value = v
                keys[key] = self._unescape_str(value)
            elif not v == ['']:
                if v[0][0] and v[0][0] == '-':
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

        if isinstance(value, int):
            return "%d" % value
        value = value.replace("\\", r'\\')
        for i, j in ts3_escape.items():
            value = value.replace(i, j)
        return value

    @staticmethod
    def _unescape_str(value):
        """
        Unescape a TS3 compatible string into a normal string
        @param value: Value
        @type value: string/int
        """

        if isinstance(value, int):
            return "%d" % value
        value = value.replace(r"\\", "\\")
        for i, j in ts3_escape.items():
            value = value.replace(j, i)
        return value

    def send(self, payload):
        if self._connected:
            self._log.debug('Sent: %s' % payload)
            self._conn.write(payload.encode('utf-8'))


class TS3Server(TS3Proto):
    def __init__(self, ip, port, id=0):
        """
        Abstraction class for TS3 Servers
        @param ip: IP Address
        @type ip: str
        @param port: Port Number
        @type port: int
        """
        TS3Proto.__init__(self)

        self.connect(ip, port)

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
        @type msg: str
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


class TeamspeakError(Exception):
    def __init__(self, code, msg=None):
        self.code = str(code)
        if not msg:
            msg = ts3_errors[self.code]
        self.msg = msg

    def __str__(self):
        return self.code + ' ' + self.msg

ts3_errors = {
    '0': 'unknown error code',
    '1': 'undefined error',
    '2': 'not implemented',
    '3': '',
    '4': '',
    '5': 'library time limit reached',
    '256': 'command not found',
    '257': 'unable to bind network port',
    '258': 'no network port available',
    '512': 'invalid clientID',
    '513': 'nickname is already in use',
    '514': 'invalid error code',
    '515': 'max clients protocol limit reached',
    '516': 'invalid client type',
    '517': 'already subscribed',
    '518': 'not logged in',
    '519': 'could not validate client identity',
    '520': 'invalid loginname or password',
    '521': 'too many clones already connected',
    '522': 'client version outdated, please update',
    '523': 'client is online',
    '524': 'client is flooding',
    '525': 'client is modified',
    '526': 'can not verify client at this moment',
    '527': 'client is not permitted to log in',
    '528': 'client is not subscribed to the channel',
    '768': 'invalid channelID',
    '769': 'max channels protocol limit reached',
    '770': 'already member of channel',
    '771': 'channel name is already in use',
    '772': 'channel not empty',
    '773': 'can not delete default channel',
    '774': 'default channel requires permanent',
    '775': 'invalid channel flags',
    '776': 'permanent channel can not be child of non permanent channel',
    '777': 'channel maxclient reached',
    '778': 'channel maxfamily reached',
    '779': 'invalid channel order',
    '780': 'channel does not support filetransfers',
    '781': 'invalid channel password',
    '782': 'channel is private channel',
    '783': 'invalid security hash supplied by client',
    '1024': 'invalid serverID',
    '1025': 'server is running',
    '1026': 'server is shutting down',
    '1027': 'server maxclient reached',
    '1028': 'invalid server password',
    '1029': 'deployment active',
    '1030': 'unable to stop own server in your connection class',
    '1031': 'server is virtual',
    '1032': 'server wrong machineID',
    '1033': 'server is not running',
    '1034': 'server is booting up',
    '1035': 'server got an invalid status for this operation',
    '1036': 'server modal quit',
    '1037': 'server version is too old for command',
    '1280': 'database error',
    '1281': 'database empty result set',
    '1282': 'database duplicate entry',
    '1283': 'database no modifications',
    '1284': 'database invalid constraint',
    '1285': 'database reinvoke command',
    '1536': 'invalid quote',
    '1537': 'invalid parameter count',
    '1538': 'invalid parameter',
    '1539': 'parameter not found',
    '1540': 'convert error',
    '1541': 'invalid parameter size',
    '1542': 'missing required parameter',
    '1543': 'invalid checksum',
    '1792': 'virtual server got a critical error',
    '1793': 'Connection lost',
    '1794': 'not connected',
    '1795': 'no cached connection info',
    '1796': 'currently not possible',
    '1797': 'failed connection initialization',
    '1798': 'could not resolve hostname',
    '1799': 'invalid server connection handler ID',
    '1800': 'could not initialize Input Manager',
    '1801': 'client library not initialized',
    '1802': 'server library not initialized',
    '1803': 'too many whisper targets',
    '1804': 'no whisper targets found',
    '2048': 'invalid file name',
    '2049': 'invalid file permissions',
    '2050': 'file already exists',
    '2051': 'file not found',
    '2052': 'file input/output error',
    '2053': 'invalid file transfer ID',
    '2054': 'invalid file path',
    '2055': 'no files available',
    '2056': 'overwrite excludes resume',
    '2057': 'invalid file size',
    '2058': 'file already in use',
    '2059': 'could not open file transfer connection',
    '2060': 'no space left on device (disk full?)',
    '2061': "file exceeds file system's maximum file size",
    '2062': 'file transfer connection timeout',
    '2063': 'lost file transfer connection',
    '2064': 'file exceeds supplied file size',
    '2065': 'file transfer complete',
    '2066': 'file transfer canceled',
    '2067': 'file transfer interrupted',
    '2068': 'file transfer server quota exceeded',
    '2069': 'file transfer client quota exceeded',
    '2070': 'file transfer reset',
    '2071': 'file transfer limit reached',
    '2304': 'preprocessor disabled',
    '2305': 'internal preprocessor',
    '2306': 'internal encoder',
    '2307': 'internal playback',
    '2308': 'no capture device available',
    '2309': 'no playback device available',
    '2310': 'could not open capture device',
    '2311': 'could not open playback device',
    '2312': 'ServerConnectionHandler has a device registered',
    '2313': 'invalid capture device',
    '2314': 'invalid clayback device',
    '2315': 'invalid wave file',
    '2316': 'wave file type not supported',
    '2317': 'could not open wave file',
    '2318': 'internal capture',
    '2319': 'device still in use',
    '2320': 'device already registerred',
    '2321': 'device not registered/known',
    '2322': 'unsupported frequency',
    '2323': 'invalid channel count',
    '2324': 'read error in wave',
    '2325': 'sound need more data',
    '2326': 'sound device was busy',
    '2327': 'there is no sound data for this period',
    '2328': 'Channelmask set bits count (speakers) is not the same as channel (count)',
    '2560': 'invalid group ID',
    '2561': 'duplicate entry',
    '2562': 'invalid permission ID',
    '2563': 'empty result set',
    '2564': 'access to default group is forbidden',
    '2565': 'invalid size',
    '2566': 'invalid value',
    '2567': 'group is not empty',
    '2568': 'insufficient client permissions',
    '2569': 'insufficient group modify power',
    '2570': 'insufficient permission modify power',
    '2571': 'template group is currently used',
    '2572': 'permission error',
    '2816': 'virtualserver limit reached',
    '2817': 'max slot limit reached',
    '2818': 'license file not found',
    '2819': 'license date not ok',
    '2820': 'unable to connect to accounting server',
    '2821': 'unknown accounting error',
    '2822': 'accounting server error',
    '2823': 'instance limit reached',
    '2824': 'instance check error',
    '2825': 'license file invalid',
    '2826': 'virtualserver is running elsewhere',
    '2827': 'virtualserver running in same instance already',
    '2828': 'virtualserver already started',
    '2829': 'virtualserver not started',
    '2830': '',
    '3072': 'invalid message id',
    '3328': 'invalid ban id',
    '3329': 'connection failed, you are banned',
    '3330': 'rename failed, new name is banned',
    '3331': 'flood ban',
    '3584': 'unable to initialize tts',
    '3840': 'invalid privilege key',
    '4096': '',
    '4097': '',
    '4098': '',
    '4099': '',
    '4100': '',
    '4101': '',
    '4102': '',
    '4103': '',
    '4352': 'invalid password',
    '4353': 'invalid request',
    '4354': 'no (more) slots available',
    '4355': 'pool missing',
    '4356': 'pool unknown',
    '4357': 'unknown ip location (perhaps LAN ip?)',
    '4358': 'internal error (tried exceeded)',
    '4359': 'too many slots requested',
    '4360': 'too many reserved',
    '4361': 'could not connect to provisioning server',
    '4368': 'authentication server not connected',
    '4369': 'authentication data too large',
    '4370': 'already initialized',
    '4371': 'not initialized',
    '4372': 'already connecting',
    '4373': 'already connected',
    '4374': '',
    '4375': 'io_error',
    '4376': '',
    '4377': '',
    '4378': '',
}
