import pytest

import html2kirby


@pytest.fixture
def formatter():
    yield html2kirby.HTML2Kirby()
