"""Tests for main FastAPI application setup."""
import pytest
from fastapi.testclient import TestClient

from main import app


class TestMainApp:
    """Test the main FastAPI application configuration."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_app_instance(self):
        """Test that the app is a FastAPI instance."""
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        # Check that middleware is added
        assert len(app.user_middleware) > 0

        # Find CORS middleware
        cors_middleware = None
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_middleware = middleware
                break

        assert cors_middleware is not None, "CORS middleware not found"

    def test_routers_included(self):
        """Test that both auth and analysis routers are included."""
        # Get all routes from the app
        routes = [route.path for route in app.routes]

        # Check for auth routes
        assert any("/auth/signup" in route for route in routes), "Auth signup route not found"
        assert any("/auth/login" in route for route in routes), "Auth login route not found"
        assert any("/auth/me" in route for route in routes), "Auth me route not found"

        # Check for analysis routes
        assert any("/analyze" in route for route in routes), "Analyze route not found"
        assert any("/history" in route for route in routes), "History route not found"

    def test_app_responds_to_requests(self, client):
        """Test that the app responds to HTTP requests."""
        # This should return 404 for root, but proves the app is running
        response = client.get("/")
        # Any response (even 404) means the app is working
        assert response.status_code in [200, 404, 405]

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.options("/auth/signup", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST"
        })

        # Should have CORS headers (even if endpoint doesn't exist, middleware should respond)
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
