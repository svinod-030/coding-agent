#!/usr/bin/env python3
"""
CLI interface for TDD & Security Coding Agent
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

from coding_agent import CodingAgent, ReviewType

def print_colored(text: str, color: str = "white"):
    """Print colored text to terminal"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m", 
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def print_security_review(review):
    """Print security review results"""
    print_colored(f"\n🔒 Security Review for {review.file_path}", "bold")
    print_colored(f"Overall Severity: {review.severity}", 
                 "red" if review.severity in ["HIGH", "CRITICAL"] else "yellow")
    print_colored(f"Confidence: {review.confidence:.0%}", "cyan")
    
    if review.issues:
        print_colored("\n📋 Issues Found:", "bold")
        for i, issue in enumerate(review.issues, 1):
            severity_color = {
                "CRITICAL": "red",
                "HIGH": "red", 
                "MEDIUM": "yellow",
                "LOW": "green"
            }.get(issue.get("severity", "LOW"), "white")
            
            print_colored(f"\n{i}. {issue.get('type', 'Unknown')}", "bold")
            print_colored(f"   Severity: {issue.get('severity', 'LOW')}", severity_color)
            if 'line' in issue:
                print_colored(f"   Line: {issue['line']}", "cyan")
            print_colored(f"   Description: {issue.get('description', 'No description')}", "white")
            
            if 'mitigation' in issue:
                print_colored(f"   💡 Mitigation: {issue['mitigation']}", "green")
            
            if 'secure_example' in issue:
                print_colored(f"   ✅ Secure Example:", "green")
                print_colored(f"   {issue['secure_example']}", "white")
    else:
        print_colored("✅ No security issues found!", "green")

def print_clean_code_review(review):
    """Print clean code review results"""
    print_colored(f"\n🧹 Clean Code Review for {review.file_path}", "bold")
    print_colored(f"Confidence: {review.confidence:.0%}", "cyan")
    
    if review.suggestions:
        print_colored("\n📝 Suggestions:", "bold")
        for suggestion in review.suggestions:
            if suggestion.strip():  # Skip empty lines
                print_colored(f"• {suggestion.strip()}", "white")
    else:
        print_colored("✅ Code follows clean code principles!", "green")

def analyze_file_command(args):
    """Handle file analysis command"""
    agent = CodingAgent(args.model)
    
    if not os.path.exists(args.file):
        print_colored(f"❌ File not found: {args.file}", "red")
        return 1
    
    print_colored(f"🔍 Analyzing {args.file}...", "blue")
    results = agent.analyze_file(args.file)
    
    if "error" in results:
        print_colored(f"❌ Error: {results['error']}", "red")
        return 1
    
    # Print security review
    if "security" in results and args.security:
        print_security_review(results["security"])
    
    # Print clean code review  
    if "clean_code" in results and args.clean_code:
        print_clean_code_review(results["clean_code"])
    
    return 0

def generate_tests_command(args):
    """Handle test generation command"""
    agent = CodingAgent(args.model)
    
    if not os.path.exists(args.file):
        print_colored(f"❌ File not found: {args.file}", "red")
        return 1
    
    print_colored(f"🧪 Generating TDD tests for {args.file}...", "blue")
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print_colored(f"❌ Error reading file: {str(e)}", "red")
        return 1
    
    tests = agent.generate_tdd_tests(args.file, code, args.framework)
    
    if args.output:
        # Save to file
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(tests)
            print_colored(f"✅ Tests saved to {args.output}", "green")
        except Exception as e:
            print_colored(f"❌ Error saving tests: {str(e)}", "red")
            return 1
    else:
        # Print to console
        print_colored("\n📝 Generated Tests:", "bold")
        print_colored("=" * 50, "cyan")
        print(tests)
        print_colored("=" * 50, "cyan")
    
    return 0

