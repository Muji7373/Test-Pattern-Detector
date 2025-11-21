#!/usr/bin/env python3
"""
Test Pattern Detector - Interactive Tool
=========================================
Easy-to-use menu interface for test pattern detection.

Author: Muji - Optisol Business Solutions
"""

import os
import sys
import glob
from pathlib import Path


# Color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_banner():
    """Print welcome banner."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           🔍 TEST PATTERN DETECTION TOOL                             ║
║              Easy Mode - Just Follow the Steps!                      ║
║                                                                      ║
║              Developed by: Muji                                      ║
║              Optisol Business Solutions                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)


def print_section(title):
    """Print section header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}{Colors.END}\n")


def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")


def show_main_menu():
    """Display main menu."""
    print_section("MAIN MENU")

    menu = f"""
{Colors.BOLD}Choose what you want to do:{Colors.END}

{Colors.GREEN}1.{Colors.END} 🎯 Quick Start with Demo Data (Recommended for first time!)
{Colors.GREEN}2.{Colors.END} 🔍 Analyze My Test Results
{Colors.GREEN}3.{Colors.END} ⚙️  Configure Settings
{Colors.GREEN}4.{Colors.END} 📊 View Last Analysis Results
{Colors.GREEN}5.{Colors.END} 📚 Help & Documentation
{Colors.GREEN}6.{Colors.END} 🚪 Exit

"""
    print(menu)
    choice = input(f"{Colors.CYAN}Enter your choice (1-6): {Colors.END}").strip()
    return choice


def quick_start_demo():
    """Run quick demo with sample data."""
    print_section("QUICK START DEMO")

    print_info("This will generate sample test data and run analysis.")
    print_info("Perfect for learning how the tool works!\n")

    confirm = input(f"{Colors.YELLOW}Continue? (y/n): {Colors.END}").strip().lower()

    if confirm != 'y':
        print_warning("Demo cancelled.")
        return

    print("\n" + Colors.BOLD + "Step 1: Generating sample test data..." + Colors.END)
    ret = os.system('python3 generate_sample_data.py')

    if ret != 0:
        print_error("Failed to generate sample data!")
        return

    print("\n" + Colors.BOLD + "Step 2: Running analysis..." + Colors.END)
    ret = os.system('python3 detector.py --input sample_data/*.xml')

    if ret != 0:
        print_error("Analysis failed!")
        return

    print("\n" + Colors.BOLD + "Step 3: Opening dashboard..." + Colors.END)

    # Try to open dashboard based on OS
    dashboard_path = "output/dashboard.html"
    if sys.platform == "darwin":  # macOS
        os.system(f'open {dashboard_path}')
    elif sys.platform == "linux":
        os.system(f'xdg-open {dashboard_path}')
    elif sys.platform == "win32":
        os.system(f'start {dashboard_path}')

    print_success("Demo complete! Dashboard should open in your browser.")
    print_info(f"You can also open it manually: {dashboard_path}")

    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")


