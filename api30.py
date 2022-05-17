import json
import re
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Dict, Callable, Any, Tuple, List, Iterable


@dataclass
class Request:
    method: str
    path: str

    @classmethod
    def from_env(cls, env) -> 'Request':
        return cls(
            env['REQUEST_METHOD'],
            env['PATH_INFO']
        )


@dataclass
class Response:
    data: Any = None
    status: HTTPStatus = HTTPStatus.OK
    headers: Dict[str, str] = field(default_factory=dict)

    @property
    def headers_list(self) -> List[Tuple[str, str]]:
        return [(k, v) for k, v in self.headers.items()]

    @property
    def body(self) -> Iterable[bytes]:
        if self.data is None:
            return []
        return [json.dumps(self.data).encode()]


ApiFunction = Callable[[Request, ...], Response]


class Api30:
    def __init__(self):
        self._routes: Dict[Tuple[str, re.Pattern], ApiFunction] = {}
        self._middlewares: List = []

    def __call__(self, environ, start_response: callable) -> Iterable[bytes]:
        req = Request.from_env(environ)
        self._pre_view(req)
        for (method, pattern), function in self._routes.items():
            if req.method == method and (match := pattern.fullmatch(req.path)):
                resp = function(req, *match.groups())
                self._post_view(req, resp)
                start_response(
                    self._format_status(resp.status),
                    resp.headers,
                )
                return resp.body

        start_response(self._format_status(HTTPStatus.NOT_FOUND), [('Content-Type', 'text/plain')])
        return []

    def _pre_view(self, req: Request):
        for m in self._middlewares:
            m.pre(req)

    def _post_view(self, req: Request, resp: Response):
        for m in self._middlewares:
            m.post(req, resp)

    def _format_status(self, status: HTTPStatus) -> str:
        return f'{status.value} {status.name}'

    def add_route(self, method: str, path: str, func: ApiFunction) -> None:
        self._routes[(method, re.compile(path))] = func

    def get(self, path: str, func: ApiFunction) -> None:
        self.add_route('GET', path, func)

    def push_middleware(self, middleware):
        self._middlewares.append(middleware)
