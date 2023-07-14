import unittest
from test import test_header

# Create a test suite
def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(test_header.HeaderTest))
    test_suite.addTest(unittest.makeSuite(test_header.HeaderTestDecode))
    return test_suite

# Run the tests
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