def analyze_my_tests():
    """Guide user through analyzing their test results."""
    print_section("ANALYZE YOUR TEST RESULTS")

    print_info("I'll help you find and analyze your test results.\n")

    # Step 1: Ask about test framework
    print(f"{Colors.BOLD}Step 1: What testing framework do you use?{Colors.END}\n")
    print("1. Java (Maven/Gradle/JUnit/TestNG)")
    print("2. Python (pytest/unittest)")
    print("3. JavaScript (Jest/Mocha)")
    print("4. C# (.NET/NUnit/xUnit)")
    print("5. Other / I have XML files ready")
    print("6. I don't know / Help me find them\n")

    framework = input(f"{Colors.CYAN}Enter choice (1-6): {Colors.END}").strip()

    # Provide hints based on framework
    hints = {
        '1': "Java test results are usually in:\n  - Maven: target/surefire-reports/*.xml\n  - Gradle: build/test-results/test/*.xml",
        '2': "Python test results (if using JUnit XML):\n  - pytest: test-results/*.xml (if you used --junitxml)\n  - unittest: test-results.xml",
        '3': "JavaScript test results:\n  - Jest: test-results/*.xml (if configured)\n  - Mocha: test-results/*.xml",
        '4': "C# test results:\n  - Usually in: TestResults/*.xml\n  - Or: build/test-results/*.xml",
        '5': "Great! Your XML files should be in JUnit format.",
        '6': "No problem! Common locations:\n  - target/surefire-reports/\n  - build/test-results/\n  - test-results/"
    }

    if framework in hints:
        print(f"\n{Colors.YELLOW}{hints[framework]}{Colors.END}\n")

    # Step 2: Get file path
    print(f"\n{Colors.BOLD}Step 2: Where are your test result files?{Colors.END}\n")
    print("Options:")
    print("1. Enter full path to directory (e.g., /path/to/test-results)")
    print("2. Enter file pattern (e.g., target/surefire-reports/*.xml)")
    print("3. Search for XML files in current directory\n")

    option = input(f"{Colors.CYAN}Choose option (1-3): {Colors.END}").strip()

    file_pattern = None

    if option == '1':
        dir_path = input(f"{Colors.CYAN}Enter directory path: {Colors.END}").strip()
        file_pattern = os.path.join(dir_path, "*.xml")
    elif option == '2':
        file_pattern = input(f"{Colors.CYAN}Enter file pattern: {Colors.END}").strip()
    elif option == '3':
        print_info("Searching for XML files...")
        xml_files = glob.glob("**/*.xml", recursive=True)
        if xml_files:
            print(f"\n{Colors.GREEN}Found {len(xml_files)} XML files:{Colors.END}")
            for i, f in enumerate(xml_files[:10], 1):
                print(f"  {i}. {f}")
            if len(xml_files) > 10:
                print(f"  ... and {len(xml_files) - 10} more")

            use_all = input(f"\n{Colors.CYAN}Use all these files? (y/n): {Colors.END}").strip().lower()
            if use_all == 'y':
                file_pattern = "**/*.xml"
            else:
                file_pattern = input(f"{Colors.CYAN}Enter specific pattern: {Colors.END}").strip()
        else:
            print_error("No XML files found in current directory.")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return

    # Verify files exist
    if file_pattern:
        files = glob.glob(file_pattern, recursive=True)
        if not files:
            print_error(f"No files found matching: {file_pattern}")
            print_info("Make sure the path is correct and files exist.")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return

        print_success(f"Found {len(files)} test result file(s)")

        # Show first few files
        print(f"\n{Colors.BOLD}Files to analyze:{Colors.END}")
        for f in files[:5]:
            print(f"  • {f}")
        if len(files) > 5:
            print(f"  • ... and {len(files) - 5} more files")

    # Step 3: Configure options
    print(f"\n{Colors.BOLD}Step 3: Analysis Options{Colors.END}\n")
    print("1. Quick analysis (min 5 runs)")
    print("2. Accurate analysis (min 10 runs)")
    print("3. High confidence (min 15 runs)")
    print("4. Custom settings\n")

    analysis_option = input(f"{Colors.CYAN}Choose option (1-4): {Colors.END}").strip()

    min_runs_map = {'1': 5, '2': 10, '3': 15}
    min_runs = min_runs_map.get(analysis_option, 5)

    if analysis_option == '4':
        min_runs = input(f"{Colors.CYAN}Enter minimum runs needed: {Colors.END}").strip()
        try:
            min_runs = int(min_runs)
        except:
            print_warning("Invalid number, using default: 5")
            min_runs = 5

    # Step 4: Run analysis
    print(f"\n{Colors.BOLD}Step 4: Running Analysis...{Colors.END}\n")
    print_info("This may take a few seconds...")

    cmd = f'python3 detector.py --input "{file_pattern}" --min-runs {min_runs}'
    print(f"\n{Colors.YELLOW}Command: {cmd}{Colors.END}\n")

    ret = os.system(cmd)

    if ret == 0:
        print_success("\nAnalysis completed successfully!")

        # Try to open dashboard
        dashboard_path = "output/dashboard.html"
        open_dash = input(f"\n{Colors.CYAN}Open dashboard in browser? (y/n): {Colors.END}").strip().lower()

        if open_dash == 'y':
            if sys.platform == "darwin":
                os.system(f'open {dashboard_path}')
            elif sys.platform == "linux":
                os.system(f'xdg-open {dashboard_path}')
            elif sys.platform == "win32":
                os.system(f'start {dashboard_path}')

            print_success("Dashboard opened!")

        print(f"\n{Colors.GREEN}Your reports are saved in:{Colors.END}")
        print(f"  • Dashboard: output/dashboard.html")
        print(f"  • CSV Report: output/pattern_report.csv")
        print(f"  • JSON Data: output/insights.json")
    else:
        print_error("Analysis failed! Check the error messages above.")

    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")


