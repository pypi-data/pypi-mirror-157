import asyncio
import inspect
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Response, WebSocket, status
from httpx import AsyncClient
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse
from websockets import WebSocketClientProtocol, connect

from databutton.utils.config import MAX_WEBSOCKET_MESSAGE_SIZE_IN_MB

# Decorator for defining a method as a streamlit app


DEFAULT_MEMORY = "256Mi"
DEFAULT_CPU = "0.2"


@dataclass
class StreamlitApp:
    filename: str
    uid: str
    name: str
    route: str
    memory: str = DEFAULT_MEMORY
    cpu: str = DEFAULT_CPU
    port: int = 0


# Global var to store all streamlit apps
_streamlit_apps: List[StreamlitApp] = []


def streamlit(
    route: str,
    name: str = None,
    memory: Optional[str] = None,
    cpu: Optional[str] = None,
):
    def app(func):
        cleaned_route = route if route.endswith("/") else route + "/"
        splitted_route = list(filter(None, cleaned_route.split("/")))
        uid = "-".join(splitted_route)
        filename = Path(".databutton", "app", f"tmp-{uid}.py")
        filename.parent.mkdir(parents=True, exist_ok=True)

        module_name = inspect.getmodule(func).__name__
        func_name = func.__name__
        import_statement = f"from {module_name} import {func_name}"

        with open(filename, "w") as f:
            f.write(import_statement)
            f.write("\n")
            f.write("\n")
            f.write(f"{func_name}()")
        st = StreamlitApp(
            filename=str(filename),
            route=cleaned_route,
            name=name if name else func_name,
            uid=uid,
        )
        if memory:
            st.memory = memory
        if cpu:
            st.cpu = cpu
        _streamlit_apps.append(st)
        return func

    return app


async def get_proxy(route: str, rest: str = "", port: int = 0):
    # Find correct app
    client = AsyncClient(base_url=f"http://localhost:{port}/")
    req = client.build_request("GET", rest)
    r = await client.send(req, stream=True)
    return StreamingResponse(
        r.aiter_raw(), background=BackgroundTask(r.aclose), headers=r.headers
    )


def create_streamlit_router(app: StreamlitApp):
    router = APIRouter()

    @router.get(app.route + "{rest:path}")
    async def _get_app(rest: str):
        try:
            return await get_proxy(app.route, rest, app.port)
        except Exception as e:
            # Simply ignore messages. It's not this one's job to make sure it's up and running
            logging.debug("Error in http proxy", extra=e)

    @router.websocket(app.route + "stream")
    async def handle_proxied_websocket(ws_client: WebSocket):
        try:
            await ws_client.accept()
            port = app.port
            if port is None:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            max_size = MAX_WEBSOCKET_MESSAGE_SIZE_IN_MB * int(1e6)
            async with connect(
                f"ws://localhost:{port}/stream", max_size=max_size
            ) as ws_server:
                fwd_task = asyncio.create_task(forward(ws_client, ws_server))
                rev_task = asyncio.create_task(reverse(ws_client, ws_server))
                await asyncio.gather(fwd_task, rev_task)
        except Exception as e:
            # Simply ignore messages. It's not this one's job to make sure it's up and running
            logging.debug("Error in websocket proxy", extra=e)

    return router


async def forward(ws_client: WebSocket, ws_server: WebSocketClientProtocol):
    while True:
        data = await ws_client.receive_bytes()
        await ws_server.send(data)


async def reverse(ws_client: WebSocket, ws_server: WebSocketClientProtocol):
    while True:
        data = await ws_server.recv()
        await ws_client.send_text(data)
