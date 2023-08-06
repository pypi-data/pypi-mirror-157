# pylint: skip-file
import asyncio

import pytest


@pytest.fixture(scope='session')
def base_url() -> str:
    return "https://cbra.localhost"


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.new_event_loop()