def configure_settings():
    """Configure tool settings."""
    print_section("CONFIGURE SETTINGS")

    config_file = "config.yaml"

    if not os.path.exists(config_file):
        print_error("Config file not found!")
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        return

    print_info("Current configuration:\n")

    # Read and display current config
    with open(config_file, 'r') as f:
        content = f.read()
        print(content)

    print(f"\n{Colors.BOLD}What do you want to change?{Colors.END}\n")
    print("1. Minimum runs required")
    print("2. Flaky threshold (min %)")
    print("3. Flaky threshold (max %)")
    print("4. Output directory")
    print("5. Nothing, go back\n")

    choice = input(f"{Colors.CYAN}Enter choice (1-5): {Colors.END}").strip()

    if choice == '5':
        return

    # Read current config
    import yaml
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except:
        print_warning("Could not load YAML config, will use simple editing")
        print_info("Edit config.yaml manually for now")
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        return

    # Update based on choice
    if choice == '1':
        new_value = input(f"{Colors.CYAN}Enter new minimum runs (current: {config['min_runs']}): {Colors.END}").strip()
        try:
            config['min_runs'] = int(new_value)
            print_success(f"Updated minimum runs to {new_value}")
        except:
            print_error("Invalid number!")

    elif choice == '2':
        new_value = input(
            f"{Colors.CYAN}Enter new flaky threshold min % (current: {config['flaky_threshold_min']}): {Colors.END}").strip()
        try:
            config['flaky_threshold_min'] = int(new_value)
            print_success(f"Updated flaky threshold min to {new_value}%")
        except:
            print_error("Invalid number!")

    elif choice == '3':
        new_value = input(
            f"{Colors.CYAN}Enter new flaky threshold max % (current: {config['flaky_threshold_max']}): {Colors.END}").strip()
        try:
            config['flaky_threshold_max'] = int(new_value)
            print_success(f"Updated flaky threshold max to {new_value}%")
        except:
            print_error("Invalid number!")

    elif choice == '4':
        new_value = input(
            f"{Colors.CYAN}Enter new output directory (current: {config['output_directory']}): {Colors.END}").strip()
        config['output_directory'] = new_value
        print_success(f"Updated output directory to {new_value}")

    # Save config
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        print_success("Configuration saved!")
    except:
        print_error("Could not save config file!")

    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")


