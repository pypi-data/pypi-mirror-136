import io
import enum
import os
import ssl
from urllib.parse import urlparse
from ftplib import FTP, error_perm, FTP_TLS
from typing import Any, List, Dict, Optional, Tuple

from drb import DrbNode
from drb.abstract_node import AbstractNode
from drb.factory import DrbFactory
from drb.exceptions import DrbException, DrbNotImplementationException
from drb.path import ParsedPath

from drb_impl_ftp.basic_auth import BasicAuth
from drb_impl_ftp.execptions import DrbFtpNodeException


def check_args(*args):
    return len(args) > 0 and isinstance(
        args[0],
        int
    ) and args[0] > 0


def check_response(resp: str):
    if int(resp[0]) >= 3:
        raise DrbFtpNodeException(f'ERROR: {resp}')


class Download(io.BytesIO):

    def __init__(self, path: str, chunk_size: int, ftp: FTP):
        self._chunk_size = chunk_size
        self._ftp = ftp
        self._path = path
        self._buff = bytearray(0)
        self.__res = None
        super().__init__(self.__res)

    def download(self, read: int = None):
        """
        Download all the file you want to download or if you give
        a limit to read in argument,
        juste download part of the file.
        :param read: int
        :return: The status code of the download
        """
        self._ftp.voidcmd('TYPE I')
        with self._ftp.transfercmd('RETR %s' % self._path, None) as conn:
            while 1:
                if read is None:
                    data = conn.recv(self._chunk_size)
                else:
                    data = conn.recv(read)
                    self._buff.extend(data)
                    break
                if not data:
                    break
                self._buff.extend(data)

        return self._ftp.voidresp()

    def read(self, *args, **kwargs):
        if not check_args(*args):
            resp = self.download()
        else:
            resp = self.download(args[0])
        check_response(resp)
        return self._buff


class FtpConnection:
    """
    This class use the singleton pattern to provide too
    much connection to the ftp server
    """
    ftp = None

    def __new__(cls,
                auth: BasicAuth = BasicAuth(),
                path: str = None,
                host: str = '',
                protocol=None):
        if cls.ftp is None:
            parsed_uri = urlparse(path)
            context = None
            if protocol is not None:
                context = ssl.SSLContext(protocol=protocol)
            tmp = parsed_uri.netloc.split(':')
            cls.ftp = FTP_TLS(context=context, host=host)
            cls.ftp.connect(tmp[0], int(tmp[1]))
            try:
                cls.ftp.auth()
            except error_perm:
                cls.ftp.close()
                cls.ftp = FTP(host)
                cls.ftp.connect(tmp[0], int(tmp[1]))
            cls.ftp.login(auth.username, auth.password)
        return cls.ftp


class DrbFtpAttributeNames(enum.Enum):
    """
    This Enum class provide us the different
    attribute of a file.
    """
    DIRECTORY = 'directory'
    SIZE = 'size'
    MODIFIED = 'modified'


class DrbFtpNode(AbstractNode):
    ftp = None

    def __init__(self, path, host: str = '',
                 parent: DrbNode = None,
                 auth: BasicAuth = BasicAuth(), protocol=None):
        super().__init__()
        self._original_path = path
        self._path = path
        self._host = host
        self._parent: DrbNode = parent
        self._protocol = protocol
        if parent:
            self.ftp = parent.ftp
        self._attributes: Dict[Tuple[str, str], Any] = None
        self._children: List[DrbNode] = None
        self._auth = auth

    def is_file(self, filename):
        """
        Check if the file given in argument is not a folder.
        :param filename: str
        :return: True if the filename given in argument is a file
        False otherwise
        """
        self.ftp = FtpConnection(self._auth, self._original_path, self._host)
        current = self.ftp.pwd()
        try:
            self.ftp.cwd(filename)
        except error_perm:
            self.ftp.cwd(current)
            return True
        self.ftp.cwd(current)
        return False

    def check_file_exist(self, filename):
        self.ftp = FtpConnection(self._auth, self._original_path, self._host)
        return filename in self.ftp.nlst()

    def get_modification_date(self, file_name):
        self.ftp = FtpConnection(self._auth, self._original_path, self._host)
        line = []
        self.ftp.dir(file_name, line.append)
        tokens = line[0].split(maxsplit=9)
        return tokens[5] + " " + tokens[6] + " " + tokens[7]

    @property
    def name(self) -> str:
        parsed_uri = urlparse(self._path)
        return parsed_uri.path.split('/')[-1]

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def path(self) -> ParsedPath:
        return ParsedPath(self._path)

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {}
            name = DrbFtpAttributeNames.DIRECTORY.value
            self._attributes[(name, None)] = not self.is_file(self.path.path)

            name = DrbFtpAttributeNames.SIZE.value
            if self.is_file(self.path.path):
                self.ftp.voidcmd('TYPE I')
                self._attributes[(name, None)] = self.ftp.size(self.path.path)
            else:
                self._attributes[(name, None)] = None

            name = DrbFtpAttributeNames.MODIFIED.value
            self._attributes[(name, None)] = \
                self.get_modification_date(self.path.path)

        return self._attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        key = (name, namespace_uri)
        if key in self.attributes.keys():
            return self.attributes[key]
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    @property
    def children(self) -> List[DrbNode]:
        self.ftp = FtpConnection(self._auth, self._original_path, self._host)
        if self._children is None:
            self._children = []
            if not self.is_file(self.path.path):
                sorted_child_names = sorted(self.ftp.nlst(self.path.path))
                for filename in sorted_child_names:
                    child = DrbFtpNode(os.path.join(
                        self._original_path, filename),
                        parent=self,
                        auth=self._auth)
                    self._children.append(child)
        return self._children

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if namespace is None:
            if name is None:
                return len(self.children) > 0
            return name in list(map(lambda x: x.name, self.children))

        return False

    def has_impl(self, impl: type) -> bool:
        return impl == io.BytesIO

    def get_impl(self, impl: type, **kwargs) -> Any:
        self.ftp = FtpConnection(self._auth, self._original_path, self._host)
        if self.has_impl(impl):
            return Download(self.path.path, kwargs.get('chunk_size', 12000),
                            self.ftp)
        raise DrbNotImplementationException(
            f'no {impl} implementation found')

    def close(self) -> None:
        if self.ftp is not None:
            self.ftp.close()


class DrbFtpFactory(DrbFactory):
    @staticmethod
    def _create_from_uri_of_node(node: DrbNode):
        uri = node.path.name
        return DrbFtpNode(uri)

    def _create(self, node: DrbNode) -> DrbNode:
        return self._create_from_uri_of_node(node)
