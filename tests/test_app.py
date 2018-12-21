from app import APP
import pytest
from flask import url_for

@pytest.fixture
def app():
    return APP

def test_app(app):
    assert app is not None


def test_list_profiles(client):
    assert client.get(url_for('profile.get_list')).status_code == 200
