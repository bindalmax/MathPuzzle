import unittest
import sys
import os

def run_suite(suite_path):
    loader = unittest.TestLoader()
    suite = loader.discover(suite_path)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result

def main():
    base_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
    else:
        target = 'all'

    results = {}
    overall = {
        'testsRun': 0,
        'failures': 0,
        'errors': 0,
        'skipped': 0,
        'expectedFailures': 0,
        'unexpectedSuccesses': 0
    }

    def run_and_store(name, path):
        print(f"\n--- Running {name.upper()} Tests ---")
        res = run_suite(path)
        results[name] = res
        if res is None:
            return
        overall['testsRun'] += getattr(res, 'testsRun', 0)
        overall['failures'] += len(getattr(res, 'failures', []))
        overall['errors'] += len(getattr(res, 'errors', []))
        overall['skipped'] += len(getattr(res, 'skipped', []))
        overall['expectedFailures'] += len(getattr(res, 'expectedFailures', []))
        overall['unexpectedSuccesses'] += len(getattr(res, 'unexpectedSuccesses', []))

    if target in ['unit', 'all']:
        run_and_store('unit', os.path.join(base_dir, 'unit'))

    if target in ['integration', 'all']:
        run_and_store('integration', os.path.join(base_dir, 'integration'))

    if target in ['e2e', 'all']:
        run_and_store('e2e', os.path.join(base_dir, 'e2e'))

    # Per-category summary
    print("\n=== TEST SUMMARY ===")
    for name in ['unit', 'integration', 'e2e']:
        res = results.get(name)
        if res is None:
            print(f"{name.upper()}: No tests found or not run")
            continue
        print(f"{name.upper()}: run={res.testsRun} failures={len(res.failures)} errors={len(res.errors)} skipped={len(res.skipped)}")

    print('\nOverall: testsRun={testsRun} failures={failures} errors={errors} skipped={skipped} expectedFailures={expectedFailures} unexpectedSuccesses={unexpectedSuccesses}'.format(**overall))

    if overall['failures'] > 0 or overall['errors'] > 0 or overall['unexpectedSuccesses'] > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
