import unittest

class TestTemplate(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName=methodName)

    def setUp(self):

        return super().setUp()

    def tearDown(self):

        return self.tearDown()

    def test_datagen(self):
        pass

if __name__ == "__main__":
    unittest.main()