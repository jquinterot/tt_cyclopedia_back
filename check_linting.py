#!/usr/bin/env python3
"""
Simple linting script to check for common Python code quality issues.
"""
import os
import ast
import re
from pathlib import Path

def check_file(file_path):
    """Check a single Python file for common linting issues."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            # Trailing whitespace
            if line.rstrip() != line and line.strip():
                issues.append(f"Line {i}: Trailing whitespace")
            
            # Line too long (over 120 characters)
            if len(line) > 120:
                issues.append(f"Line {i}: Line too long ({len(line)} characters)")
            
            # Mixed tabs and spaces
            if '\t' in line and '    ' in line:
                issues.append(f"Line {i}: Mixed tabs and spaces")
        
        # Check for unused imports (basic check)
        try:
            tree = ast.parse(content)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
        
        # Check for common patterns
        if re.search(r'print\s*\(', content):
            issues.append("Contains print statements (consider using logging)")
        
        if re.search(r'except:', content):
            issues.append("Bare except clause found (specify exception type)")
        
        if re.search(r'assert\s+[^,]+$', content, re.MULTILINE):
            issues.append("Assert statements found (remove for production)")
        
        return issues
        
    except Exception as e:
        return [f"Error reading file: {e}"]

def main():
    """Main function to check all Python files in the app directory."""
    app_dir = Path("app")
    if not app_dir.exists():
        print("❌ app directory not found")
        return 1
    
    total_issues = 0
    files_checked = 0
    
    print("🔍 Checking Python files for linting issues...")
    print("=" * 60)
    
    for py_file in app_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        files_checked += 1
        issues = check_file(py_file)
        
        if issues:
            print(f"\n📁 {py_file}")
            for issue in issues:
                print(f"  ⚠️  {issue}")
                total_issues += 1
        else:
            print(f"✅ {py_file}")
    
    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"  Files checked: {files_checked}")
    print(f"  Total issues: {total_issues}")
    
    if total_issues == 0:
        print("🎉 No linting issues found!")
        return 0
    else:
        print(f"⚠️  Found {total_issues} linting issues")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 