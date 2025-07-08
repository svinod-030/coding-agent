#!/usr/bin/env python3
"""
TDD & Security Coding Agent using Deepseek Coder
Focuses on Test-Driven Development and Security Code Reviews
"""

import json
import subprocess
import os
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
from enum import Enum

class ReviewType(Enum):
    SECURITY = "security"
    TDD = "tdd"
    CLEAN_CODE = "clean_code"
    BEST_PRACTICES = "best_practices"

@dataclass
class CodeReview:
    file_path: str
    review_type: ReviewType
    issues: List[Dict]
    suggestions: List[str]
    severity: str
    confidence: float

class CodingAgent:
    def __init__(self, model_name: str = "deepseek-coder:6.7b"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"
        self.security_patterns = self._load_security_patterns()
        self.tdd_templates = self._load_tdd_templates()
        
    def _load_security_patterns(self) -> Dict:
        """Load security vulnerability patterns"""
        return {
            "sql_injection": [
                "SELECT.*FROM.*WHERE.*=.*{",
                "INSERT.*INTO.*VALUES.*{",
                "UPDATE.*SET.*WHERE.*=.*{",
                "DELETE.*FROM.*WHERE.*=.*{",
                "CREATE.*TABLE.*{",
                "DROP.*TABLE.*{",
            ],
            "xss": [
                "innerHTML.*=.*{",
                "document.write.*{",
                "eval.*{",
                "dangerouslySetInnerHTML.*{",
                "v-html.*=.*{",  # Vue.js
            ],
            "hardcoded_secrets": [
                "password.*=.*['\"].*['\"]",
                "api_key.*=.*['\"].*['\"]",
                "secret.*=.*['\"].*['\"]",
                "token.*=.*['\"].*['\"]",
                "private_key.*=.*['\"].*['\"]",
            ],
            "insecure_random": [
                "Math.random()",
                "random.random()",
                "rand()",  # C/C++
                "Random()"  # C#
            ],
            "path_traversal": [
                "\.\./",
                "os.path.join.*\.\.",
                "File.ReadAllText.*\.\.",
            ],
            "command_injection": [
                "os.system.*{",
                "subprocess.call.*{",
                "exec.*{",
                "Runtime.getRuntime().exec.*{",
            ],
            "insecure_deserialization": [
                "pickle.loads.*{",
                "yaml.load.*{",
                "ObjectInputStream.*{",
                "JSON.parse.*{",
            ]
        }
    
    def _load_tdd_templates(self) -> Dict:
        """Load TDD test templates"""
        return {
            "python": {
                "unittest": """
import unittest
from {module} import {class_name}

class Test{class_name}(unittest.TestCase):
    def setUp(self):
        self.{instance} = {class_name}()
    
    def test_{method_name}(self):
        # Arrange
        {arrange_code}
        
        # Act
        result = self.{instance}.{method_name}({parameters})
        
        # Assert
        self.assertEqual(result, {expected})
        
if __name__ == '__main__':
    unittest.main()
""",
                "pytest": """
import pytest
from {module} import {class_name}

class Test{class_name}:
    def setup_method(self):
        self.{instance} = {class_name}()
    
    def test_{method_name}(self):
        # Arrange
        {arrange_code}
        
        # Act
        result = self.{instance}.{method_name}({parameters})
        
        # Assert
        assert result == {expected}
"""
            },
            "javascript": {
                "jest": """
const {class_name} = require('./{module}');

describe('{class_name}', () => {
    let {instance};
    
    beforeEach(() => {
        {instance} = new {class_name}();
    });
    
    test('should {test_description}', () => {
        // Arrange
        {arrange_code}
        
        // Act
        const result = {instance}.{method_name}({parameters});
        
        // Assert
        expect(result).toBe({expected});
    });
});
""",
                "mocha": """
const {class_name} = require('./{module}');
const assert = require('assert');

describe('{class_name}', () => {
    let {instance};
    
    beforeEach(() => {
        {instance} = new {class_name}();
    });
    
    it('should {test_description}', () => {
        // Arrange
        {arrange_code}
        
        // Act
        const result = {instance}.{method_name}({parameters});
        
        // Assert
        assert.strictEqual(result, {expected});
    });
});
"""
            },
            "typescript": {
                "jest": """
import {{ {class_name} }} from './{module}';

describe('{class_name}', () => {
    let {instance}: {class_name};
    
    beforeEach(() => {
        {instance} = new {class_name}();
    });
    
    test('should {test_description}', () => {
        // Arrange
        {arrange_code}
        
        // Act
        const result = {instance}.{method_name}({parameters});
        
        // Assert
        expect(result).toBe({expected});
    });
});
"""
            },
            "java": {
                "junit5": """
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

class {class_name}Test {{
    private {class_name} {instance};
    
    @BeforeEach
    void setUp() {{
        {instance} = new {class_name}();
    }}
    
    @Test
    void should{test_description}() {{
        // Arrange
        {arrange_code}
        
        // Act
        var result = {instance}.{method_name}({parameters});
        
        // Assert
        assertEquals({expected}, result);
    }}
}}
"""
            },
            "go": {
                "testing": """
package {package_name}

import (
    "testing"
)

func Test{class_name}_{method_name}(t *testing.T) {{
    // Arrange
    {instance} := &{class_name}{{}}
    {arrange_code}
    
    // Act
    result := {instance}.{method_name}({parameters})
    
    // Assert
    if result != {expected} {{
        t.Errorf("Expected %v, got %v", {expected}, result)
    }}
}}
"""
            },
            "csharp": {
                "nunit": """
using NUnit.Framework;

namespace {namespace}
{{
    [TestFixture]
    public class {class_name}Tests
    {{
        private {class_name} {instance};
        
        [SetUp]
        public void Setup()
        {{
            {instance} = new {class_name}();
        }}
        
        [Test]
        public void Should{test_description}()
        {{
            // Arrange
            {arrange_code}
            
            // Act
            var result = {instance}.{method_name}({parameters});
            
            // Assert
            Assert.AreEqual({expected}, result);
        }}
    }}
}}
"""
            },
            "rust": {
                "cargo_test": """
#[cfg(test)]
mod tests {{
    use super::*;
    
    #[test]
    fn test_{method_name}() {{
        // Arrange
        let {instance} = {class_name}::new();
        {arrange_code}
        
        // Act
        let result = {instance}.{method_name}({parameters});
        
        // Assert
        assert_eq!(result, {expected});
    }}
}}
"""
            }
        }
    
    def _query_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Query Ollama API"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            
            return response.json().get("response", "")
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"
    
    def security_review(self, file_path: str, code: str) -> CodeReview:
        """Perform security code review"""
        system_prompt = """
You are a security expert conducting a code review. Focus on:
1. Common vulnerabilities (OWASP Top 10)
2. Input validation issues
3. Authentication/authorization flaws
4. Insecure data handling
5. Cryptographic issues
6. Dependency vulnerabilities

Provide specific, actionable feedback with severity levels (LOW, MEDIUM, HIGH, CRITICAL).
"""
        
        prompt = f"""
Review this code for security vulnerabilities:

File: {file_path}
Code:
```
{code}
```

Identify security issues and provide:
1. Vulnerability type
2. Location in code
3. Severity level
4. Mitigation strategy
5. Secure code example

Format as JSON with structure:
{{
    "issues": [
        {{
            "type": "vulnerability_type",
            "line": line_number,
            "severity": "LOW|MEDIUM|HIGH|CRITICAL",
            "description": "detailed description",
            "mitigation": "how to fix",
            "secure_example": "corrected code"
        }}
    ]
}}
"""
        
        response = self._query_ollama(prompt, system_prompt)
        
        # Parse response and create CodeReview object
        try:
            result = json.loads(response)
            return CodeReview(
                file_path=file_path,
                review_type=ReviewType.SECURITY,
                issues=result.get("issues", []),
                suggestions=[],
                severity=self._calculate_overall_severity(result.get("issues", [])),
                confidence=0.85
            )
        except json.JSONDecodeError:
            return CodeReview(
                file_path=file_path,
                review_type=ReviewType.SECURITY,
                issues=[{"type": "parse_error", "description": response}],
                suggestions=[],
                severity="LOW",
                confidence=0.1
            )
    
    def generate_tdd_tests(self, file_path: str, code: str, test_framework: str = "pytest") -> str:
        """Generate TDD tests for given code"""
        system_prompt = """
You are a TDD expert. Generate comprehensive unit tests following TDD principles:
1. Test behavior, not implementation
2. Use Arrange-Act-Assert pattern
3. Test edge cases and error conditions
4. Write descriptive test names
5. Include setup and teardown when needed
6. Follow the Red-Green-Refactor cycle
"""
        
        prompt = f"""
Generate TDD tests for this code:

File: {file_path}
Code:
```
{code}
```

Requirements:
- Use {test_framework} framework
- Cover all public methods
- Include edge cases and error scenarios
- Follow naming conventions
- Add docstrings for complex tests
- Consider mocking for external dependencies

Generate complete test file with proper imports and structure.
"""
        
        response = self._query_ollama(prompt, system_prompt)
        return response
    
    def clean_code_review(self, file_path: str, code: str) -> CodeReview:
        """Review code for clean code principles"""
        system_prompt = """
You are a clean code expert. Review code for:
1. Code readability and clarity
2. Function/method length and complexity
3. Naming conventions
4. Code duplication
5. Comments and documentation
6. SOLID principles adherence
7. Code organization and structure
"""
        
        prompt = f"""
Review this code for clean code principles:

File: {file_path}
Code:
```
{code}
```

Identify improvements for:
1. Readability and clarity
2. Function complexity
3. Naming conventions
4. Code duplication
5. Documentation
6. Structure and organization

Provide specific refactoring suggestions with examples.
"""
        
        response = self._query_ollama(prompt, system_prompt)
        
        # Parse and return CodeReview
        return CodeReview(
            file_path=file_path,
            review_type=ReviewType.CLEAN_CODE,
            issues=[],
            suggestions=response.split('\n'),
            severity="LOW",
            confidence=0.8
        )
    
    def _calculate_overall_severity(self, issues: List[Dict]) -> str:
        """Calculate overall severity from individual issues"""
        if not issues:
            return "LOW"
        
        severity_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        max_severity = max(severity_weights.get(issue.get("severity", "LOW"), 1) for issue in issues)
        
        for severity, weight in severity_weights.items():
            if weight == max_severity:
                return severity
        
        return "LOW"
    
    def analyze_file(self, file_path: str) -> Dict[str, CodeReview]:
        """Comprehensive analysis of a code file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return {"error": f"Cannot read file: {str(e)}"}
        
        results = {}
        
        # Security review
        results["security"] = self.security_review(file_path, code)
        
        # Clean code review
        results["clean_code"] = self.clean_code_review(file_path, code)
        
        return results
    
    def generate_project_tests(self, project_path: str, test_framework: str = "pytest") -> Dict[str, str]:
        """Generate tests for entire project"""
        test_results = {}
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.cs', '.php', '.rb', '.swift', '.kt')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code = f.read()
                        
                        tests = self.generate_tdd_tests(file_path, code, test_framework)
                        test_results[file_path] = tests
                    except Exception as e:
                        test_results[file_path] = f"Error generating tests: {str(e)}"
        
        return test_results

if __name__ == "__main__":
    agent = CodingAgent()
    
    # Example usage
    sample_code = """
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return execute_query(query)
"""
    
    # Security review
    security_review = agent.security_review("example.py", sample_code)
    print("Security Review:", security_review)
    
    # Generate tests
    tests = agent.generate_tdd_tests("example.py", sample_code)
    print("Generated Tests:", tests)
