import functools
import os
import re
import requests
import time
from random import randint
from requests import Session
from requests.exceptions import HTTPError
from requests.packages import urllib3

from .logger import get_logger

logger = get_logger()

RETRY_TIMES = 3
BACKOFF_FACTOR = 1
STATUS_TO_RETRY = (429, 500, 502, 503, 504)
DEFAULT_TIMEOUT = (30, 120)
URL_PATH_PATTERN = re.compile("([^/]).*")
DOMAIN_PATTERN = re.compile(r"^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,63}$")


class HTTP_METHOD:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class RetryException(Exception):
    """Specified exception to retry request."""

    def __init__(self, message):
        super().__init__(message)


def is_ssl_verification():
    return False if os.environ.get("CURL_CA_BUNDLE") == "" else True


def retry(*exceptions):
    """Decorate an async function to execute it a few times before giving up.
    Hopes that problem is resolved by another side shortly.
    Args:
        exceptions (tuple): The exceptions expected during function execution
    """

    def accumulate_cooldown(retry_times, backoff_factor=None):
        backoff_factor = backoff_factor or BACKOFF_FACTOR
        return backoff_factor * (2 ** retry_times) + (randint(1, 999)) * 0.001

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _count = 0
            _errors = None
            while _count < RETRY_TIMES:
                try:
                    return func(*args, **kwargs)
                except exceptions as err:
                    _errors = err
                    if getattr(_errors, "response", None) is not None:
                        if err.response.status_code not in STATUS_TO_RETRY:
                            break

                    _count += 1
                    try:
                        retry_after = int(err.response.headers.get("Retry-After", 0))
                    except Exception:
                        retry_after = accumulate_cooldown(
                            _count, kwargs.get("backoff_factor")
                        )

                    logger.debug(f"Retry attempt {_count} after {retry_after} seconds")
                    time.sleep(retry_after)

            if _errors:
                raise _errors

        return wrapper

    return decorator


@retry(RetryException, HTTPError)
def retry_request(
    method,
    url,
    headers=None,
    files=None,
    data=None,
    json=None,
    params=None,
    auth=None,
    cookies=None,
    hooks=None,
    timeout=DEFAULT_TIMEOUT,
    verify=None,
    session=None,
    proxies=None,
    jsonify=True,
    object_hook=None,
    **kwargs,
):
    """
    Args:
        method: HTTP request method.
        url: HTTP request url.
        session: The session is used to send HTTP request.
        proxies: The proxy configs are applied to session.
        timeout: The specified timeout for HTTP response.
        jsonify: By default it is True, return response content as dictionary.
            If False, return HTTP response object.
        object_hook: The hook is used for json.loads if jsonify is True.
        error_handler: The function is used to handle raised exception and accept
            the exception object(maybe None) as first args of function.
    """

    session = session or Session()
    if isinstance(proxies, dict):
        session.proxies.update(proxies)

    req = requests.Request(
        method=method,
        url=url,
        headers=headers,
        files=files,
        data=data,
        json=json,
        params=params,
        auth=auth,
        cookies=cookies,
        hooks=hooks,
    ).prepare()
    resp_data = None
    verify = verify if isinstance(verify, bool) else is_ssl_verification()
    if verify is False:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    _start_time = time.time()
    _target = f"{method.upper()} {url}"
    logger.debug(f"HTTP request start, {_target}")
    resp = session.send(req, timeout=timeout, verify=verify, **kwargs)
    resp.raise_for_status()
    _dt = time.time() - _start_time
    logger.debug(
        f"HTTP request finish in {_dt:.3f} seconds, {_target}"
    )
    resp_data = resp.json(object_hook=object_hook) if jsonify else resp
    return resp_data


def urljoin(*paths):
    """
    urljoin(*args): Concatenate any number of strings as url path and handle for the
        path which starts with "/".
    Example: urljoin("https://www.pentium.network/", "/users", "me/")
        -> "https://www.pentium.network/users/me"
    """

    _paths = [str(a) for a in paths]
    _paths = (
        _match.group() for _match in map(URL_PATH_PATTERN.search, _paths) if _match
    )
    url_path = os.path.join(*_paths)
    return url_path


def chunks(lst, n):
    """Generator yield n-sized chunks from a list."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