def view_last_results():
    """View last analysis results."""
    print_section("VIEW LAST RESULTS")

    output_dir = "output"
    dashboard = os.path.join(output_dir, "dashboard.html")
    csv_report = os.path.join(output_dir, "pattern_report.csv")
    json_report = os.path.join(output_dir, "insights.json")

    if not os.path.exists(output_dir):
        print_warning("No results found! Run an analysis first.")
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        return

    print(f"{Colors.BOLD}Available results:{Colors.END}\n")

    files_found = []

    if os.path.exists(dashboard):
        print_success(f"Dashboard: {dashboard}")
        files_found.append(('dashboard', dashboard))

    if os.path.exists(csv_report):
        print_success(f"CSV Report: {csv_report}")
        files_found.append(('csv', csv_report))

    if os.path.exists(json_report):
        print_success(f"JSON Report: {json_report}")
        files_found.append(('json', json_report))

    if not files_found:
        print_warning("No result files found!")
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        return

    print(f"\n{Colors.BOLD}What do you want to open?{Colors.END}\n")
    print("1. Dashboard (browser)")
    print("2. CSV Report")
    print("3. JSON Report")
    print("4. Show summary")
    print("5. Go back\n")

    choice = input(f"{Colors.CYAN}Enter choice (1-5): {Colors.END}").strip()

    if choice == '1' and os.path.exists(dashboard):
        if sys.platform == "darwin":
            os.system(f'open {dashboard}')
        elif sys.platform == "linux":
            os.system(f'xdg-open {dashboard}')
        elif sys.platform == "win32":
            os.system(f'start {dashboard}')
        print_success("Opening dashboard...")

    elif choice == '2' and os.path.exists(csv_report):
        if sys.platform == "darwin":
            os.system(f'open {csv_report}')
        elif sys.platform == "linux":
            os.system(f'xdg-open {csv_report}')
        elif sys.platform == "win32":
            os.system(f'start {csv_report}')
        print_success("Opening CSV report...")

    elif choice == '3' and os.path.exists(json_report):
        print("\n" + Colors.BOLD + "JSON Report Contents:" + Colors.END + "\n")
        with open(json_report, 'r') as f:
            print(f.read())

    elif choice == '4' and os.path.exists(json_report):
        import json
        with open(json_report, 'r') as f:
            data = json.load(f)

        stats = data.get('statistics', {})
        print(f"\n{Colors.BOLD}Analysis Summary:{Colors.END}\n")
        print(f"  Total Tests:           {stats.get('total_tests', 0)}")
        print(f"  ✅ Stable Tests:       {stats.get('stable_tests', 0)}")
        print(f"  ⚠️  Flaky Tests:        {stats.get('flaky_tests', 0)}")
        print(f"  ❌ Failing Tests:      {stats.get('failing_tests', 0)}")

        total = stats.get('total_tests', 0)
        if total > 0:
            healthy = stats.get('stable_tests', 0) + stats.get('mostly_stable', 0)
            health_score = (healthy / total) * 100
            print(f"\n  🏥 Health Score:       {health_score:.1f}%")

    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")


def show_help():
    """Show help and documentation."""
    print_section("HELP & DOCUMENTATION")

    help_text = f"""
{Colors.BOLD}Quick Start Guide:{Colors.END}

1. {Colors.GREEN}First Time?{Colors.END}
   → Choose option 1 (Demo) to see how it works

2. {Colors.GREEN}Have Test Results?{Colors.END}
   → Choose option 2 (Analyze)
   → I'll help you find and analyze them

3. {Colors.GREEN}Want to Customize?{Colors.END}
   → Choose option 3 (Configure)
   → Change thresholds and settings

{Colors.BOLD}Supported Test Frameworks:{Colors.END}
  • Java: JUnit, TestNG, Maven, Gradle
  • Python: pytest (--junitxml), unittest
  • JavaScript: Jest, Mocha (with JUnit reporter)
  • C#: NUnit, xUnit, .NET Test
  • Any framework that outputs JUnit XML!

{Colors.BOLD}What You Need:{Colors.END}
  • Python 3.7 or higher (check: python3 --version)
  • Test result files in JUnit XML format
  • At least 5 test runs for accurate detection

{Colors.BOLD}Output Files:{Colors.END}
  • dashboard.html  → Beautiful web dashboard
  • pattern_report.csv → Excel/Sheets data
  • insights.json → API/automation data

{Colors.BOLD}Documentation Files:{Colors.END}
  • START_HERE.md → Quick orientation
  • QUICKSTART.md → 3-minute setup
  • README.md → Complete user guide
  • METHODOLOGY.md → How it works

{Colors.BOLD}Need More Help?{Colors.END}
  • Read the documentation files above
  • Check test_pattern_detector.log for errors
  • Contact: Muji - DevSecOps Team

"""
    print(help_text)
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")


def main():
    """Main program loop."""
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')  # Clear screen

        print_banner()

        choice = show_main_menu()

        if choice == '1':
            quick_start_demo()
        elif choice == '2':
            analyze_my_tests()
        elif choice == '3':
            configure_settings()
        elif choice == '4':
            view_last_results()
        elif choice == '5':
            show_help()
        elif choice == '6':
            print(f"\n{Colors.GREEN}Thanks for using Test Pattern Detector! 🚀{Colors.END}\n")
            sys.exit(0)
        else:
            print_error("Invalid choice! Please enter 1-6.")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Exiting... Goodbye! 👋{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)