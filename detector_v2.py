#!/usr/bin/env python3
"""
Failed Test Pattern Detection Tool - ENHANCED VERSION
======================================================
Professional automation tool for detecting flaky and failing test patterns.
NOW WITH: Pagination, Search, Filtering, and Sorting in HTML Dashboard!

Author: Muji - Optisol Business Solutions
Enhanced by: Claude (Muji's request)
Version: 2.0.0 - Professional Paginated Dashboard
"""

import xml.etree.ElementTree as ET
import json
import csv
import os
import sys
import argparse
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import statistics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_pattern_detector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TestResult:
    """Represents a single test execution result."""

    def __init__(self, name: str, status: str, error_message: str = "",
                 duration: float = 0.0, timestamp: str = ""):
        self.name = name
        self.status = status  # 'passed', 'failed', 'skipped'
        self.error_message = error_message
        self.duration = duration
        self.timestamp = timestamp or datetime.now().isoformat()

    def __repr__(self):
        return f"TestResult({self.name}, {self.status})"


class TestPattern:
    """Analyzes and classifies test execution patterns."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.executions = []
        self.total_runs = 0
        self.pass_count = 0
        self.fail_count = 0
        self.skip_count = 0
        self.failure_rate = 0.0
        self.classification = "Unknown"
        self.confidence_score = 0.0
        self.error_patterns = []
        self.avg_duration = 0.0

    def add_execution(self, result: TestResult):
        """Add a test execution result."""
        self.executions.append(result)
        self.total_runs += 1

        if result.status == 'passed':
            self.pass_count += 1
        elif result.status == 'failed':
            self.fail_count += 1
            if result.error_message:
                self.error_patterns.append(result.error_message)
        else:
            self.skip_count += 1

    def analyze(self, min_runs: int = 5, flaky_threshold: Tuple[float, float] = (5, 95)):
        """Analyze the test pattern and classify it."""
        if self.total_runs < min_runs:
            self.classification = "Insufficient Data"
            self.confidence_score = 0.0
            return

        # Calculate failure rate
        self.failure_rate = (self.fail_count / self.total_runs) * 100

        # Calculate average duration
        durations = [e.duration for e in self.executions if e.duration > 0]
        self.avg_duration = statistics.mean(durations) if durations else 0.0

        # Classify based on failure rate
        min_flaky, max_flaky = flaky_threshold

        if self.failure_rate == 0:
            self.classification = "Stable"
            self.confidence_score = 100.0
        elif self.failure_rate == 100:
            self.classification = "Consistently Failing"
            self.confidence_score = 100.0
        elif min_flaky <= self.failure_rate <= max_flaky:
            self.classification = "Flaky"
            # Confidence decreases as failure rate approaches 50% (maximum uncertainty)
            self.confidence_score = 100 - abs(50 - self.failure_rate)
        elif self.failure_rate < min_flaky:
            self.classification = "Mostly Stable"
            self.confidence_score = 90.0
        else:
            self.classification = "Mostly Failing"
            self.confidence_score = 90.0

        # Adjust confidence based on sample size
        sample_confidence = min(100, (self.total_runs / 20) * 100)
        self.confidence_score = (self.confidence_score + sample_confidence) / 2

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        return {
            'test_name': self.test_name,
            'total_runs': self.total_runs,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'skip_count': self.skip_count,
            'failure_rate': round(self.failure_rate, 2),
            'classification': self.classification,
            'confidence_score': round(self.confidence_score, 2),
            'avg_duration': round(self.avg_duration, 3),
            'error_pattern_count': len(set(self.error_patterns))
        }


class TestPatternDetector:
    """Main detection engine for test patterns."""

    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.test_patterns = defaultdict(lambda: TestPattern(""))
        self.output_dir = Path(self.config['output_directory'])
        self.output_dir.mkdir(exist_ok=True)
        logger.info("Test Pattern Detector initialized")

    def _default_config(self) -> Dict:
        """Default configuration."""
        return {
            'min_runs': 5,
            'flaky_threshold_min': 5,
            'flaky_threshold_max': 95,
            'output_directory': 'output',
            'generate_html': True,
            'generate_csv': True,
            'generate_json': True
        }

    def parse_junit_xml(self, xml_file: str) -> List[TestResult]:
        """Parse JUnit XML format test results."""
        results = []

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Handle both <testsuites> and <testsuite> root elements
            if root.tag == 'testsuites':
                testsuites = root.findall('testsuite')
            else:
                testsuites = [root]

            for testsuite in testsuites:
                for testcase in testsuite.findall('testcase'):
                    name = f"{testcase.get('classname', '')}.{testcase.get('name', '')}"
                    duration = float(testcase.get('time', 0))

                    # Determine status
                    failure = testcase.find('failure')
                    error = testcase.find('error')
                    skipped = testcase.find('skipped')

                    if failure is not None:
                        status = 'failed'
                        error_msg = failure.get('message', '') or failure.text or ''
                    elif error is not None:
                        status = 'failed'
                        error_msg = error.get('message', '') or error.text or ''
                    elif skipped is not None:
                        status = 'skipped'
                        error_msg = ''
                    else:
                        status = 'passed'
                        error_msg = ''

                    results.append(TestResult(name, status, error_msg, duration))

            logger.info(f"Parsed {len(results)} test results from {xml_file}")
            return results

        except Exception as e:
            logger.error(f"Error parsing XML file {xml_file}: {str(e)}")
            return []

    def parse_multiple_files(self, file_paths: List[str]):
        """Parse multiple test result files."""
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue

            results = self.parse_junit_xml(file_path)

            for result in results:
                if result.name not in self.test_patterns:
                    self.test_patterns[result.name] = TestPattern(result.name)

                self.test_patterns[result.name].add_execution(result)

        logger.info(f"Processed {len(self.test_patterns)} unique tests")

    def analyze_patterns(self):
        """Analyze all test patterns."""
        min_runs = self.config['min_runs']
        flaky_threshold = (
            self.config['flaky_threshold_min'],
            self.config['flaky_threshold_max']
        )

        for pattern in self.test_patterns.values():
            pattern.analyze(min_runs, flaky_threshold)

        logger.info("Pattern analysis complete")

    def get_statistics(self) -> Dict:
        """Get overall statistics."""
        total_tests = len(self.test_patterns)
        classifications = defaultdict(int)

        for pattern in self.test_patterns.values():
            classifications[pattern.classification] += 1

        return {
            'total_tests': total_tests,
            'stable_tests': classifications['Stable'],
            'flaky_tests': classifications['Flaky'],
            'failing_tests': classifications['Consistently Failing'],
            'mostly_stable': classifications['Mostly Stable'],
            'mostly_failing': classifications['Mostly Failing'],
            'insufficient_data': classifications['Insufficient Data']
        }

    def generate_csv_report(self):
        """Generate CSV report."""
        csv_path = self.output_dir / 'pattern_report.csv'

        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = [
                'Test Name', 'Failed/Total Runs', 'Pass Count', 'Fail Count',
                'Skip Count', 'Failure Rate (%)', 'Classification',
                'Confidence Score (%)', 'Avg Duration (s)', 'Unique Errors'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Sort by classification priority
            priority = {
                'Consistently Failing': 0,
                'Flaky': 1,
                'Mostly Failing': 2,
                'Mostly Stable': 3,
                'Stable': 4,
                'Insufficient Data': 5
            }

            sorted_patterns = sorted(
                self.test_patterns.values(),
                key=lambda x: (priority.get(x.classification, 99), -x.failure_rate)
            )

            for pattern in sorted_patterns:
                summary = pattern.get_summary()
                writer.writerow({
                    'Test Name': summary['test_name'],
                    'Failed/Total Runs': f"{summary['fail_count']}/{summary['total_runs']}",
                    'Pass Count': summary['pass_count'],
                    'Fail Count': summary['fail_count'],
                    'Skip Count': summary['skip_count'],
                    'Failure Rate (%)': summary['failure_rate'],
                    'Classification': summary['classification'],
                    'Confidence Score (%)': summary['confidence_score'],
                    'Avg Duration (s)': summary['avg_duration'],
                    'Unique Errors': summary['error_pattern_count']
                })

        logger.info(f"CSV report generated: {csv_path}")
        return csv_path

    def generate_json_report(self):
        """Generate JSON report with detailed insights."""
        json_path = self.output_dir / 'insights.json'

        report = {
            'generated_at': datetime.now().isoformat(),
            'configuration': self.config,
            'statistics': self.get_statistics(),
            'test_patterns': []
        }

        for pattern in self.test_patterns.values():
            summary = pattern.get_summary()
            summary['error_samples'] = list(set(pattern.error_patterns[:3]))  # Top 3 unique errors
            report['test_patterns'].append(summary)

        with open(json_path, 'w') as jsonfile:
            json.dump(report, jsonfile, indent=2)

        logger.info(f"JSON report generated: {json_path}")
        return json_path

    def generate_html_dashboard(self):
        """Generate interactive HTML dashboard with pagination and advanced features."""
        html_path = self.output_dir / 'dashboard.html'

        stats = self.get_statistics()

        # Count critical tests for display
        critical_count = len(
            [p for p in self.test_patterns.values() if p.classification in ['Consistently Failing', 'Flaky']])

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Pattern Detection Dashboard v2.0</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        .header .version {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            display: inline-block;
            margin-top: 10px;
            font-weight: 600;
        }}

        .header .timestamp {{
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}

        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stat-card .value {{
            color: #333;
            font-size: 2.5em;
            font-weight: bold;
        }}

        .stat-card.critical {{
            border-left: 5px solid #e74c3c;
        }}

        .stat-card.warning {{
            border-left: 5px solid #f39c12;
        }}

        .stat-card.success {{
            border-left: 5px solid #27ae60;
        }}

        .stat-card.info {{
            border-left: 5px solid #3498db;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}

        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .chart-container h3 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}

        .table-container {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow-x: auto;
            margin-bottom: 30px;
        }}

        .table-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 15px;
        }}

        .table-controls h3 {{
            color: #333;
            font-size: 1.5em;
            margin: 0;
        }}

        .controls-right {{
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .search-box {{
            padding: 12px 20px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            width: 280px;
            transition: all 0.3s ease;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .filter-select {{
            padding: 12px 20px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .filter-select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            transition: background 0.3s ease;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        th:hover {{
            background: linear-gradient(135deg, #5568d3 0%, #65408b 100%);
        }}

        th .sort-icon {{
            font-size: 12px;
            margin-left: 8px;
            opacity: 0.7;
        }}

        td {{
            padding: 14px 16px;
            border-bottom: 1px solid #eee;
            color: #333;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .badge {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            display: inline-block;
        }}

        .badge.critical {{
            background: #fee;
            color: #e74c3c;
        }}

        .badge.warning {{
            background: #fef5e7;
            color: #f39c12;
        }}

        .badge.success {{
            background: #eafaf1;
            color: #27ae60;
        }}

        .badge.info {{
            background: #ebf5fb;
            color: #3498db;
        }}

        .pagination-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 25px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            flex-wrap: wrap;
            gap: 15px;
        }}

        .page-info {{
            color: #666;
            font-size: 14px;
            font-weight: 500;
        }}

        .pagination {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .page-btn {{
            padding: 8px 14px;
            border: 2px solid #ddd;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .page-btn:hover:not(:disabled) {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}

        .page-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}

        .page-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .no-results {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.1em;
        }}

        .footer {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            color: #666;
            margin-top: 30px;
        }}

        .footer strong {{
            color: #333;
        }}

        @media (max-width: 768px) {{
            .table-controls {{
                flex-direction: column;
                align-items: stretch;
            }}

            .controls-right {{
                flex-direction: column;
                width: 100%;
            }}

            .search-box, .filter-select {{
                width: 100%;
            }}

            .pagination-container {{
                flex-direction: column;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Test Pattern Detection Dashboard</h1>
            <div class="subtitle">Automated Flaky & Failed Test Analysis</div>
            <span class="version">v2.0 - Enhanced Edition</span>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card info">
                <div class="label">Total Tests</div>
                <div class="value">{stats['total_tests']}</div>
            </div>
            <div class="stat-card critical">
                <div class="label">Consistently Failing</div>
                <div class="value">{stats['failing_tests']}</div>
            </div>
            <div class="stat-card warning">
                <div class="label">Flaky Tests</div>
                <div class="value">{stats['flaky_tests']}</div>
            </div>
            <div class="stat-card success">
                <div class="label">Stable Tests</div>
                <div class="value">{stats['stable_tests']}</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <h3>Test Classification Distribution</h3>
                <canvas id="distributionChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Health Score Overview</h3>
                <canvas id="healthChart"></canvas>
            </div>
        </div>

        <div class="table-container">
            <div class="table-controls">
                <h3>🚨 Critical Tests Requiring Attention ({critical_count} tests)</h3>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Classification</th>
                        <th>Failure Rate</th>
                        <th>Failed/Total Runs</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
"""

        # Show ALL critical tests
        critical_tests = sorted(
            [p for p in self.test_patterns.values() if p.classification in ['Consistently Failing', 'Flaky']],
            key=lambda x: x.failure_rate,
            reverse=True
        )

        if critical_tests:
            for pattern in critical_tests:
                badge_class = 'critical' if pattern.classification == 'Consistently Failing' else 'warning'
                html_content += f"""
                    <tr>
                        <td title="{pattern.test_name}">{pattern.test_name.split('.')[-1][:60]}</td>
                        <td><span class="badge {badge_class}">{pattern.classification}</span></td>
                        <td>{pattern.failure_rate:.1f}%</td>
                        <td>{pattern.fail_count}/{pattern.total_runs}</td>
                        <td>{pattern.confidence_score:.1f}%</td>
                    </tr>
"""
        else:
            html_content += """
                    <tr>
                        <td colspan="5" class="no-results">🎉 No critical tests found! Your test suite is healthy!</td>
                    </tr>
"""

        html_content += """
                </tbody>
            </table>
        </div>

        <div class="table-container">
            <div class="table-controls">
                <h3>📋 Complete Test List</h3>
                <div class="controls-right">
                    <input type="text" id="searchInput" class="search-box" placeholder="🔍 Search tests...">
                    <select id="filterSelect" class="filter-select">
                        <option value="all">All Classifications</option>
                        <option value="Consistently Failing">Consistently Failing</option>
                        <option value="Flaky">Flaky</option>
                        <option value="Mostly Failing">Mostly Failing</option>
                        <option value="Mostly Stable">Mostly Stable</option>
                        <option value="Stable">Stable</option>
                        <option value="Insufficient Data">Insufficient Data</option>
                    </select>
                    <select id="itemsPerPage" class="filter-select">
                        <option value="10">10 per page</option>
                        <option value="25" selected>25 per page</option>
                        <option value="50">50 per page</option>
                        <option value="100">100 per page</option>
                        <option value="all">Show All</option>
                    </select>
                </div>
            </div>

            <table id="allTestsTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Test Name <span class="sort-icon">⇅</span></th>
                        <th onclick="sortTable(1)">Classification <span class="sort-icon">⇅</span></th>
                        <th onclick="sortTable(2)">Failure Rate <span class="sort-icon">⇅</span></th>
                        <th onclick="sortTable(3)">Failed/Total Runs <span class="sort-icon">⇅</span></th>
                        <th onclick="sortTable(4)">Confidence <span class="sort-icon">⇅</span></th>
                    </tr>
                </thead>
                <tbody id="testTableBody">
"""

        # Add ALL tests sorted by classification and failure rate
        all_tests_sorted = sorted(
            self.test_patterns.values(),
            key=lambda x: (
                {'Consistently Failing': 0, 'Flaky': 1, 'Mostly Failing': 2,
                 'Mostly Stable': 3, 'Stable': 4, 'Insufficient Data': 5}.get(x.classification, 99),
                -x.failure_rate
            )
        )

        for pattern in all_tests_sorted:
            badge_class_map = {
                'Consistently Failing': 'critical',
                'Flaky': 'warning',
                'Mostly Failing': 'warning',
                'Mostly Stable': 'info',
                'Stable': 'success',
                'Insufficient Data': 'info'
            }
            badge_class = badge_class_map.get(pattern.classification, 'info')

            html_content += f"""
                    <tr class="test-row" data-classification="{pattern.classification}" 
                        data-name="{pattern.test_name}" 
                        data-failure-rate="{pattern.failure_rate}"
                        data-fail-count="{pattern.fail_count}"
                        data-confidence="{pattern.confidence_score}">
                        <td title="{pattern.test_name}">{pattern.test_name.split('.')[-1][:60]}</td>
                        <td><span class="badge {badge_class}">{pattern.classification}</span></td>
                        <td>{pattern.failure_rate:.1f}%</td>
                        <td>{pattern.fail_count}/{pattern.total_runs}</td>
                        <td>{pattern.confidence_score:.1f}%</td>
                    </tr>
"""

        html_content += f"""
                </tbody>
            </table>

            <div class="pagination-container">
                <div class="page-info" id="pageInfo"></div>
                <div class="pagination" id="pagination"></div>
            </div>
        </div>

        <div class="footer">
            <p><strong>Test Pattern Detector v2.0 Enhanced</strong> | Optisol Business Solutions</p>
            <p>Original Development: Muji | Enhanced Features: DevSecOps Team</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                ✨ New Features: Pagination • Search • Filtering • Sorting • Professional UI
            </p>
        </div>
    </div>

    <script>
        // ==================== CHARTS ====================

        // Distribution Chart
        const distCtx = document.getElementById('distributionChart').getContext('2d');
        new Chart(distCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Stable', 'Flaky', 'Consistently Failing', 'Mostly Stable', 'Mostly Failing', 'Insufficient Data'],
                datasets: [{{
                    data: [{stats['stable_tests']}, {stats['flaky_tests']}, {stats['failing_tests']}, {stats['mostly_stable']}, {stats['mostly_failing']}, {stats['insufficient_data']}],
                    backgroundColor: ['#27ae60', '#f39c12', '#e74c3c', '#7fb3d5', '#f1948a', '#aeb6bf']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 15,
                            font: {{
                                size: 12
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Health Score Chart
        const healthCtx = document.getElementById('healthChart').getContext('2d');
        const totalTests = {stats['total_tests']};
        const healthyTests = {stats['stable_tests']} + {stats['mostly_stable']};
        const unhealthyTests = {stats['flaky_tests']} + {stats['failing_tests']} + {stats['mostly_failing']};
        const healthScore = totalTests > 0 ? ((healthyTests / totalTests) * 100).toFixed(1) : 0;

        new Chart(healthCtx, {{
            type: 'bar',
            data: {{
                labels: ['Healthy Tests', 'Problematic Tests', 'Health Score %'],
                datasets: [{{
                    label: 'Test Suite Health',
                    data: [healthyTests, unhealthyTests, healthScore],
                    backgroundColor: ['#27ae60', '#e74c3c', '#3498db']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});

        // ==================== PAGINATION & FILTERING ====================

        let currentPage = 1;
        let itemsPerPage = 25;
        let allRows = [];
        let filteredRows = [];
        let currentSort = {{ column: -1, ascending: true }};

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            allRows = Array.from(document.querySelectorAll('#testTableBody .test-row'));
            filteredRows = [...allRows];
            updateDisplay();

            // Event listeners
            document.getElementById('searchInput').addEventListener('input', handleSearch);
            document.getElementById('filterSelect').addEventListener('change', handleFilter);
            document.getElementById('itemsPerPage').addEventListener('change', handleItemsPerPageChange);
        }});

        function handleSearch(e) {{
            const searchTerm = e.target.value.toLowerCase();
            filteredRows = allRows.filter(row => 
                row.dataset.name.toLowerCase().includes(searchTerm)
            );
            currentPage = 1;
            updateDisplay();
        }}

        function handleFilter(e) {{
            const filterValue = e.target.value;
            if (filterValue === 'all') {{
                filteredRows = [...allRows];
            }} else {{
                filteredRows = allRows.filter(row => 
                    row.dataset.classification === filterValue
                );
            }}
            currentPage = 1;
            updateDisplay();
        }}

        function handleItemsPerPageChange(e) {{
            const value = e.target.value;
            itemsPerPage = value === 'all' ? filteredRows.length : parseInt(value);
            currentPage = 1;
            updateDisplay();
        }}

        function sortTable(columnIndex) {{
            const ascending = currentSort.column === columnIndex ? !currentSort.ascending : true;
            currentSort = {{ column: columnIndex, ascending }};

            filteredRows.sort((a, b) => {{
                let aValue, bValue;

                switch(columnIndex) {{
                    case 0: // Test Name
                        aValue = a.dataset.name.toLowerCase();
                        bValue = b.dataset.name.toLowerCase();
                        break;
                    case 1: // Classification
                        aValue = a.dataset.classification;
                        bValue = b.dataset.classification;
                        break;
                    case 2: // Failure Rate
                        aValue = parseFloat(a.dataset.failureRate);
                        bValue = parseFloat(b.dataset.failureRate);
                        break;
                    case 3: // Fail Count
                        aValue = parseInt(a.dataset.failCount);
                        bValue = parseInt(b.dataset.failCount);
                        break;
                    case 4: // Confidence
                        aValue = parseFloat(a.dataset.confidence);
                        bValue = parseFloat(b.dataset.confidence);
                        break;
                }}

                if (aValue < bValue) return ascending ? -1 : 1;
                if (aValue > bValue) return ascending ? 1 : -1;
                return 0;
            }});

            updateDisplay();
        }}

        function updateDisplay() {{
            const start = (currentPage - 1) * itemsPerPage;
            const end = start + itemsPerPage;
            const pageRows = filteredRows.slice(start, end);

            const tbody = document.getElementById('testTableBody');
            tbody.innerHTML = '';

            if (pageRows.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="5" class="no-results">No tests found matching your criteria</td></tr>';
            }} else {{
                pageRows.forEach(row => tbody.appendChild(row.cloneNode(true)));
            }}

            updatePaginationInfo();
            updatePaginationButtons();
        }}

        function updatePaginationInfo() {{
            const start = (currentPage - 1) * itemsPerPage + 1;
            const end = Math.min(start + itemsPerPage - 1, filteredRows.length);
            const total = filteredRows.length;

            document.getElementById('pageInfo').textContent = 
                `Showing ${{start}}-${{end}} of ${{total}} tests`;
        }}

        function updatePaginationButtons() {{
            const totalPages = Math.ceil(filteredRows.length / itemsPerPage);
            const pagination = document.getElementById('pagination');
            pagination.innerHTML = '';

            // Previous button
            const prevBtn = createPageButton('← Prev', currentPage - 1, currentPage === 1);
            pagination.appendChild(prevBtn);

            // Page numbers
            const maxButtons = 7;
            let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
            let endPage = Math.min(totalPages, startPage + maxButtons - 1);

            if (endPage - startPage < maxButtons - 1) {{
                startPage = Math.max(1, endPage - maxButtons + 1);
            }}

            if (startPage > 1) {{
                pagination.appendChild(createPageButton('1', 1, false));
                if (startPage > 2) {{
                    const ellipsis = document.createElement('span');
                    ellipsis.textContent = '...';
                    ellipsis.className = 'page-btn';
                    ellipsis.style.border = 'none';
                    ellipsis.style.cursor = 'default';
                    pagination.appendChild(ellipsis);
                }}
            }}

            for (let i = startPage; i <= endPage; i++) {{
                pagination.appendChild(createPageButton(i, i, false, i === currentPage));
            }}

            if (endPage < totalPages) {{
                if (endPage < totalPages - 1) {{
                    const ellipsis = document.createElement('span');
                    ellipsis.textContent = '...';
                    ellipsis.className = 'page-btn';
                    ellipsis.style.border = 'none';
                    ellipsis.style.cursor = 'default';
                    pagination.appendChild(ellipsis);
                }}
                pagination.appendChild(createPageButton(totalPages, totalPages, false));
            }}

            // Next button
            const nextBtn = createPageButton('Next →', currentPage + 1, currentPage === totalPages);
            pagination.appendChild(nextBtn);
        }}

        function createPageButton(text, page, disabled, active = false) {{
            const btn = document.createElement('button');
            btn.textContent = text;
            btn.className = 'page-btn' + (active ? ' active' : '');
            btn.disabled = disabled;
            if (!disabled) {{
                btn.onclick = () => {{
                    currentPage = page;
                    updateDisplay();
                }};
            }}
            return btn;
        }}
    </script>
</body>
</html>"""

        with open(html_path, 'w') as htmlfile:
            htmlfile.write(html_content)

        logger.info(f"Enhanced HTML dashboard generated: {html_path}")
        return html_path

    def generate_reports(self):
        """Generate all configured reports."""
        reports = {}

        if self.config['generate_csv']:
            reports['csv'] = self.generate_csv_report()

        if self.config['generate_json']:
            reports['json'] = self.generate_json_report()

        if self.config['generate_html']:
            reports['html'] = self.generate_html_dashboard()

        return reports


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Test Pattern Detection Tool v2.0 - Enhanced with Pagination & Advanced Features'
    )
    parser.add_argument(
        '--input',
        nargs='+',
        required=True,
        help='Input test result files (JUnit XML format)'
    )
    parser.add_argument(
        '--min-runs',
        type=int,
        default=5,
        help='Minimum test runs required for classification (default: 5)'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for reports (default: output)'
    )

    args = parser.parse_args()

    # Print banner
    print("=" * 80)
    print("  TEST PATTERN DETECTION TOOL v2.0 - ENHANCED EDITION")
    print("  Automated Flaky & Failed Test Analysis with Advanced Features")
    print("  ✨ New: Pagination | Search | Filtering | Sorting | Professional UI")
    print("  Optisol Business Solutions")
    print("=" * 80)
    print()

    # Configure detector
    config = {
        'min_runs': args.min_runs,
        'flaky_threshold_min': 5,
        'flaky_threshold_max': 95,
        'output_directory': args.output_dir,
        'generate_html': True,
        'generate_csv': True,
        'generate_json': True
    }

    # Initialize detector
    detector = TestPatternDetector(config)

    # Parse test results
    logger.info(f"Processing {len(args.input)} test result file(s)...")
    detector.parse_multiple_files(args.input)

    # Analyze patterns
    logger.info("Analyzing test patterns...")
    detector.analyze_patterns()

    # Get statistics
    stats = detector.get_statistics()

    print("\n" + "=" * 80)
    print("  ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"  Total Tests Analyzed:      {stats['total_tests']}")
    print(f"  ✅ Stable Tests:           {stats['stable_tests']}")
    print(f"  ⚠️  Flaky Tests:            {stats['flaky_tests']}")
    print(f"  ❌ Consistently Failing:   {stats['failing_tests']}")
    print(f"  📊 Mostly Stable:          {stats['mostly_stable']}")
    print(f"  📊 Mostly Failing:         {stats['mostly_failing']}")
    print(f"  ℹ️  Insufficient Data:     {stats['insufficient_data']}")
    print("=" * 80)

    # Generate reports
    logger.info("Generating enhanced reports...")
    reports = detector.generate_reports()

    print("\n" + "=" * 80)
    print("  GENERATED REPORTS")
    print("=" * 80)
    for report_type, report_path in reports.items():
        print(f"  {report_type.upper()}: {report_path}")
    print("=" * 80)

    # Calculate health score
    total = stats['total_tests']
    if total > 0:
        healthy = stats['stable_tests'] + stats['mostly_stable']
        health_score = (healthy / total) * 100

        print(f"\n  🏥 TEST SUITE HEALTH SCORE: {health_score:.1f}%")

        if health_score >= 90:
            print("  ✅ Excellent! Your test suite is very healthy.")
        elif health_score >= 75:
            print("  ⚠️  Good, but some tests need attention.")
        elif health_score >= 50:
            print("  ⚠️  Warning: Multiple problematic tests detected.")
        else:
            print("  ❌ Critical: Test suite needs immediate attention.")

    print("\n  ✨ Analysis complete! Open dashboard.html for interactive experience.")
    print("  🎯 Features: Search, Filter, Sort, and Navigate through all tests!\n")
    logger.info("Test pattern detection completed successfully")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)