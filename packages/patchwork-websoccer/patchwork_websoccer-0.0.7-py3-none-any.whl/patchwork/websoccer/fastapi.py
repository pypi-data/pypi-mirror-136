# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Callable, Any, Awaitable

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from patchwork.websoccer.court.base import Court
from patchwork.websoccer.soccer import ws_protocol_handler

logger = logging.getLogger('patchwork.websoccer.fastapi')


def noop_authorizer():
    return None


async def all_permitted(auth, topic):
    return True


def bind_fastapi(
        court: Court,
        authorizer: Callable = None,
        permissions: Callable[[Any, str], Awaitable[bool]] = all_permitted
):
    """
    Binds court instance to the FastAPI, by returning a router which can be easily included
    at desired path.
    Optional authorizer is a FastAPI dependency which is called to determine if incoming connection
    is authorized. For unauthorized users it must raise exception.

    :param court:
    :param authorizer:
    :param permissions:
    :return:
    """
    router = APIRouter()

    if authorizer is None:
        authorizer = noop_authorizer

    @router.get('')
    async def describe():
        """
        Returns available transports with their locations
        :return:
        """
        return {
            'endpoints': {
                'websocket': '/ws'
            }
        }

    @router.websocket('/ws')
    async def websocket(websocket: WebSocket, auth=Depends(authorizer)):
        await websocket.accept()
        logger.info(f"{websocket.client}: websocket client accepted")
        client = await court.client(auth, permissions)

        async with client:
            tasks = [asyncio.create_task(websocket.receive_text()), asyncio.create_task(client.__anext__())]

            while True:
                rcv_task, notif_task = tasks
                try:
                    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                except asyncio.CancelledError:
                    break

                if rcv_task in done:
                    exc = rcv_task.exception()
                    if exc is not None:
                        if isinstance(exc, WebSocketDisconnect):
                            # client disconnected
                            break
                        logger.warning(f"{websocket.client}: websocket receive error: {exc.__class__.__name__}({exc})")
                        await websocket.close(code=1011)
                        break
                    else:
                        data = rcv_task.result()
                        # re-create receive task
                        tasks[0] = asyncio.create_task(websocket.receive_text())

                        try:
                            response = await ws_protocol_handler(data, client)
                        except ValueError:
                            logger.info(f"invalid frame received: {data.hex(' ')}")
                            await websocket.close(code=1007)
                        except Exception as e:
                            logger.error(f"unable to process message from {websocket.client}: {e}", exc_info=True)
                            await websocket.close(code=1011)
                        else:
                            await websocket.send_text(response)

                if notif_task in done:
                    exc = notif_task.exception()
                    if exc is not None:
                        logger.warning(
                            f"{websocket.client}: notifications client error: {exc.__class__.__name__}({exc})",
                            exc_info=True
                        )
                        await websocket.close(code=1011)
                    else:
                        record = notif_task.result()
                        await websocket.send_text(record.payload)
                        # re-create notif task
                        tasks[1] = asyncio.create_task(client.__anext__())

            # cancel receive and/or notif task (depending on the while loop break condition)
            for t in tasks:
                if not t.done():
                    t.cancel()

            logger.info(f"{websocket.client}: connection closed")

    # TODO: add SSE endpoint
    # TODO: add HTTP poll endpoint

    @router.on_event('startup')
    async def run_websoccer():
        await court.run()

    @router.on_event('shutdown')
    async def stop_websoccer():
        await court.terminate()

    logger.info("Websoccer court initialized for FastAPI")

    # include router to your FastAPI application
    return router
