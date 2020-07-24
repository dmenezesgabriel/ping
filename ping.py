import aiohttp
import asyncio
import logging
import signal


logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
logging_format += "%(message)s"

logging.basicConfig(
    format=logging_format,
    level=logging.INFO
)

_logger = logging.getLogger()
URL = 'your_url'
REQUEST_TIMEOUT = 5
INTERVAL = 5
_running = False
_tasks = []


async def fetch(session, url, timeout=REQUEST_TIMEOUT, max_tries=3):
    """
    Make a get request on endpoint
    Parameters
    ----------
    :session: aiohttp.ClientSession()
    :url: endpoint https://www.example.com
    :timeout: timeout in seconds
    Returns
    ----------
    request's response in json format
    """
    attempt_no = 0
    while attempt_no < max_tries:
        attempt_no += 1
        _logger.info('Fetching %s, attempt no %s', url, attempt_no)
        try:
            async with session.get(url, timeout=timeout) as response:
                return response.status
        except Exception as error:
            _logger.error('Error on fetching %s, attempt no %s. Error: %s',
                          url, attempt_no, error)
            await asyncio.sleep(0.01)


async def ping(url):
    """
    Sends a request to a endpoint in a established interval
    ----------
    :url: endpoint https://www.example.com
    """
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        while _running:
            response = await fetch(session, URL)
            _logger.info('Sending ping')
            _logger.info('Response: %s', response)
            await asyncio.sleep(INTERVAL)


async def init():
    _logger.info('Initializing ping')
    """
    Sets ping state to running
    """
    global _running
    _running = True


async def start():
    global task
    _logger.info('Starting ping')
    """
    Starts ping
    """
    await init()
    _tasks.append(await asyncio.ensure_future(ping(URL)))


def stop():
    _logger.info('Stopping ping')
    """
    Stops ping execution
    """
    global _running, _tasks
    _running = False
    for task in _tasks:
        if task.done():
            continue
        task.cancel()
    _logger.info('Hearbeat stopped')


def main():
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, stop)
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == '__main__':
    main()
