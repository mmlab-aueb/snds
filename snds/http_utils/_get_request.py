import aiohttp

from contextlib import asynccontextmanager
#from mininet.log    import MininetLogger
from typing import Dict, Any, AsyncGenerator

# Define a new logging format
#standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#
#_logger = MininetLogger(os.path.basename(__file__))
##TODO hardcoded log level
#_logger.setLogLevel('debug')

#for handler in _logger.handlers:
#    handler.setFormatter(logging.Formatter(standard_logging))

@asynccontextmanager
async def _aiohttp_get(headers: Dict[str, Any], url: str, params: Dict[str, Any]) -> AsyncGenerator:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params) as response:
            yield response

async def get_request(url: str, headers: Dict[str, Any], params: Dict[str, Any]):
    try:
        # Check if the response status is successful (e.g., 200 OK) if response.status != 200:
        async with _aiohttp_get(headers=headers, url=url, params=params) as response: 
            if response.status != 200:
                error_message = await response.text()
                raise aiohttp.HttpProcessingError(message=f"Unexpected status {response.status}: {error_message}", status=response.status)

            content_type = response.headers.get("Content-Type")  # Accessing headers directly

            if content_type and "application/json" in content_type:
                return await response.json()
            else:
                # If the content type is not application/json, raise an exception
                raise aiohttp.ContentTypeError(
                    request_info=response.request_info,
                    history=response.history,
                    message=f"Unsupported content type: {content_type}"
                )
    except Exception as e:
        import traceback
        # Correctly format and log the traceback
        log_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        print(log_message)
        #_logger.error("Failed to process HTTP request: " + log_message)
        
