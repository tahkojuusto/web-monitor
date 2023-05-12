# Web monitor
## Julius Eerola

## Overview

Poll a set of websites periodically, check their statuses, and write the results into a log file.

Settings are read from a JSON config file `config.json` at the root level. The variable `checking_period_seconds` defines the frequency of the polling, `log_filename` the name of the output log file.

The objects in the array `websites` contain the sites to be polled. The variable `url` is self-evident while `content` defines the expected substring found from the response body.

## Technical implementation

The Python 3.11 implementation is based on producer-consumer problem (multiple producers creating website reports, one consumer writing the log file).

Asynchronous programming library (asyncio) is used for optimising performance. It suits well to slow, non-blocking I/O, in our case, HTTP requests and log writing. Multithreading would have added unnecessary complexity while providing few benefits.

A queue is used for loosely decoupling the polling and the writing parts. This way, both parts can scale out independently, and error handling and recovery is easier.

This implementation is not thread-safe, i.e., you can't run it in multiple threads. In order
to do that, you'd need to add necessary mutex around critical sections (queue and log file)
or use thread-safe data structures.

Pydantic library is used to define domain objects. It's good for enforcing we pass validated data within the app.

## Dependencies
- Python 3.11
- Pydantic
    - domain data mode
- Asyncio
    - async programming model
- Aiofiles
    - async file operations
- Aiohttp
    - async HTTP requests

## How to install
```bash
virtualenv venv -p python3.11
source venv/bin/activate
pip install -r requirements.txt
```

## How to run
```bash
python src/main.py
```

## Future work

- unit tests
- thread-safe implementation

