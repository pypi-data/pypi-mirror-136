# ========================================================= #
import requests
import httpx
from typing import Union
from requests.models import Response
from httpx import Response as HttpxResponse
from enum import Enum

# ========================================================= #


class BaseClient:
    """
    These docs are not meant for general users. These are library API references. The actual docs will be
    available on the index page when they are prepared.

    This is the **base client class** for all other REST clients which inherit from this class and implement their own
    endpoints on top of it.
    """

    def __init__(self, api_key: str, connect_timeout: int = 10, read_timeout: int = 10):
        """
        Initiates a Client to be used to access all the endpoints.

        :param api_key: Your API Key. Visit your dashboard to get yours.
        :param connect_timeout: The connection timeout in seconds. Defaults to 10. basically the number of seconds to
                                wait for a connection to be established. Raises a ``ConnectTimeout`` if unable to
                                connect within specified time limit.
        :param read_timeout: The read timeout in seconds. Defaults to 10. basically the number of seconds to wait for
                             date to be received. Raises a ``ReadTimeout`` if unable to connect within the specified
                             time limit.
        """
        self.KEY = api_key
        self.BASE = 'https://api.polygon.io'

        self.time_out_conf = (connect_timeout, read_timeout)
        self.session = requests.session()

        self.session.headers.update({'Authorization': f'Bearer {self.KEY}'})

    # Context Managers
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def close(self):
        """
        Closes the ``requests.Session`` and frees up resources. It is recommended to call this method in your
        exit handlers
        """

        self.session.close()

    # Internal Functions
    def _get_response(self, path: str, params: dict = None,
                      raw_response: bool = True) -> Union[Response, dict]:
        """
        Get response on a path. Meant to be used internally but can be used if you know what you're doing

        :param path: RESTful path for the endpoint. Available on the docs for the endpoint right above its name.
        :param params: Query Parameters to be supplied with the request. These are mapped 1:1 with the endpoint.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to check the
                             status code or inspect the headers. Defaults to True which returns the ``Response`` object.
        :return: A Response object by default. Make ``raw_response=False`` to get JSON decoded Dictionary
        """
        _res = self.session.request('GET', self.BASE + path, params=params, timeout=self.time_out_conf)

        if raw_response:
            return _res

        return _res.json()

    def get_page_by_url(self, url: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the next page of a response. The URl is returned within ``next_url`` attribute on endpoints which support
        pagination (eg the tickers endpoint). If the response doesn't contain this attribute, either all pages were
        received or the endpoint doesn't have pagination. Meant for internal use primarily.

        :param url: The next URL. As contained in ``next_url`` of the response.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: Either a Dictionary or a Response object depending on value of raw_response. Defaults to Dict.
        """
        _res = self.session.request('GET', url)

        if raw_response:
            return _res

        return _res.json()

    def get_next_page(self, old_response: Union[Response, dict],
                      raw_response: bool = False) -> Union[Response, dict, bool]:
        """
        Get the next page using the most recent old response. This function simply parses the next_url attribute
        from the  existing response and uses it to get the next page. Returns False if there is no next page
        remaining (which implies that you have reached the end of all pages or the endpoint doesn't support pagination).

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        try:
            if not isinstance(old_response, (dict, list)):
                old_response = old_response.json()

            _next_url = old_response['next_url']

            return self.get_page_by_url(_next_url, raw_response=raw_response)

        except KeyError:
            return False

    def get_previous_page(self, old_response: Union[Response, dict],
                          raw_response: bool = False) -> Union[Response, dict, bool]:
        """
        Get the previous page using the most recent old response. This function simply parses the previous_url attribute
        from the  existing response and uses it to get the previous page. Returns False if there is no previous page
        remaining (which implies that you have reached the start of all pages or the endpoint doesn't support
        pagination).

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        try:
            if not isinstance(old_response, (dict, list)):
                old_response = old_response.json()

            _prev_url = old_response['previous_url']

            return self.get_page_by_url(_prev_url, raw_response=raw_response)

        except KeyError:
            return False

    def get_all_pages(self, old_response, max_pages: int = None, direction: str = 'next',
                      raw_responses: bool = False):
        """
        A helper function for endpoints which implement pagination using ``next_url`` and ``previous_url`` attributes.
        Can be used externally too to get all responses in a list.

        :param old_response: The last response you had. In most cases, this would be simply the very first response.
        :param max_pages: If you want to limit the number of pages to retrieve. Defaults to None which fetches ALL
                          available pages
        :param direction: The direction to paginate in. Defaults to next which grabs all next_pages. see
                          :class:`polygon.enums.PaginationDirection` for choices
        :param raw_responses: If set to True, the elements in container list, you will get underlying Response object
                              instead of the json formatted dict/list. Only use if you need to check status codes or
                              headers. Defaults to False, which makes it return decoded data in list.
        :return: A list of responses. By default, responses are actual json decoded dict/list. Depending on value of
                 ``raw_response``
        """

        direction, container, _res = self._change_enum(direction, str), [], old_response
        if not max_pages:
            max_pages = float('inf')

        if direction in ['prev', 'previous']:
            fn = self.get_previous_page
        else:
            fn = self.get_next_page

        # Start paginating
        while 1:
            if len(container) >= max_pages:
                break

            _res = fn(_res, raw_response=True)

            if not _res:
                break

            if raw_responses:
                container.append(_res)
                continue

            container.append(_res.json())

        return container

    def _paginate(self, _res, merge_all_pages: bool = True, max_pages: int = None, raw_page_responses: bool = False):
        """
        Internal function to call the core pagination methods to build the response object to be parsed by individual
        methods.

        :param merge_all_pages: whether to merge all the pages into one response. defaults to True
        :param max_pages: number of pages to fetch. defaults to all available pages.
        :param raw_page_responses: whether to keep raw response objects or decode them. Only considered if
                                   merge_all_pages is set to False. Defaults to False.
        :return:
        """

        if isinstance(max_pages, int):
            max_pages -= 1

        # How many pages do you want?? YES!!!
        if merge_all_pages:  # prepare for a merge
            pages = [_res.json()] + self.get_all_pages(_res, max_pages=max_pages)
        elif raw_page_responses:  # we don't need your help, adventurer (no merge, no decoding)
            return [_res] + self.get_all_pages(_res, raw_responses=True, max_pages=max_pages)
        else:  # okay a little bit of help is fine  (no merge, only decoding)
            return [_res.json()] + self.get_all_pages(_res, max_pages=max_pages)

        # We need your help adventurer  (decode and merge)
        container = []
        try:
            for page in pages:
                container += page['results']
        except KeyError:
            return pages

        return container

    @staticmethod
    def _change_enum(val: Union[str, Enum, float, int], allowed_type=str):
        if isinstance(val, Enum):
            try:
                return val.value

            except AttributeError:
                raise ValueError(f'The value supplied: ({val}) does not match the required type: ({allowed_type}). '
                                 f'Please consider using the  specified enum in the docs for this function or recheck '
                                 f'the value supplied.')

        if isinstance(allowed_type, list):
            if type(val) in allowed_type:
                return val

            raise ValueError(f'The value supplied: ({val}) does not match the required type: ({allowed_type}). '
                             f'Please consider using the  specified enum in the docs for this function or recheck '
                             f'the value supplied.')

        if isinstance(val, allowed_type) or val is None:
            return val


# ========================================================= #

class BaseAsyncClient:
    """
    These docs are not meant for general users. These are library API references. The actual docs will be
    available on the index page when they are prepared.

    This is the **base async client class** for all other REST clients which inherit from this class and implement
    their own endpoints on top of it.
    """

    def __init__(self, api_key: str, connect_timeout: int = 10, read_timeout: int = 10, pool_timeout: int = 10,
                 max_connections: int = None, max_keepalive: int = None, write_timeout: int = 10):
        """
        Initiates a Client to be used to access all the endpoints.

        :param api_key: Your API Key. Visit your dashboard to get yours.
        :param connect_timeout: The connection timeout in seconds. Defaults to 10. basically the number of seconds to
                                wait for a connection to be established. Raises a ``ConnectTimeout`` if unable to
                                connect within specified time limit.
        :param read_timeout: The read timeout in seconds. Defaults to 10. basically the number of seconds to wait for
                             data to be received. Raises a ``ReadTimeout`` if unable to connect within the specified
                             time limit.
        :param pool_timeout: The pool timeout in seconds. Defaults to 10. Basically the number of seconds to wait while
                             trying to get a connection from connection pool. Do NOT change if you're unsure of what it
                             implies
        :param max_connections: Max number of connections in the pool. Defaults to NO LIMITS. Do NOT change if you're
                                unsure of application
        :param max_keepalive: max number of allowable keep alive connections in the pool. Defaults to no limit. Do NOT
                              Do NOT change if you're unsure of the applications.
        :param write_timeout: The write timeout in seconds. Defaults to 10. basically the number of seconds to wait for
                             data to be written/posted. Raises a ``WriteTimeout`` if unable to connect within the
                             specified time limit.
        """
        self.KEY = api_key
        self.BASE = 'https://api.polygon.io'

        self.time_out_conf = httpx.Timeout(connect=connect_timeout, read=read_timeout, pool=pool_timeout,
                                           write=write_timeout)
        self._conn_pool_limits = httpx.Limits(max_connections=max_connections,
                                              max_keepalive_connections=max_keepalive)
        self.session = httpx.AsyncClient(timeout=self.time_out_conf, limits=self._conn_pool_limits)

        self.session.headers.update({'Authorization': f'Bearer {self.KEY}'})

    # Context Managers
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    async def close(self):
        """
        Closes the ``httpx.AsyncClient`` and frees up resources. It is recommended to call this method in your
        exit handlers. This method should be awaited as this is a coroutine.
        """

        await self.session.aclose()

    # Internal Functions
    async def _get_response(self, path: str, params: dict = None,
                            raw_response: bool = True) -> Union[HttpxResponse, dict]:
        """
        Get response on a path - meant to be used internally but can be used if you know what you're doing

        :param path: RESTful path for the endpoint. Available on the docs for the endpoint right above its name.
        :param params: Query Parameters to be supplied with the request. These are mapped 1:1 with the endpoint.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to check the
                             status code or inspect the headers. Defaults to True which returns the ``Response`` object.
        :return: A Response object by default. Make ``raw_response=False`` to get JSON decoded Dictionary
        """
        _res = await self.session.request('GET', self.BASE + path, params=params)

        if raw_response:
            return _res

        return _res.json()

    async def get_page_by_url(self, url: str, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the next page of a response. The URl is returned within ``next_url`` attribute on endpoints which support
        pagination (eg the tickers endpoint). If the response doesn't contain this attribute, either all pages were
        received or the endpoint doesn't have pagination. Meant for internal use primarily.

        :param url: The next URL. As contained in ``next_url`` of the response.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: Either a Dictionary or a Response object depending on value of raw_response. Defaults to Dict.
        """
        _res = await self.session.request('GET', url)

        if raw_response:
            return _res

        return _res.json()

    async def get_next_page(self, old_response: Union[HttpxResponse, dict],
                            raw_response: bool = False) -> Union[HttpxResponse, dict, bool]:
        """
        Get the next page using the most recent old response. This function simply parses the next_url attribute
        from the  existing response and uses it to get the next page. Returns False if there is no next page
        remaining (which implies that you have reached the end of all pages or the endpoint doesn't support
        pagination) - Async method

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        try:
            if not isinstance(old_response, dict):
                old_response = old_response.json()

            _next_url = old_response['next_url']

            return await self.get_page_by_url(_next_url, raw_response=raw_response)

        except KeyError:
            return False

    async def get_previous_page(self, old_response: Union[HttpxResponse, dict],
                                raw_response: bool = False) -> Union[HttpxResponse, dict, bool]:
        """
        Get the previous page using the most recent old response. This function simply parses the previous_url attribute
        from the  existing response and uses it to get the previous page. Returns False if there is no previous page
        remaining (which implies that you have reached the start of all pages or the endpoint doesn't support
        pagination) - Async method

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        try:
            if not isinstance(old_response, dict):
                old_response = old_response.json()

            _prev_url = old_response['previous_url']

            return await self.get_page_by_url(_prev_url, raw_response=raw_response)

        except KeyError:
            return False

    async def get_all_pages(self, old_response, max_pages: int = None, direction: str = 'next',
                            raw_responses: bool = False):
        """
        A helper function for endpoints which implement pagination using ``next_url`` and ``previous_url`` attributes.
        Can be used externally too to get all responses in a list.

        :param old_response: The last response you had. In most cases, this would be simply the very first response.
        :param max_pages: If you want to limit the number of pages to retrieve. Defaults to None which fetches ALL
                          available pages
        :param direction: The direction to paginate in. Defaults to next which grabs all next_pages. see
                          :class:`polygon.enums.PaginationDirection` for choices
        :param raw_responses: If set to True, the elements in container list, you will get underlying Response object
                              instead of the json formatted dict/list. Only use if you need to check status codes or
                              headers. Defaults to False, which makes it return decoded data in list.
        :return: A list of responses. By default, responses are actual json decoded dict/list. Depending on value of
                 ``raw_response``
        """

        direction, container, _res = self._change_enum(direction, str), [], old_response
        if not max_pages:
            max_pages = float('inf')

        if direction in ['prev', 'previous']:
            fn = self.get_previous_page
        else:
            fn = self.get_next_page

        # Start paginating
        while 1:
            if len(container) >= max_pages:
                break

            _res = await fn(_res, raw_response=True)

            if not _res:
                break

            if raw_responses:
                container.append(_res)
                continue

            container.append(_res.json())

        return container

    async def _paginate(self, _res, merge_all_pages: bool = True, max_pages: int = None,
                        raw_page_responses: bool = False):
        """
        Internal function to call the core pagination methods to build the response object to be parsed by individual
        methods.

        :param merge_all_pages: whether to merge all the pages into one response. defaults to True
        :param max_pages: number of pages to fetch. defaults to all available pages.
        :param raw_page_responses: whether to keep raw response objects or decode them. Only considered if
                                   merge_all_pages is set to False. Defaults to False.
        :return:
        """

        if isinstance(max_pages, int):
            max_pages -= 1

        # How many pages do you want?? YES!!!
        if merge_all_pages:  # prepare for a merge
            pages = [_res.json()] + await self.get_all_pages(_res, max_pages=max_pages)
        elif raw_page_responses:  # we don't need your help, adventurer (no merge, no decoding)
            return [_res] + await self.get_all_pages(_res, raw_responses=True, max_pages=max_pages)
        else:  # okay a little bit of help is fine  (no merge, only decoding)
            return [_res.json()] + await self.get_all_pages(_res, max_pages=max_pages)

        # We need your help adventurer  (decode and merge)
        container = []
        try:
            for page in pages:
                container += page['results']
        except KeyError:
            return pages

        return container

    @staticmethod
    def _change_enum(val: Union[str, Enum, float, int], allowed_type=str):
        if isinstance(val, Enum):
            try:
                return val.value

            except AttributeError:
                raise ValueError(f'The value supplied: ({val}) does not match the required type: ({allowed_type}). '
                                 f'Please consider using the  specified enum in the docs for this function or recheck '
                                 f'the value supplied.')

        if isinstance(allowed_type, list):
            if type(val) in allowed_type:
                return val

            raise ValueError(f'The value supplied: ({val}) does not match the required type: ({allowed_type}). '
                             f'Please consider using the  specified enum in the docs for this function or recheck '
                             f'the value supplied.')

        if isinstance(val, allowed_type) or val is None:
            return val


# ========================================================= #


if __name__ == '__main__':  # Tests
    print('Don\'t You Dare Running Lib Files Directly')

# ========================================================= #
