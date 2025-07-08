#!/bin/bash

# TDD & Security Code Analysis Shell Script
# Enhanced version with additional features

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default values
DEFAULT_MODEL="deepseek-coder:6.7b"
DEFAULT_FRAMEWORK="pytest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"

# Function to print colored output
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print header
print_header() {
    echo ""
    print_colored "${BOLD}${CYAN}" "============================================="
    print_colored "${BOLD}${CYAN}" "  TDD & Security Code Analysis Tool"
    print_colored "${BOLD}${CYAN}" "============================================="
    echo ""
}

# Function to show help
show_help() {
    print_header
    cat << EOF
Usage: $0 [OPTIONS] COMMAND [ARGS]

COMMANDS:
    analyze FILE [--security] [--clean-code]    Analyze a file for issues
    test FILE [--framework FRAMEWORK]           Generate TDD tests for a file
    project DIR                                  Analyze entire project
    interactive                                  Interactive mode with file selection
    batch FILES...                              Analyze multiple files in batch
    watch DIR                                    Watch directory for changes and auto-analyze
    compare FILE1 FILE2                         Compare security analysis of two files
    report [--format json|html|md]              Generate analysis report

OPTIONS:
    --model MODEL           Ollama model to use (default: $DEFAULT_MODEL)
    --framework FRAMEWORK   Test framework (default: $DEFAULT_FRAMEWORK)
    --output FILE           Output file for results
    --severity LEVEL        Filter by severity (LOW|MEDIUM|HIGH|CRITICAL)
    --verbose              Enable verbose output
    --quiet                Suppress non-essential output
    --help                 Show this help message

EXAMPLES:
    $0 analyze src/main.py --security
    $0 test src/utils.py --framework pytest --output tests/test_utils.py
    $0 project ./my-app
    $0 interactive
    $0 batch src/*.py
    $0 watch src/
    $0 compare old_version.py new_version.py
    $0 report --format html --output security_report.html

SUPPORTED LANGUAGES:
    Python (.py), JavaScript (.js), TypeScript (.ts), Java (.java),
    Go (.go), Rust (.rs), C# (.cs), C/C++ (.c, .cpp), PHP (.php),
    Ruby (.rb), Swift (.swift), Kotlin (.kt)

SUPPORTED TEST FRAMEWORKS:
    pytest, unittest, jest, mocha, junit5, testing, nunit, cargo_test
EOF
}

# Function to check dependencies
check_dependencies() {
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v ollama &> /dev/null; then
        missing_deps+=("ollama")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_colored "${RED}" "❌ Missing dependencies: ${missing_deps[*]}"
        print_colored "${YELLOW}" "Please install the missing dependencies and try again."
        exit 1
    fi
    
    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_colored "${YELLOW}" "⚠️  Ollama server is not running. Starting..."
        ollama serve &
        sleep 5
        if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
            print_colored "${RED}" "❌ Failed to start Ollama server"
            exit 1
        fi
    fi
    
    # Check if required files exist
    if [ ! -f "$SRC_DIR/cli.py" ]; then
        print_colored "${RED}" "❌ CLI script not found: $SRC_DIR/cli.py"
        exit 1
    fi
}

# Function to validate file exists
validate_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        print_colored "${RED}" "❌ File not found: $file"
        exit 1
    fi
}

# Function to validate directory exists
validate_directory() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        print_colored "${RED}" "❌ Directory not found: $dir"
        exit 1
    fi
}

# Function to get supported file extensions
get_supported_extensions() {
    echo "py js ts java go rs cs c cpp php rb swift kt"
}

# Function to check if file is supported
is_supported_file() {
    local file="$1"
    local ext="${file##*.}"
    local supported_extensions=($(get_supported_extensions))
    
    for supported_ext in "${supported_extensions[@]}"; do
        if [ "$ext" = "$supported_ext" ]; then
            return 0
        fi
    done
    return 1
}

# Function to analyze a single file
analyze_file() {
    local file="$1"
    local security_flag="$2"
    local clean_code_flag="$3"
    local model="$4"
    
    validate_file "$file"
    
    if ! is_supported_file "$file"; then
        print_colored "${YELLOW}" "⚠️  File type may not be fully supported: $file"
    fi
    
    print_colored "${BLUE}" "🔍 Analyzing $file..."
    
    local cmd="python3 $SRC_DIR/cli.py analyze --file \"$file\" --model \"$model\""
    
    if [ "$security_flag" = "true" ]; then
        cmd="$cmd --security"
    fi
    
    if [ "$clean_code_flag" = "true" ]; then
        cmd="$cmd --clean-code"
    fi
    
    eval "$cmd"
}

# Function to generate tests
generate_tests() {
    local file="$1"
    local framework="$2"
    local output="$3"
    local model="$4"
    
    validate_file "$file"
    
    print_colored "${BLUE}" "🧪 Generating TDD tests for $file..."
    
    local cmd="python3 $SRC_DIR/cli.py test --file \"$file\" --framework \"$framework\" --model \"$model\""
    
    if [ -n "$output" ]; then
        cmd="$cmd --output \"$output\""
        print_colored "${GREEN}" "✅ Tests will be saved to: $output"
    fi
    
    eval "$cmd"
}

# Function to analyze entire project
analyze_project() {
    local project_dir="$1"
    local model="$2"
    
    validate_directory "$project_dir"
    
    print_colored "${BLUE}" "🔍 Analyzing project: $project_dir..."
    python3 "$SRC_DIR/cli.py" project --project "$project_dir" --model "$model"
}

# Function for interactive mode
interactive_mode() {
    print_header
    
    while true; do
        echo ""
        print_colored "${CYAN}" "Select an option:"
        echo "1. Analyze a file"
        echo "2. Generate tests"
        echo "3. Analyze project"
        echo "4. List supported file types"
        echo "5. Exit"
        echo ""
        
        read -p "Enter your choice (1-5): " choice
        
        case $choice in
            1)
                read -p "Enter file path: " file_path
                if [ -f "$file_path" ]; then
                    analyze_file "$file_path" "true" "true" "$DEFAULT_MODEL"
                else
                    print_colored "${RED}" "❌ File not found: $file_path"
                fi
                ;;
            2)
                read -p "Enter file path: " file_path
                if [ -f "$file_path" ]; then
                    read -p "Enter test framework (default: pytest): " framework
                    framework=${framework:-pytest}
                    generate_tests "$file_path" "$framework" "" "$DEFAULT_MODEL"
                else
                    print_colored "${RED}" "❌ File not found: $file_path"
                fi
                ;;
            3)
                read -p "Enter project directory: " project_dir
                if [ -d "$project_dir" ]; then
                    analyze_project "$project_dir" "$DEFAULT_MODEL"
                else
                    print_colored "${RED}" "❌ Directory not found: $project_dir"
                fi
                ;;
            4)
                print_colored "${CYAN}" "Supported file types:"
                for ext in $(get_supported_extensions); do
                    echo "  - .$ext"
                done
                ;;
            5)
                print_colored "${GREEN}" "👋 Goodbye!"
                exit 0
                ;;
            *)
                print_colored "${RED}" "❌ Invalid choice. Please try again."
                ;;
        esac
    done
}

# Function to batch analyze files
batch_analyze() {
    local files=("$@")
    local model="$DEFAULT_MODEL"
    local total_files=${#files[@]}
    local processed=0
    
    print_colored "${BLUE}" "📦 Batch analyzing $total_files files..."
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            processed=$((processed + 1))
            print_colored "${CYAN}" "[$processed/$total_files] Processing: $file"
            analyze_file "$file" "true" "true" "$model"
            echo ""
        else
            print_colored "${YELLOW}" "⚠️  Skipping non-existent file: $file"
        fi
    done
    
    print_colored "${GREEN}" "✅ Batch analysis complete! Processed $processed files."
}

# Function to watch directory for changes
watch_directory() {
    local dir="$1"
    local model="$2"
    
    validate_directory "$dir"
    
    if ! command -v fswatch &> /dev/null; then
        print_colored "${YELLOW}" "⚠️  fswatch not found. Installing..."
        if command -v brew &> /dev/null; then
            brew install fswatch
        else
            print_colored "${RED}" "❌ Please install fswatch manually"
            exit 1
        fi
    fi
    
    print_colored "${BLUE}" "👁️  Watching directory: $dir"
    print_colored "${YELLOW}" "Press Ctrl+C to stop watching"
    
    fswatch -o "$dir" | while read num; do
        print_colored "${CYAN}" "🔄 Changes detected, analyzing..."
        analyze_project "$dir" "$model"
    done
}

# Function to compare two files
compare_files() {
    local file1="$1"
    local file2="$2"
    local model="$3"
    
    validate_file "$file1"
    validate_file "$file2"
    
    print_colored "${BLUE}" "🔍 Comparing security analysis of:"
    print_colored "${CYAN}" "  File 1: $file1"
    print_colored "${CYAN}" "  File 2: $file2"
    
    echo ""
    print_colored "${BOLD}" "=== ANALYSIS OF FILE 1 ==="
    analyze_file "$file1" "true" "false" "$model"
    
    echo ""
    print_colored "${BOLD}" "=== ANALYSIS OF FILE 2 ==="
    analyze_file "$file2" "true" "false" "$model"
}

# Function to generate reports
generate_report() {
    local format="$1"
    local output="$2"
    local project_dir="${3:-.}"
    
    print_colored "${BLUE}" "📊 Generating $format report..."
    
    # This would be extended to generate different report formats
    case "$format" in
        "json")
            print_colored "${YELLOW}" "JSON report generation not yet implemented"
            ;;
        "html")
            print_colored "${YELLOW}" "HTML report generation not yet implemented"
            ;;
        "md")
            print_colored "${YELLOW}" "Markdown report generation not yet implemented"
            ;;
        *)
            print_colored "${RED}" "❌ Unsupported format: $format"
            exit 1
            ;;
    esac
}

# Main function
main() {
    local command=""
    local model="$DEFAULT_MODEL"
    local framework="$DEFAULT_FRAMEWORK"
    local output=""
    local security_flag="false"
    local clean_code_flag="false"
    local verbose="false"
    local quiet="false"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --model)
                model="$2"
                shift 2
                ;;
            --framework)
                framework="$2"
                shift 2
                ;;
            --output)
                output="$2"
                shift 2
                ;;
            --security)
                security_flag="true"
                shift
                ;;
            --clean-code)
                clean_code_flag="true"
                shift
                ;;
            --verbose)
                verbose="true"
                shift
                ;;
            --quiet)
                quiet="true"
                shift
                ;;
            analyze|test|project|interactive|batch|watch|compare|report)
                command="$1"
                shift
                break
                ;;
            *)
                print_colored "${RED}" "❌ Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Show header unless in quiet mode
    if [ "$quiet" != "true" ]; then
        print_header
    fi
    
    # Check dependencies
    check_dependencies
    
    # Set default flags for analyze command
    if [ "$command" = "analyze" ] && [ "$security_flag" = "false" ] && [ "$clean_code_flag" = "false" ]; then
        security_flag="true"
        clean_code_flag="true"
    fi
    
    # Execute command
    case "$command" in
        "analyze")
            if [ $# -eq 0 ]; then
                print_colored "${RED}" "❌ File path required for analyze command"
                exit 1
            fi
            analyze_file "$1" "$security_flag" "$clean_code_flag" "$model"
            ;;
        "test")
            if [ $# -eq 0 ]; then
                print_colored "${RED}" "❌ File path required for test command"
                exit 1
            fi
            generate_tests "$1" "$framework" "$output" "$model"
            ;;
        "project")
            if [ $# -eq 0 ]; then
                print_colored "${RED}" "❌ Project directory required for project command"
                exit 1
            fi
            analyze_project "$1" "$model"
            ;;
        "interactive")
            interactive_mode
            ;;
        "batch")
            if [ $# -eq 0 ]; then
                print_colored "${RED}" "❌ File paths required for batch command"
                exit 1
            fi
            batch_analyze "$@"
            ;;
        "watch")
            if [ $# -eq 0 ]; then
                print_colored "${RED}" "❌ Directory path required for watch command"
                exit 1
            fi
            watch_directory "$1" "$model"
            ;;
        "compare")
            if [ $# -lt 2 ]; then
                print_colored "${RED}" "❌ Two file paths required for compare command"
                exit 1
            fi
            compare_files "$1" "$2" "$model"
            ;;
        "report")
            local format="md"
            if [ $# -gt 0 ]; then
                format="$1"
            fi
            generate_report "$format" "$output" "."
            ;;
        "")
            print_colored "${YELLOW}" "⚠️  No command specified. Use --help for usage information."
            interactive_mode
            ;;
        *)
            print_colored "${RED}" "❌ Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
