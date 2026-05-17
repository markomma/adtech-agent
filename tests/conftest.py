from pathlib import Path
import pytest
from adtech_crosswalk.loader import Loader

@pytest.fixture(scope="session")
def loader():
    return Loader()

@pytest.fixture
def small_taxonomy():
    return {
        "entries": [
            {"id": "1", "name": "Beer", "full_path": "Alcohol > Beer"},
            {"id": "2", "name": "Wine", "full_path": "Alcohol > Wine"},
            {"id": "3", "name": "Spirits", "full_path": "Alcohol > Spirits"},
        ]
    }

@pytest.fixture
def small_index():
    return {
        "corpus_size": 3,
        "avgdl": 2.0,
        "idf": {"beer": 1.4, "alcohol": 0.3, "wine": 1.4, "spirits": 1.4},
        "inverted": {
            "beer": ["1"],
            "alcohol": ["1", "2", "3"],
            "wine": ["2"],
            "spirits": ["3"],
        },
        "documents": {
            "1": {"name": "Beer", "full_path": "Alcohol > Beer", "tokens": ["beer", "alcohol"], "dl": 2},
            "2": {"name": "Wine", "full_path": "Alcohol > Wine", "tokens": ["wine", "alcohol"], "dl": 2},
            "3": {"name": "Spirits", "full_path": "Alcohol > Spirits", "tokens": ["spirits", "alcohol"], "dl": 2},
        },
    }
