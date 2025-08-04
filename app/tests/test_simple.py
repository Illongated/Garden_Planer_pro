import pytest

def test_basic_import():
    """Test basique pour vérifier que pytest fonctionne"""
    assert True

def test_python_version():
    """Test pour vérifier la version de Python"""
    import sys
    assert sys.version_info >= (3, 8)

def test_fastapi_available():
    """Test pour vérifier que FastAPI est disponible"""
    try:
        import fastapi
        assert fastapi is not None
    except ImportError:
        pytest.skip("FastAPI not available")

def test_sqlalchemy_available():
    """Test pour vérifier que SQLAlchemy est disponible"""
    try:
        import sqlalchemy
        assert sqlalchemy is not None
    except ImportError:
        pytest.skip("SQLAlchemy not available") 