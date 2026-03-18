import unittest
import test_math_game
import test_app

# Load tests from test modules
suite = unittest.TestSuite()
loader = unittest.TestLoader()
suite.addTests(loader.loadTestsFromModule(test_math_game))
suite.addTests(loader.loadTestsFromModule(test_app))

# Run the tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if not result.wasSuccessful():
    exit(1)
