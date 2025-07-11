#!/usr/bin/env python3
"""
Fast test script that bypasses Cloudinary imports for quick testing
"""
import os
import sys
import types
import pytest

# Set environment before any imports
os.environ["ENVIRONMENT"] = "testing"
os.environ["SQL_LITE_DB"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "testsecret"
os.environ["ALGORITHM"] = "HS256"

# Mock cloudinary to avoid import issues
class MockCloudinary:
    def config(self, **kwargs):
        pass
    
    def uploader(self):
        return self
    
    def upload(self, *args, **kwargs):
        return {"secure_url": "/static/uploads/test.jpg"}
    
    def destroy(self, *args, **kwargs):
        pass

# Create proper mock modules
mock_cloudinary = types.ModuleType('cloudinary')
mock_uploader = types.ModuleType('cloudinary.uploader')
mock_api = types.ModuleType('cloudinary.api')

# Mock the cloudinary module
sys.modules['cloudinary'] = mock_cloudinary
sys.modules['cloudinary.uploader'] = mock_uploader
sys.modules['cloudinary.api'] = mock_api

if __name__ == "__main__":
    # Run a simple test
    pytest.main([
        "app/tests/test_users.py::TestSetup::test_imports_work",
        "-v",
        "--tb=short"
    ]) 