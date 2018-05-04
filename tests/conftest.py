import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "/../")

from evodoc import create_app
from pytest import fixture

@fixture
def app():
    test_settings = {
        'TEST': True,
        'SQLALCHEMY_TRACK_MODIFICATIONS': True,
        'SQLALCHEMY_DATABASE_URI': "sqlite:////tmp/test.db"
    }

    return create_app(test_settings)

