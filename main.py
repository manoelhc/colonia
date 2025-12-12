import os
import mimetypes
from rupy import Rupy, Response

app = Rupy()

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def serve_file_from_static(filepath):
    """Helper function to serve a file from the static directory."""
    full_path = os.path.join(STATIC_DIR, filepath)
    
    # Security check: prevent directory traversal
    if not os.path.abspath(full_path).startswith(os.path.abspath(STATIC_DIR)):
        return Response("Forbidden", status=403)
    
    # Check if file exists
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return Response("Not Found", status=404)
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(full_path)
    if content_type is None:
        content_type = "application/octet-stream"
    
    # Read file content
    try:
        # Read as text for text files, binary for others
        if content_type and content_type.startswith(('text/', 'application/json', 'application/javascript')):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            with open(full_path, "rb") as f:
                content = f.read()
    except Exception as e:
        return Response(f"Error reading file: {e}", status=500)
    
    # Create response
    response = Response(content, status=200)
    response.set_header("Content-Type", content_type)
    response.set_header("Cache-Control", "max-age=3600")
    return response


# Register specific static file routes
@app.get("/static/css/styles.css")
def serve_styles_css(request):
    return serve_file_from_static("css/styles.css")


@app.get("/static/js/theme.js")
def serve_theme_js(request):
    return serve_file_from_static("js/theme.js")


@app.get("/static/js/i18n.js")
def serve_i18n_js(request):
    return serve_file_from_static("js/i18n.js")


@app.get("/static/locales/en.json")
def serve_en_locale(request):
    return serve_file_from_static("locales/en.json")


@app.get("/static/locales/pt.json")
def serve_pt_locale(request):
    return serve_file_from_static("locales/pt.json")


@app.get("/static/locales/es.json")
def serve_es_locale(request):
    return serve_file_from_static("locales/es.json")


@app.get("/")
def index(request):
    """Serve the main dashboard page."""
    template_path = os.path.join(TEMPLATES_DIR, "dashboard.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    response = Response(html_content, status=200)
    response.set_header("Content-Type", "text/html; charset=utf-8")
    return response


def main():
    """Run the Colonia web server."""
    print("Starting Colonia Dashboard...")
    print("Access the dashboard at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
