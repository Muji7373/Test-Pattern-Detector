#!/usr/bin/env python3
"""
Sample Test Data Generator
===========================
Generates sample JUnit XML test results for demonstration.
"""

import random
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os


def generate_test_result(test_name, pass_probability, run_number, duration_base=1.0):
    """Generate a single test case result."""
    testcase = ET.Element('testcase')
    testcase.set('classname', f'com.optisol.tests.{test_name.split("_")[0]}')
    testcase.set('name', test_name)
    testcase.set('time', str(duration_base + random.uniform(-0.5, 0.5)))

    # Determine if test passes based on probability
    if random.random() > pass_probability:
        failure = ET.SubElement(testcase, 'failure')
        failure.set('message', random.choice([
            'AssertionError: Expected 200 but got 500',
            'TimeoutException: Request timed out after 30s',
            'NullPointerException: Object reference not set',
            'ConnectionRefusedError: Unable to connect to database',
            'ValidationError: Invalid input data',
            'ResourceNotFoundError: File not found'
        ]))

    return testcase


def generate_test_suite(run_number, total_runs):
    """Generate a complete test suite."""
    testsuite = ET.Element('testsuite')
    testsuite.set('name', f'TestRun_{run_number}')
    testsuite.set('tests', '20')
    testsuite.set('timestamp', (datetime.now() - timedelta(hours=total_runs - run_number)).isoformat())

    # Define test scenarios
    tests = [
        # Stable tests (100% pass rate)
        ('test_user_login', 1.0, 0.5),
        ('test_home_page_load', 1.0, 0.3),
        ('test_static_content', 1.0, 0.2),
        ('test_health_check', 1.0, 0.1),

        # Flaky tests (intermittent failures)
        ('test_api_integration', 0.6, 1.2),  # 40% failure
        ('test_database_connection', 0.7, 0.8),  # 30% failure
        ('test_cache_invalidation', 0.5, 1.5),  # 50% failure
        ('test_concurrent_users', 0.65, 2.0),  # 35% failure

        # Mostly stable (occasional failures)
        ('test_file_upload', 0.95, 1.0),  # 5% failure
        ('test_email_notification', 0.97, 0.9),  # 3% failure

        # Failing tests (100% failure)
        ('test_broken_feature', 0.0, 0.5),
        ('test_deprecated_api', 0.0, 0.7),

        # Mostly failing
        ('test_unstable_service', 0.1, 1.3),  # 90% failure
        ('test_memory_leak', 0.05, 2.5),  # 95% failure

        # Additional variety
        ('test_authentication', 0.85, 0.6),
        ('test_authorization', 0.75, 0.8),
        ('test_data_validation', 0.9, 0.4),
        ('test_error_handling', 0.8, 0.7),
        ('test_performance', 0.55, 3.0),
        ('test_load_balancer', 0.7, 1.1)
    ]

    for test_name, pass_prob, duration in tests:
        testcase = generate_test_result(test_name, pass_prob, run_number, duration)
        testsuite.append(testcase)

    # Update counts
    failures = len([tc for tc in testsuite.findall('testcase') if tc.find('failure') is not None])
    testsuite.set('failures', str(failures))
    testsuite.set('errors', '0')
    testsuite.set('skipped', '0')

    return testsuite


def generate_sample_data(num_runs=15, output_dir='sample_data'):
    """Generate multiple test run results."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating {num_runs} sample test runs...")

    for i in range(1, num_runs + 1):
        root = ET.Element('testsuites')
        testsuite = generate_test_suite(i, num_runs)
        root.append(testsuite)

        tree = ET.ElementTree(root)
        ET.indent(tree, space='  ')

        filename = f'{output_dir}/test_results_run_{i:02d}.xml'
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        print(f"  ✓ Generated: {filename}")

    print(f"\n✅ Sample data generation complete!")
    print(f"📁 Files saved in: {output_dir}/")
    print(f"\n🚀 Run analysis with:")
    print(f"   python detector.py --input {output_dir}/*.xml")


if __name__ == "__main__":
    generate_sample_data(num_runs=15)