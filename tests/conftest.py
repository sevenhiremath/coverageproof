import pytest
from coverageproof.domain import Scope
from coverageproof.store import Store

@pytest.fixture
def scope():
    return Scope(name='owned fixture',networks=('127.0.0.1/32',),ports=(8765,8766),authorization_reference='Self-owned unit-test fixture only')

@pytest.fixture
def store(tmp_path):
    return Store(tmp_path/'test.sqlite')
