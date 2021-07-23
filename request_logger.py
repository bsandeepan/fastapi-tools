import logging
from typing import Dict

from fastapi import Request

logger = logging.getLogger(__name__)


async def request_to_dict(r: Request) -> Dict:
    """ Map Starlette Request Coroutine to a Dictionary for logging. """
    return dict(
        method=r.method,
        base_url=r.base_url.__str__(),
        endpoint=r.url.path,
        full_path=r.url.__str__(),
        remote_address=f"{r.client.host}:{r.client.port}",  # either can be None
        payload=await r.body(),
        request_id=r.state._state.get("request_id")
        # !WARNING: only activate logging headers if really needed
        # headers=dict(**r.headers),
    )


async def fastapi_logger_async(request: Request):
    """ Logs Incoming requests. """
    logger.info(await request_to_dict(request))

