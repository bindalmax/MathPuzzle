#!/usr/bin/env python
"""
Comprehensive Test Verification Script
Tests all components: console game, web app, and leaderboard enhancements
"""

import sys
import unittest
import os

def run_all_tests():
    """Run all test suites and report results"""

    print("="*80)
    print("MATHPUZZLE - COMPREHENSIVE TEST SUITE")
    print("="*80)

    # Create test loader
    loader = unittest.TestLoader()

    # Create main test suite
    main_suite = unittest.TestSuite()

    # Load all tests
    try:
        # Load test modules
        from test_math_game import (
            TestHighscoreManager,
            TestQuestionFactory,
            TestBasicArithmeticQuestion,
            TestDecimalFractionQuestion,
            TestPercentageQuestion,
            TestAlgebraQuestion,
            TestProfitLossQuestion,
            TestGame
        )
        from test_app import TestWebApp

        print("\n✓ Successfully imported all test classes\n")

        # Add test cases
        test_classes = [
            TestHighscoreManager,
            TestQuestionFactory,
            TestBasicArithmeticQuestion,
            TestDecimalFractionQuestion,
            TestPercentageQuestion,
            TestAlgebraQuestion,
            TestProfitLossQuestion,
            TestGame,
            TestWebApp
        ]

        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            main_suite.addTests(tests)
            print(f"✓ Loaded {tests.countTestCases()} tests from {test_class.__name__}")

        print("\n" + "-"*80)
        print("RUNNING TESTS")
        print("-"*80 + "\n")

        # Run with detailed output
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(main_suite)

        # Print summary
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        print(f"Total Tests Run:  {result.testsRun}")
        print(f"Successes:        {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Failures:         {len(result.failures)}")
        print(f"Errors:           {len(result.errors)}")
        print(f"Skipped:          {len(result.skipped)}")
        print("-"*80)

        if result.wasSuccessful():
            print("✅ ALL TESTS PASSED!")
            print("="*80)
            return 0
        else:
            print("❌ SOME TESTS FAILED!")
            if result.failures:
                print("\nFailures:")
                for test, traceback in result.failures:
                    print(f"\n{test}:\n{traceback}")
            if result.errors:
                print("\nErrors:")
                for test, traceback in result.errors:
                    print(f"\n{test}:\n{traceback}")
            print("="*80)
            return 1

    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)