def analyze_project_command(args):
    """Handle project analysis command"""
    agent = CodingAgent(args.model)
    
    if not os.path.exists(args.project):
        print_colored(f"❌ Project directory not found: {args.project}", "red")
        return 1
    
    print_colored(f"🔍 Analyzing project: {args.project}...", "blue")
    
    # Find all code files
    code_files = []
    extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.cs', '.php', '.rb', '.swift', '.kt']
    
    for root, dirs, files in os.walk(args.project):
        # Skip common directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                code_files.append(os.path.join(root, file))
    
    if not code_files:
        print_colored("❌ No code files found in project", "red")
        return 1
    
    print_colored(f"📁 Found {len(code_files)} code files", "cyan")
    
    total_issues = 0
    critical_files = []
    
    for file_path in code_files:
        print_colored(f"\n🔍 Analyzing {file_path}...", "blue")
        results = agent.analyze_file(file_path)
        
        if "error" in results:
            print_colored(f"⚠️  Error: {results['error']}", "yellow")
            continue
        
        # Count security issues
        if "security" in results:
            issues = results["security"].issues
            if issues:
                total_issues += len(issues)
                severity = results["security"].severity
                if severity in ["HIGH", "CRITICAL"]:
                    critical_files.append((file_path, severity, len(issues)))
                
                print_colored(f"   🔒 Security: {severity} ({len(issues)} issues)", 
                             "red" if severity in ["HIGH", "CRITICAL"] else "yellow")
            else:
                print_colored("   🔒 Security: ✅ Clean", "green")
    
    # Summary
    print_colored(f"\n📊 Analysis Summary", "bold")
    print_colored(f"Total files analyzed: {len(code_files)}", "cyan")
    print_colored(f"Total security issues: {total_issues}", 
                 "red" if total_issues > 0 else "green")
    
    if critical_files:
        print_colored(f"\n⚠️  Critical Files (HIGH/CRITICAL severity):", "red")
        for file_path, severity, issue_count in critical_files:
            print_colored(f"   • {file_path}: {severity} ({issue_count} issues)", "red")
    
    return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="TDD & Security Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single file for security issues
  python cli.py analyze --file main.py --security
  
  # Analyze for both security and clean code
  python cli.py analyze --file main.py --security --clean-code
  
  # Generate TDD tests
  python cli.py test --file main.py --framework pytest --output test_main.py
  
  # Analyze entire project
  python cli.py project --project ./my-app
        """
    )
    
    parser.add_argument("--model", default="deepseek-coder:6.7b", 
                       help="Ollama model to use (default: deepseek-coder:6.7b)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze file command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single file")
    analyze_parser.add_argument("--file", required=True, help="File to analyze")
    analyze_parser.add_argument("--security", action="store_true", 
                               help="Perform security review")
    analyze_parser.add_argument("--clean-code", action="store_true",
                               help="Perform clean code review")
    
    # Generate tests command  
    test_parser = subparsers.add_parser("test", help="Generate TDD tests")
    test_parser.add_argument("--file", required=True, help="File to generate tests for")
    test_parser.add_argument("--framework", default="pytest", 
                            choices=["pytest", "unittest", "jest", "mocha", "junit5", "testing", "nunit", "cargo_test"],
                            help="Test framework to use")
    test_parser.add_argument("--output", help="Output file for generated tests")
    
    # Analyze project command
    project_parser = subparsers.add_parser("project", help="Analyze entire project")
    project_parser.add_argument("--project", required=True, help="Project directory to analyze")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Set default flags for analyze command
    if args.command == "analyze" and not args.security and not args.clean_code:
        args.security = True
        args.clean_code = True
    
    try:
        if args.command == "analyze":
            return analyze_file_command(args)
        elif args.command == "test":
            return generate_tests_command(args)
        elif args.command == "project":
            return analyze_project_command(args)
    except KeyboardInterrupt:
        print_colored("\n❌ Operation cancelled by user", "red")
        return 1
    except Exception as e:
        print_colored(f"❌ Unexpected error: {str(e)}", "red")
        return 1

if __name__ == "__main__":
    sys.exit(main())
