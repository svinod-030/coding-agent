# TDD & Security Coding Agent

A specialized AI coding agent powered by Deepseek Coder and Ollama, focused on **Test-Driven Development (TDD)** and **Security Code Reviews**. This agent helps developers write secure, clean, and well-tested code across multiple programming languages.

## 🚀 Features

### 🔒 Security Reviews
- **OWASP Top 10** vulnerability detection
- **Input validation** analysis
- **Authentication/authorization** flaw detection
- **Cryptographic** issue identification
- **Dependency vulnerability** scanning
- **Language-specific** security patterns

### 🧪 Test-Driven Development (TDD)
- **Automated test generation** following TDD principles
- **Multiple framework support** (pytest, Jest, JUnit, etc.)
- **Arrange-Act-Assert** pattern implementation
- **Edge case** and **error scenario** coverage
- **Mocking strategy** suggestions

### 🧹 Clean Code Reviews
- **SOLID principles** adherence checking
- **Code readability** analysis
- **Function complexity** assessment
- **Naming convention** validation
- **Code duplication** detection
- **Documentation** quality review

## 🛠 Supported Languages & Frameworks

### Languages
- **Python** (.py)
- **JavaScript** (.js)
- **TypeScript** (.ts)
- **Java** (.java)
- **Go** (.go)
- **Rust** (.rs)
- **C#** (.cs)
- **C/C++** (.c, .cpp)
- **PHP** (.php)
- **Ruby** (.rb)
- **Swift** (.swift)
- **Kotlin** (.kt)

### Test Frameworks
- **Python**: pytest, unittest
- **JavaScript**: Jest, Mocha
- **TypeScript**: Jest
- **Java**: JUnit 5
- **Go**: testing
- **Rust**: cargo test
- **C#**: NUnit

## 📦 Installation

### Prerequisites
1. **Ollama** installed and running
2. **Python 3.7+**

### Setup
```bash
# Clone or create the project
cd tdd-security-agent

# Install dependencies
pip install -r requirements.txt

# Pull the Deepseek Coder model
ollama pull deepseek-coder:6.7b

# Start Ollama server (if not already running)
ollama serve
```

## 🎯 Usage

### Enhanced Shell Script Interface 🚀

We've added a powerful shell script `analyze_or_test.sh` that provides an enhanced interface with additional features:

```bash
# Make script executable (first time only)
chmod +x analyze_or_test.sh

# Show all available commands and options
./analyze_or_test.sh --help
```

#### Quick Start with Shell Script

```bash
# Analyze a file (security + clean code)
./analyze_or_test.sh analyze src/coding_agent.py

# Security analysis only
./analyze_or_test.sh analyze samples/vulnerable_app.py --security

# Generate TDD tests
./analyze_or_test.sh test src/cli.py --framework pytest --output test_cli.py

# Interactive mode (recommended for beginners)
./analyze_or_test.sh interactive

# Analyze entire project
./analyze_or_test.sh project .

# Batch analyze multiple files
./analyze_or_test.sh batch src/*.py samples/*.py

# Watch directory for changes and auto-analyze
./analyze_or_test.sh watch src/

# Compare security analysis of two files
./analyze_or_test.sh compare old_version.py new_version.py
```

#### Shell Script Features

- 🎨 **Colored output** for better readability
- 🔍 **Interactive mode** with guided menus
- 📦 **Batch processing** of multiple files
- 👁️ **Directory watching** for continuous monitoring
- ⚖️ **File comparison** for version analysis
- ✅ **Automatic dependency checking**
- 🚀 **Auto-start Ollama** if not running
- 📊 **Progress tracking** for batch operations
- 🛡️ **Enhanced error handling** and validation

### Command Line Interface (Direct Python)

#### 1. Analyze a Single File
```bash
# Security and clean code review
python src/cli.py analyze --file main.py

# Security review only
python src/cli.py analyze --file main.py --security

# Clean code review only
python src/cli.py analyze --file main.py --clean-code
```

#### 2. Generate TDD Tests
```bash
# Generate pytest tests
python src/cli.py test --file main.py --framework pytest --output test_main.py

# Generate Jest tests for JavaScript
python src/cli.py test --file app.js --framework jest --output app.test.js

# Print tests to console
python src/cli.py test --file main.py
```

#### 3. Analyze Entire Project
```bash
# Use the enhanced shell script for analysis
./analyze_or_test.sh analyze src/coding_agent.py --security --clean-code

# Generate TDD tests
./analyze_or_test.sh test src/cli.py --framework pytest --output test_cli.py

# Analyze entire project
./analyze_or_test.sh project ./my-app

# Interactive mode
./analyze_or_test.sh interactive

# Batch mode
./analyze_or_test.sh batch src/*.py

# Watch mode
./analyze_or_test.sh watch src/

# Compare two file versions
./analyze_or_test.sh compare old_version.py new_version.py
```

### Python API

```python
from src.coding_agent import CodingAgent

# Initialize agent
agent = CodingAgent()

# Security review
security_review = agent.security_review("example.py", code_content)
print(f"Severity: {security_review.severity}")
print(f"Issues: {len(security_review.issues)}")

# Generate TDD tests
tests = agent.generate_tdd_tests("example.py", code_content, "pytest")
print(tests)

# Full file analysis
results = agent.analyze_file("example.py")
print(results["security"])
print(results["clean_code"])
```

