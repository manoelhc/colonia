from rupy import Rupy, Response, Request
from app.database import create_db_and_tables
from app.api import (
    create_project_handler,
    list_projects_handler,
    get_project_handler,
    update_project_handler,
    delete_project_handler,
    trigger_repo_scan_handler,
)

app = Rupy()
app.set_template_directory("./templates")

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
    return {"title": "Colonia Dashboard"}


@app.template("/projects", template="projects.html.tpl")
def projects(request: Request) -> dict:
    """Render projects page with context data"""
    return {"title": "Colonia Projects"}


@app.template("/stacks", template="stacks.html.tpl")
def stacks(request: Request) -> dict:
    """Render stacks page with context data"""
    return {"title": "Colonia Stacks"}


@app.template("/settings", template="settings.html.tpl")
def settings(request: Request) -> dict:
    """Render settings page with context data"""
    return {"title": "Colonia Settings"}


@app.template("/environments", template="environments.html.tpl")
def environments(request: Request) -> dict:
    """Render environments page with context data"""
    return {"title": "Colonia Environments"}


@app.template("/contexts", template="contexts.html.tpl")
def contexts(request: Request) -> dict:
    """Render contexts page with context data"""
    return {"title": "Colonia Contexts"}


@app.template("/users", template="users.html.tpl")
def users(request: Request) -> dict:
    """Render users page with context data"""
    return {"title": "Colonia Users"}


@app.template("/teams", template="teams.html.tpl")
def teams(request: Request) -> dict:
    """Render teams page with context data"""
    return {"title": "Colonia Teams"}


# API Routes
@app.route("/api/projects", methods=["GET", "POST"])
def api_projects(request: Request) -> Response:
    """Handle projects API endpoint."""
    if request.method == "POST":
        return create_project_handler(request, app)
    else:  # GET
        return list_projects_handler(request, app)


@app.route("/api/projects/<project_id>", methods=["GET", "PUT", "DELETE"])
def api_project(request: Request, project_id: str) -> Response:
    """Handle single project API endpoint."""
    if request.method == "GET":
        return get_project_handler(request, app, project_id)
    elif request.method == "PUT":
        return update_project_handler(request, app, project_id)
    else:  # DELETE
        return delete_project_handler(request, app, project_id)


@app.route("/api/projects/<project_id>/scan", methods=["POST"])
def api_project_scan(request: Request, project_id: str) -> Response:
    """Trigger repository scan for a project."""
    return trigger_repo_scan_handler(request, app, project_id)


def main():
    """Run the Colonia web server."""
    # Initialize database
    create_db_and_tables()

    print("Starting Colonia Dashboard...")
    print("Access the dashboard at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
