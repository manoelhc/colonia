import os
import mimetypes
from rupy import Rupy, Response, Request

app = Rupy()

static_dir = "./static"

print(static_dir)

@app.static("/static/js", f"{static_dir}/js")
def static_js_files(response: Response) -> Response:
    return response

@app.static("/static/css", f"{static_dir}/css")
def static_css_files(response: Response) -> Response:
    return response

@app.static("/static/locales", f"{static_dir}/locales")
def static_i18n_files(response: Response) -> Response:
    return response

@app.template("/", template="dashboard.html.tpl")
def index(request: Request) -> dict:
    """Render template with context data"""
    return {
        "title": "Colonia Dashboard"
    }

def main():
    """Run the Colonia web server."""
    print("Starting Colonia Dashboard...")
    print("Access the dashboard at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
