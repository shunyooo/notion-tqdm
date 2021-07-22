import pytest


def pytest_addoption(parser):
    parser.addoption("--token_v2", action="store", required=True)
    parser.addoption("--table_url", action="store", required=True)
    parser.addoption("--notion_email", action="store", required=True)
