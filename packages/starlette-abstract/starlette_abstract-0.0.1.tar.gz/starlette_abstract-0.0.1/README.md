# Abstract Middleware for Starlette

`AbstractHTTPMiddleware` is replacing the original Starlette's `BaseHTTPMiddleware`. 

In the original `BaseHTTPMiddleware` a `RuntimeError` with message `No response returned` is raised when two or more middlewares inheriting from the `BaseHTTPMiddleware` were used in the middleware stack following each other.

The new `AbstractHTTPMiddleware` is simply handling a situation when client closes connection early, during the original request is processing in endpoint. Normally an `anyio.EndOfStream` would be raised, causing a `RuntimeError` exception with message `No response returned`. This situation is fully logged and handled by returning a new response with `status_code=499` and `content='Client closed connection'`.

### Instalation
```bash
pip install starlette_abstract
```

### Simple Example
```python
from starlette_abstract.middleware import AbstractHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

class MyCustomMiddleware(AbstractHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # do something with request
        response = await call_next(request)

        # do something with response
        return response
```
