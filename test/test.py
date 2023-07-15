import unittest
from test import test_header
from test import test_stega

# Create a test suite
def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(test_header.HeaderTest))
    test_suite.addTest(unittest.makeSuite(test_header.HeaderTestDecode))
    test_suite.addTest(unittest.makeSuite(test_stega.StegaTest))
    return test_suite

# Run the tests
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
