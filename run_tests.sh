#!/bin/bash

# Test runner script for FastAPI backend
# This script installs test dependencies and runs all tests

set -e  # Exit on any error

echo "🧪 Setting up test environment..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed or not in PATH"
    exit 1
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip3 install -r requirements-test.txt

# Check if pytest is installed
if ! python3 -c "import pytest" &> /dev/null; then
    echo "❌ pytest is not installed. Please install it manually:"
    echo "   pip3 install pytest pytest-cov"
    exit 1
fi

echo "✅ Test dependencies installed successfully!"

# Run basic setup tests first
echo "🔧 Running basic setup tests..."
python3 -m pytest app/tests/test_basic.py -v

if [ $? -eq 0 ]; then
    echo "✅ Basic setup tests passed!"
else
    echo "❌ Basic setup tests failed. Please check your environment."
    exit 1
fi

# Run all tests
echo "🚀 Running all tests..."
python3 -m pytest app/tests/ -v --cov=app --cov-report=term-missing

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed successfully!"
    echo ""
    echo "📊 Coverage report generated."
    echo "📁 HTML coverage report: htmlcov/index.html"
    echo "📄 XML coverage report: coverage.xml"
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi 