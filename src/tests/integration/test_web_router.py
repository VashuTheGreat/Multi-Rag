import pytest


def test_index_page(client):
    """GET / should render the Jinja2 index template with 200 OK and Chai Prep theme elements."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    content = response.text
    assert "Chai Prep" in content
    assert "Multi-RAG" in content
    assert "New Thread" in content
    assert "Ingest Documents" in content
    assert "theme-dark" in content


def test_static_theme_css(client):
    """GET /static/css/theme.css should serve the stylesheet with 200 OK."""
    response = client.get("/static/css/theme.css")
    assert response.status_code == 200
    assert "text/css" in response.headers.get("content-type", "")
    assert "--accent-chai" in response.text
    assert "--user-avatar-bg" in response.text
    assert "--ai-avatar-bg" in response.text


def test_static_app_js(client):
    """GET /static/js/app.js should serve the JavaScript client logic with 200 OK."""
    response = client.get("/static/js/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers.get("content-type", "")
    assert "/api/v1/conversations" in response.text
    assert "multi_rag_threads" not in response.text
    assert "/api/v1/chat" in response.text
    assert "/api/v1/ingest" in response.text
