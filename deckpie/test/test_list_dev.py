from unittest import TestCase


# noinspection PyPep8Naming
class TestList_dev(TestCase):
    def test_list_dev(self):
        from deckpie.main import list_dev
        devices = list_dev(False)
        assert devices[0] == b'cDAQ1'
