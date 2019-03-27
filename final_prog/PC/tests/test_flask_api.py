import unittest
from flask_api import FlowSegmentColorView

class TestFlaskApi(unittest.TestCase):

    def test_format_to_rgb(self):
        hex = "ff0000"
        assert FlowSegmentColorView.format_to_rgb(hex) == {'b': 0, 'g': 0, 'r': 1.0}