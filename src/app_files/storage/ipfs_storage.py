"""
           Name: django-ipfs-storage
Original author: Ben Jeffrey (@jeffbr13, https://github.com/jeffbr13)
        License: Mozilla Public License 2.0 (see LICENSE)
            URL: https://github.com/jeffbr13/django-ipfs-storage
         Commit: 7301ef22cd343deed533ed4ecca3c16acdcfc9ea
"""


from urllib.parse import urlparse
import ipfshttpclient
from IPy import IP
from multiaddr import Multiaddr

from django.conf import settings
from django.core.files.base import File, ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


__version__ = '0.0.4'


@deconstructible
class InterPlanetaryFileSystemStorage(Storage):
    """IPFS Django storage backend.

    Only file creation and reading is supported
    due to the nature of the IPFS protocol.
    """

    def __init__(self, api_url=None, gateway_url=None):
        """Connect to Interplanetary File System daemon API to add/pin files.

        :param api_url: IPFS control API base URL.
                        Also configurable via `settings.IPFS_STORAGE_API_URL`.
                        Defaults to 'http://localhost:5001/api/v0/'.
        :param gateway_url: Base URL for IPFS Gateway (for HTTP-only clients).
                            Also configurable via `settings.IPFS_STORAGE_GATEWAY_URL`.
                            Defaults to 'https://ipfs.io/ipfs/'.
        """
        parsed_api_url = urlparse(api_url or getattr(settings, 'IPFS_STORAGE_API_URL', 'http://localhost:5001/api/v0/'))
        self._ipfs_client = ipfshttpclient.connect(
            IPFSHelper.url_to_multiaddr(parsed_api_url),
            parsed_api_url.path.strip('/')
        )
        self.gateway_url = gateway_url or getattr(settings, 'IPFS_STORAGE_GATEWAY_URL', 'https://ipfs.io/ipfs/')

    def _open(self, name: str, mode='rb') -> File:
        """Retrieve the file content identified by multihash.

        :param name: IPFS Content ID multihash.
        :param mode: Ignored. The returned File instance is read-only.
        """
        return ContentFile(self._ipfs_client.cat(name), name=name)

    def _save(self, name: str, content: File) -> str:
        """Add and pin content to IPFS daemon.

        :param name: Ignored. Provided to comply with `Storage` interface.
        :param content: Django File instance to save.
        :return: IPFS Content ID multihash.
        """
        file = self._ipfs_client.add(content, wrap_with_directory=True)

        if len(file) == 2:
            # storing hash for wrapping directory (file[1]) instead of the hash of file itself (file[0]) as only this
            # way file's name will not be lost
            file_wrapped = file[1]
            file_hash = file_wrapped.get('Hash')
            self._ipfs_client.pin.add(file_hash)
            return file_hash
        else:
            raise IOError("An error occurred while uploading the file to IPFS.")

    def get_valid_name(self, name):
        """Returns name. Only provided for compatibility with Storage interface."""
        return name

    def get_available_name(self, name, max_length=None):
        """Returns name. Only provided for compatibility with Storage interface."""
        return name

    def size(self, name: str) -> int:
        """Total size, in bytes, of IPFS content with multihash `name`."""
        return self._ipfs_client.object.stat(name)['CumulativeSize']

    def delete(self, name: str):
        """Unpin IPFS content from the daemon."""
        self._ipfs_client.pin.rm(name)

    def url(self, name: str):
        """Returns an HTTP-accessible Gateway URL by default.

        Override this if you want direct `ipfs://…` URLs or something.

        :param name: IPFS Content ID multihash.
        :return: HTTP URL to access the content via an IPFS HTTP Gateway.
        """
        obj_list = self._ipfs_client.ls(name)

        filename = obj_list.get('Objects')[0].get('Links')[0].get('Name')

        return '{gateway_url}{multihash}/{filename}'.format(gateway_url=self.gateway_url, multihash=name, filename=filename)


class IPFSHelper:
    @staticmethod
    def _detect_dns_type(hostname):
        try:
            ip = IP(hostname)
            return "ip" + str(ip.version())
        except ValueError:
            return "dns4"

    @staticmethod
    def _detect_port_number(scheme):
        if scheme == "http" or scheme == "ws":
            return 80
        elif scheme == "https" or scheme == "wss":
            return 443
        else:
            return 0

    @staticmethod
    def url_to_multiaddr(url, dns_type=None):
        multiaddr_str = ""

        hostname = url.hostname
        scheme = url.scheme

        # dns type
        dt = dns_type
        if dt is None:
            dt = IPFSHelper._detect_dns_type(hostname)
        multiaddr_str += f'/{dt}'

        # hostname
        multiaddr_str += f'/{hostname}'

        # transport layer protocol
        tlp = "tcp"
        if scheme == "udp":
            tlp = "udp"
        multiaddr_str += f'/{tlp}'

        # port
        port = url.port
        if port is None:
            port = IPFSHelper._detect_port_number(scheme)
        multiaddr_str += f'/{port}'

        if scheme != tlp:
            multiaddr_str += f'/{scheme}'

        return Multiaddr(multiaddr_str)
