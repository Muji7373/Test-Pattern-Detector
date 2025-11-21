#!/usr/bin/env python3
"""
Enhanced Sample Test Data Generator
====================================
Generates 100+ realistic test scenarios with various patterns.
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
            'ResourceNotFoundError: File not found',
            'PermissionError: Access denied',
            'NetworkError: Connection lost',
            'OutOfMemoryError: Heap space exhausted',
            'ConcurrencyError: Deadlock detected',
            'DataIntegrityError: Constraint violation',
            'AuthenticationError: Invalid credentials'
        ]))

    return testcase


def generate_comprehensive_test_suite(run_number, total_runs):
    """Generate a comprehensive test suite with 100+ tests."""
    testsuite = ET.Element('testsuite')
    testsuite.set('name', f'ComprehensiveTestRun_{run_number}')
    testsuite.set('tests', '120')
    testsuite.set('timestamp', (datetime.now() - timedelta(hours=total_runs - run_number)).isoformat())

    # Define 100+ test scenarios with diverse patterns
    tests = []

    # === STABLE TESTS (20 tests - 0% failure) ===
    stable_tests = [
        ('test_health_check', 1.0, 0.1),
        ('test_version_info', 1.0, 0.1),
        ('test_configuration_load', 1.0, 0.2),
        ('test_static_resources', 1.0, 0.2),
        ('test_basic_routing', 1.0, 0.3),
        ('test_session_creation', 1.0, 0.4),
        ('test_cookie_handling', 1.0, 0.3),
        ('test_cors_headers', 1.0, 0.2),
        ('test_content_type', 1.0, 0.2),
        ('test_user_profile_view', 1.0, 0.5),
        ('test_list_operations', 1.0, 0.4),
        ('test_string_validation', 1.0, 0.2),
        ('test_number_formatting', 1.0, 0.2),
        ('test_date_parsing', 1.0, 0.3),
        ('test_json_serialization', 1.0, 0.3),
        ('test_xml_parsing', 1.0, 0.4),
        ('test_base64_encoding', 1.0, 0.2),
        ('test_hash_generation', 1.0, 0.3),
        ('test_uuid_creation', 1.0, 0.1),
        ('test_enum_validation', 1.0, 0.2),
    ]

    # === MOSTLY STABLE (15 tests - 1-4% failure) ===
    mostly_stable = [
        ('test_email_notification', 0.98, 0.9),
        ('test_sms_delivery', 0.97, 1.0),
        ('test_file_upload', 0.97, 1.2),
        ('test_image_resize', 0.96, 1.5),
        ('test_pdf_generation', 0.96, 2.0),
        ('test_excel_export', 0.97, 1.8),
        ('test_csv_import', 0.98, 1.0),
        ('test_zip_compression', 0.97, 1.3),
        ('test_log_rotation', 0.98, 0.5),
        ('test_backup_restore', 0.96, 2.5),
        ('test_data_migration', 0.97, 2.0),
        ('test_index_rebuild', 0.96, 1.8),
        ('test_cache_warmup', 0.97, 1.2),
        ('test_report_generation', 0.98, 1.5),
        ('test_analytics_query', 0.97, 1.0),
    ]

    # === FLAKY TESTS - LOW (20 tests - 10-30% failure) ===
    flaky_low = [
        ('test_api_authentication', 0.85, 0.8),
        ('test_token_refresh', 0.80, 0.7),
        ('test_oauth_callback', 0.82, 1.0),
        ('test_sso_integration', 0.78, 1.2),
        ('test_ldap_connection', 0.75, 1.5),
        ('test_saml_validation', 0.80, 1.3),
        ('test_jwt_verification', 0.85, 0.6),
        ('test_api_rate_limiting', 0.78, 0.8),
        ('test_webhook_delivery', 0.80, 1.0),
        ('test_message_queue', 0.82, 0.9),
        ('test_async_processing', 0.75, 1.5),
        ('test_batch_jobs', 0.78, 2.0),
        ('test_scheduled_tasks', 0.80, 1.2),
        ('test_event_streaming', 0.82, 1.1),
        ('test_real_time_updates', 0.75, 1.0),
        ('test_websocket_connection', 0.80, 0.9),
        ('test_grpc_communication', 0.78, 1.0),
        ('test_graphql_queries', 0.82, 0.8),
        ('test_rest_pagination', 0.85, 0.7),
        ('test_api_versioning', 0.80, 0.6),
    ]

    # === FLAKY TESTS - MEDIUM (20 tests - 30-50% failure) ===
    flaky_medium = [
        ('test_database_transaction', 0.60, 1.2),
        ('test_cache_invalidation', 0.55, 1.0),
        ('test_redis_connection', 0.58, 0.9),
        ('test_mongodb_query', 0.52, 1.3),
        ('test_elasticsearch_search', 0.60, 1.5),
        ('test_kafka_consumer', 0.55, 1.2),
        ('test_rabbitmq_publisher', 0.58, 1.1),
        ('test_s3_file_upload', 0.52, 2.0),
        ('test_cdn_distribution', 0.60, 1.8),
        ('test_load_balancer', 0.55, 1.0),
        ('test_circuit_breaker', 0.58, 0.8),
        ('test_retry_mechanism', 0.52, 1.2),
        ('test_fallback_handler', 0.60, 0.9),
        ('test_service_discovery', 0.55, 1.0),
        ('test_health_monitoring', 0.58, 0.7),
        ('test_metric_collection', 0.52, 0.8),
        ('test_distributed_tracing', 0.60, 1.1),
        ('test_log_aggregation', 0.55, 1.0),
        ('test_alert_notification', 0.58, 0.9),
        ('test_incident_response', 0.52, 1.2),
    ]

    # === FLAKY TESTS - HIGH (15 tests - 50-70% failure) ===
    flaky_high = [
        ('test_concurrent_users', 0.40, 2.0),
        ('test_stress_load', 0.35, 3.0),
        ('test_spike_traffic', 0.38, 2.5),
        ('test_endurance_run', 0.42, 4.0),
        ('test_memory_pressure', 0.35, 2.8),
        ('test_cpu_intensive', 0.40, 3.2),
        ('test_io_bottleneck', 0.38, 2.6),
        ('test_network_latency', 0.42, 2.0),
        ('test_packet_loss', 0.35, 2.2),
        ('test_bandwidth_limit', 0.40, 2.4),
        ('test_connection_pool', 0.38, 1.8),
        ('test_thread_contention', 0.42, 2.1),
        ('test_race_condition', 0.35, 1.5),
        ('test_deadlock_scenario', 0.40, 2.0),
        ('test_resource_leak', 0.38, 2.3),
    ]

    # === MOSTLY FAILING (15 tests - 85-95% failure) ===
    mostly_failing = [
        ('test_legacy_integration', 0.10, 1.5),
        ('test_deprecated_endpoint', 0.08, 1.2),
        ('test_unstable_service', 0.12, 1.8),
        ('test_third_party_api', 0.10, 2.0),
        ('test_external_dependency', 0.08, 1.7),
        ('test_flaky_microservice', 0.12, 1.6),
        ('test_unreliable_network', 0.10, 1.9),
        ('test_intermittent_error', 0.08, 1.4),
        ('test_random_timeout', 0.12, 2.2),
        ('test_unstable_database', 0.10, 1.8),
        ('test_corrupted_cache', 0.08, 1.5),
        ('test_broken_pipeline', 0.12, 2.0),
        ('test_failing_webhook', 0.10, 1.7),
        ('test_incomplete_migration', 0.08, 2.1),
        ('test_partial_deployment', 0.12, 1.9),
    ]

    # === CONSISTENTLY FAILING (15 tests - 100% failure) ===
    consistently_failing = [
        ('test_broken_feature', 0.0, 0.8),
        ('test_missing_dependency', 0.0, 0.6),
        ('test_config_error', 0.0, 0.5),
        ('test_permission_denied', 0.0, 0.7),
        ('test_invalid_credentials', 0.0, 0.6),
        ('test_database_down', 0.0, 1.0),
        ('test_service_unavailable', 0.0, 0.9),
        ('test_endpoint_not_found', 0.0, 0.4),
        ('test_method_not_allowed', 0.0, 0.5),
        ('test_unsupported_format', 0.0, 0.6),
        ('test_schema_mismatch', 0.0, 0.7),
        ('test_version_conflict', 0.0, 0.8),
        ('test_incompatible_library', 0.0, 0.9),
        ('test_runtime_exception', 0.0, 0.5),
        ('test_fatal_error', 0.0, 0.6),
    ]

    # Combine all test categories
    tests.extend(stable_tests)
    tests.extend(mostly_stable)
    tests.extend(flaky_low)
    tests.extend(flaky_medium)
    tests.extend(flaky_high)
    tests.extend(mostly_failing)
    tests.extend(consistently_failing)

    # Generate test cases
    for test_name, pass_prob, duration in tests:
        testcase = generate_test_result(test_name, pass_prob, run_number, duration)
        testsuite.append(testcase)

    # Update counts
    failures = len([tc for tc in testsuite.findall('testcase') if tc.find('failure') is not None])
    testsuite.set('failures', str(failures))
    testsuite.set('errors', '0')
    testsuite.set('skipped', '0')
    testsuite.set('tests', str(len(tests)))

    return testsuite


def generate_large_sample_data(num_runs=20, output_dir='sample_data'):
    """Generate comprehensive test data with 100+ tests."""
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("  COMPREHENSIVE SAMPLE DATA GENERATOR")
    print("  Creating 100+ test scenarios across multiple runs")
    print("=" * 70)
    print()
    print(f"Generating {num_runs} test runs with 120 tests each...")
    print()

    for i in range(1, num_runs + 1):
        root = ET.Element('testsuites')
        testsuite = generate_comprehensive_test_suite(i, num_runs)
        root.append(testsuite)

        tree = ET.ElementTree(root)
        ET.indent(tree, space='  ')

        filename = f'{output_dir}/test_results_run_{i:02d}.xml'
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        # Get test counts
        total = int(testsuite.get('tests', 0))
        failures = int(testsuite.get('failures', 0))
        passed = total - failures

        print(f"  ✓ Run {i:02d}: {passed} passed, {failures} failed → {filename}")

    print()
    print("=" * 70)
    print("  GENERATION COMPLETE!")
    print("=" * 70)
    print()
    print(f"📊 Statistics:")
    print(f"   • Total Runs: {num_runs}")
    print(f"   • Tests per Run: 120")
    print(f"   • Total Test Executions: {num_runs * 120}")
    print()
    print(f"📁 Files saved in: {output_dir}/")
    print()
    print("🎯 Test Distribution:")
    print("   • 20 Stable tests (0% failure)")
    print("   • 15 Mostly Stable (1-4% failure)")
    print("   • 20 Flaky Low (10-30% failure)")
    print("   • 20 Flaky Medium (30-50% failure)")
    print("   • 15 Flaky High (50-70% failure)")
    print("   • 15 Mostly Failing (85-95% failure)")
    print("   • 15 Consistently Failing (100% failure)")
    print()
    print("🚀 Run analysis with:")
    print(f"   python3 detector.py --input {output_dir}/*.xml")
    print()


if __name__ == "__main__":
    import sys

    # Allow custom number of runs
    num_runs = 20
    if len(sys.argv) > 1:
        try:
            num_runs = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of runs. Using default: {num_runs}")

    generate_large_sample_data(num_runs=num_runs)