## 🔧 Configuration

### Model Selection
You can use different Ollama models:
```bash
python src/cli.py analyze --file main.py --model codellama:7b
python src/cli.py analyze --file main.py --model deepseek-coder:1.3b
```

### Custom Security Patterns
Edit `src/coding_agent.py` to add custom security patterns:
```python
def _load_security_patterns(self):
    return {
        "custom_pattern": [
            "dangerous_function.*{",
            "unsafe_operation.*{",
        ],
        # ... existing patterns
    }
```

## 📊 Output Examples

### Security Review Output
```
🔒 Security Review for main.py
Overall Severity: HIGH
Confidence: 85%

📋 Issues Found:

1. SQL Injection
   Severity: HIGH
   Line: 15
   Description: Direct string concatenation in SQL query allows injection
   💡 Mitigation: Use parameterized queries or prepared statements
   ✅ Secure Example: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

2. Hardcoded Secret
   Severity: MEDIUM
   Line: 8
   Description: API key hardcoded in source code
   💡 Mitigation: Use environment variables or secure configuration
```

### Test Generation Output
```python
import pytest
from main import UserService

class TestUserService:
    def setup_method(self):
        self.user_service = UserService()
    
    def test_create_user_with_valid_data(self):
        # Arrange
        user_data = {"name": "John Doe", "email": "john@example.com"}
        
        # Act
        result = self.user_service.create_user(user_data)
        
        # Assert
        assert result["success"] == True
        assert "id" in result
    
    def test_create_user_with_invalid_email(self):
        # Arrange
        user_data = {"name": "John Doe", "email": "invalid-email"}
        
        # Act & Assert
        with pytest.raises(ValueError):
            self.user_service.create_user(user_data)
```

## 🎨 Customization

### Adding New Languages
1. Add file extension to `generate_project_tests()` method
2. Add test template in `_load_tdd_templates()`
3. Add language-specific security patterns

### Extending Security Patterns
Add patterns to `_load_security_patterns()`:
```python
"new_vulnerability": [
    "pattern1.*{",
    "pattern2.*{",
]
```

### Custom Test Templates
Add framework templates:
```python
"language": {
    "framework": """
    template content with {placeholders}
    """
}
```

## 🤝 Integration

### CI/CD Integration

#### Using Shell Script (Recommended)
```bash
# In your CI pipeline
./analyze_or_test.sh project . --quiet > security_report.txt
if grep -q "CRITICAL\|HIGH" security_report.txt; then
    echo "Security issues found!"
    exit 1
fi

# Batch analyze changed files
git diff --name-only HEAD~1 | grep -E '\.(py|js|ts|java|go|rs|cs|c|cpp|php|rb|swift|kt)$' | xargs ./analyze_or_test.sh batch
```

#### Using Direct Python
```bash
# In your CI pipeline
python src/cli.py project --project . > security_report.txt
if grep -q "CRITICAL\|HIGH" security_report.txt; then
    echo "Security issues found!"
    exit 1
fi
```

### Pre-commit Hook

#### Enhanced Hook with Shell Script
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Get list of changed files
changed_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts|java|go|rs|cs|c|cpp|php|rb|swift|kt)$')

if [ -n "$changed_files" ]; then
    echo "🔍 Running security analysis on changed files..."
    ./analyze_or_test.sh batch $changed_files --quiet
    
    if [ $? -ne 0 ]; then
        echo "❌ Security issues found! Please fix before committing."
        exit 1
    fi
fi
```

#### Simple Hook
```bash
#!/bin/sh
python src/cli.py analyze --file $1 --security
```

### IDE Integration
The agent can be integrated with VS Code, Vim, or other editors through custom plugins.

## 🛡️ Security Focus Areas

Based on your interest in **TDD and security code reviews**, this agent specializes in:

1. **Security Vulnerability Detection**
   - SQL injection prevention
   - XSS vulnerability identification
   - Authentication bypass detection
   - Insecure data handling
   - Cryptographic weaknesses

2. **Test-Driven Development**
   - Red-Green-Refactor cycle support
   - Comprehensive test coverage
   - Edge case identification
   - Mocking strategies
   - Test maintainability

3. **Clean Code & Best Practices**
   - SOLID principles enforcement
   - Code smell detection
   - Refactoring suggestions
   - Documentation quality
   - Performance considerations

## 🚧 Roadmap

- [ ] **IDE plugins** (VS Code, JetBrains)
- [ ] **Git hooks** integration
- [ ] **Custom rule sets** for organizations
- [ ] **Vulnerability database** integration
- [ ] **Performance optimization** analysis
- [ ] **API documentation** generation
- [ ] **Team collaboration** features

## 📝 License

This project is open source. Feel free to customize and extend for your needs.

## 🤝 Contributing

Contributions welcome! Areas of focus:
- Additional language support
- More security patterns
- Enhanced test templates
- Performance improvements
- Documentation

---

**Built with ❤️ for developers who care about security and code quality**
