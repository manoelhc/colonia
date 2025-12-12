from rupy import Rupy, Response

app = Rupy()

# Configure static files and templates
app.set_template_directory("templates")
app.static("/static", "static")


@app.get("/")
def index(request):
    """Serve the main dashboard page."""
    return app.template("dashboard.html")


def main():
    """Run the Colonia web server."""
    print("Starting Colonia Dashboard...")
    print("Access the dashboard at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
