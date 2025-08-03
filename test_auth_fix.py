#!/usr/bin/env python3
"""
Test script to validate authentication fixes
"""

def test_imports():
    """Test that all imports work correctly."""
    try:
        # Test auth endpoint import
        from app.api.v1.endpoints import auth
        print("✅ Auth endpoints imported successfully")
        
        # Test security functions
        from app.core.security import create_access_token, create_refresh_token
        print("✅ Security token functions imported successfully")
        
        # Test email service
        from app.services.email_service import email_service
        print("✅ Email service imported successfully")
        
        # Test API router includes auth
        from app.api.v1.api import api_router
        print("✅ API router imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_token_creation():
    """Test token creation functions."""
    try:
        from app.core.security import create_access_token, create_refresh_token
        
        # Test access token creation
        access_token = create_access_token("test_user_id")
        assert isinstance(access_token, str)
        assert len(access_token) > 10
        print("✅ Access token creation works")
        
        # Test refresh token creation  
        refresh_token = create_refresh_token("test_user_id")
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 10
        print("✅ Refresh token creation works")
        
        return True
    except Exception as e:
        print(f"❌ Token creation error: {e}")
        return False

def test_router_setup():
    """Test that auth router is properly included."""
    try:
        from app.api.v1.api import api_router
        
        # Check if auth routes are included
        routes = [route.path for route in api_router.routes]
        auth_routes = [route for route in routes if route.startswith('/auth')]
        
        if auth_routes:
            print(f"✅ Auth routes found: {auth_routes}")
            return True
        else:
            print("❌ No auth routes found in API router")
            return False
            
    except Exception as e:
        print(f"❌ Router setup error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Authentication Fixes...")
    print("-" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Token Creation Tests", test_token_creation),
        ("Router Setup Tests", test_router_setup)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}:")
        results.append(test_func())
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("✅ Authentication fixes are working correctly!")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("❌ Some issues remain, check the errors above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)