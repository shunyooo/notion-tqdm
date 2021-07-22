import threading
from time import sleep, time

import pytest
from notion_tqdm import Status, notion_tqdm

WAIT_SEC = 10

@pytest.fixture(autouse=True, scope='function')
def set_config(pytestconfig):
    notion_tqdm.set_config(
        pytestconfig.getoption("token_v2"),
        pytestconfig.getoption("table_url"),
        email=pytestconfig.getoption("notion_email"),
        timezone="Asia/Tokyo"
        )


def test_run_not_wait_api_in_loop():
    total = 100
    with notion_tqdm(total=total, desc='pytest') as pbar:
        st_time = time()
        for i in range(total):
            sleep(0.01)
        assert time() - st_time < 2


def test_run():
    total = 10
    with notion_tqdm(total=total, desc='pytest') as pbar:
        for i in range(total):
            pbar.update()  
            if i == 8:
                pbar.row.status == Status.doing
            sleep(1)
    sleep(WAIT_SEC)
    assert pbar.row.value == total
    assert pbar.row.status == Status.done
    pbar.row.remove()


def test_error():
    total = 3
    try:
        with notion_tqdm(total=total, desc='pytest') as pbar:
            raise
    except:
        pass
    sleep(WAIT_SEC)
    assert pbar.row.status == Status.error
    pbar.row.remove()


def test_set_props():
    total = 3
    notion_tqdm.set_common_props(test_common='test_common_value')
    with notion_tqdm(total=total, desc='pytest') as pbar:
        for i in range(total):
            sleep(0.5)
            pbar.update_props(test_custom='test_custom_value')
    sleep(WAIT_SEC)
    assert pbar.row.test_common == 'test_common_value'
    assert pbar.row.test_custom == 'test_custom_value'
    pbar.row.remove()
