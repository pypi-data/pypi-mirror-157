import abc
import io

from drb.utils.keyringconnection import kr_get_auth, kr_check
from drb.exceptions import DrbException, DrbNotImplementationException, \
    DrbFactoryException

from defusedxml import ElementTree

from drb import DrbNode, AbstractNode
from drb.path import ParsedPath
from requests.auth import AuthBase
from typing import Any, Dict, List, Optional, Tuple

from drb.factory import DrbFactoryResolver
from drb_impl_http import DrbHttpNode
from drb_impl_xml import XmlNode


class WXSServiceNode(AbstractNode, abc.ABC):
    """
    Common WXsNode interface
    """

    def __init__(self, service_url, auth: AuthBase = None, **kwargs):
        super(AbstractNode, self).__init__()
        self._original_service_url = service_url
        self._service_url = service_url
        self.__auth = auth
        self._children = None
        self.__path = None
        self.__other_key = kwargs
        self._version = None

    def read_capabilities(self, xml_node: DrbNode):
        for key_attr in xml_node.attributes.keys():
            if key_attr[0].lower() == 'version':
                self._version = xml_node.get_attribute(key_attr[0])

    def get_auth(self) -> Optional[AuthBase]:
        """
        Returns the associated authentication required to access to the Wxs
        service.
        :returns: an authentication compatible with requests library.
        :rtype: AuthBase
        """
        if self.__auth is not None:
            return self.__auth
        if kr_check(self._original_service_url):
            return kr_get_auth(self._original_service_url)

    @property
    @abc.abstractmethod
    def type_service(self):
        raise NotImplementedError

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def path(self) -> ParsedPath:
        if self.__path is None:
            self.__path = ParsedPath(self._service_url)
        return self.__path

    @property
    def parent(self) -> Optional[DrbNode]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    @staticmethod
    def compute_key_url(url, arguments: dict):
        if arguments is not None:
            for (key, value) in arguments.items():
                if isinstance(value, (list, tuple)):
                    for value_item in value:
                        url += f'&{key}={value_item}'
                else:
                    url += f'&{key}={value}'
        return url

    def url_service(self, request: str):
        url = f'{self._service_url}?request={request}' \
               f'&service={self.type_service}'
        return WXSServiceNode.compute_key_url(url, self.__other_key)

    def get_capabilities(self):
        get_caps = WXSNodeOperationGetCapabilities(self)
        return get_caps.children()

    @property
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            try:
                self.read_capabilities(self.get_capabilities())
            except DrbException as ex:
                raise DrbFactoryException(
                    f'Unsupported Wxs service: {self.name}')

        return self._children

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException('WxsNode has no attribute')

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbException(f"Wxs Not doesn't support {impl} implementation")

    def __eq__(self, other):
        return isinstance(other, WXSServiceNode) and \
            self._service_url == other._service_url

    def __hash__(self):
        return hash(self._service_url)


class WXSNodeOperation(AbstractNode):

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbNotImplementationException(f'no {impl} '
                                            f'implementation found')

    def __compute_url(self, arguments: dict):
        url = self.__parent.url_service(self.name)
        if self._version is not None and len(self._version) > 0 \
                and 'version' not in arguments.keys():
            url = WXSServiceNode.compute_key_url(url,
                                                 {'version': self._version})
        return WXSServiceNode.compute_key_url(url, arguments)

    def __init__(self,
                 source: WXSServiceNode,
                 name: str,
                 namespace: str,
                 attributes: dict = {},
                 version: str = None):
        super(AbstractNode, self).__init__()

        self._name = name
        self._attributes = attributes
        self._namespace = namespace
        self.__parent = source
        self._version = version

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self._namespace

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def path(self) -> ParsedPath:
        return self.__path

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.__parent

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {}
            for attribute_name in self._data_set.ncattrs():
                self._attributes[(attribute_name, None)] = \
                    getattr(self._data_set, attribute_name)

        return self._attributes

    @property
    def children(self) -> List[DrbNode]:
        return []

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        key = (name, namespace_uri)
        if key in self.attributes.keys():
            return self.attributes[key]
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    @staticmethod
    def _get_content_type(node):
        content_type = ''
        for attr_key in node.attributes:
            if attr_key[0].lower() == 'content-type':
                content_type = node.get_attribute(attr_key[0])
        return content_type

    def _get_child(self, item):
        if isinstance(item, dict):
            url = self.__compute_url(item)
            node = DrbHttpNode(url, auth=self.__parent.get_auth())
            impl = node.get_impl(io.BytesIO)

            content_type = self._get_content_type(node)
            if 'text/xml' in content_type:
                tree = ElementTree.parse(impl)
                node_child = XmlNode(tree.getroot())
            elif 'text/html' in content_type:
                tree = ElementTree.parse(impl)
                node_child = XmlNode(tree.getroot())
            else:
                node_child = DrbFactoryResolver().create(node)
            return node_child
        else:
            raise KeyError(f'Invalid key: {type(item)}')

    def __getitem__(self, item):
        return self._get_child(item)


class WXSNodeOperationGetCapabilities(WXSNodeOperation):
    def __init__(self,
                 source: WXSServiceNode):
        super().__init__(source, 'GetCapabilities', None)

    def children(self) -> List[DrbNode]:
        return self._get_child({})
