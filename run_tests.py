import unittest
import sys
import os

def run_suite(suite_path):
    loader = unittest.TestLoader()
    suite = loader.discover(suite_path)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def main():
    base_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
    else:
        target = 'all'

    success = True

    if target in ['unit', 'all']:
        print("\n--- Running UNIT Tests ---")
        success &= run_suite(os.path.join(base_dir, 'unit'))

    if target in ['integration', 'all']:
        print("\n--- Running INTEGRATION Tests ---")
        success &= run_suite(os.path.join(base_dir, 'integration'))

    if target in ['e2e', 'all']:
        print("\n--- Running E2E Tests ---")
        success &= run_suite(os.path.join(base_dir, 'e2e'))

    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
