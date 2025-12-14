import os
import mimetypes
from rupy import Rupy, Response, Request

app = Rupy()

static_dir = os.getenv("PWD")

@app.static("/js", f"{static_dir}/static/js")
def static_js_files():
    pass

@app.static("/css", f"{static_dir}/css")
def static_css_files():
    pass

@app.static("/locales", f"{static_dir}/locales")
def static_i18n_files():
    pass


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
