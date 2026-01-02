from rupy import Rupy, Response, Request
from app.database import create_db_and_tables
from app.api import (
    create_project_handler,
    list_projects_handler,
    get_project_handler,
    update_project_handler,
    delete_project_handler,
    trigger_repo_scan_handler,
    get_stats_handler,
    get_stacks_grouped_handler,
    get_environments_grouped_handler,
    create_user_handler,
    list_users_handler,
    get_user_handler,
    update_user_handler,
    delete_user_handler,
    create_team_handler,
    list_teams_handler,
    get_team_handler,
    update_team_handler,
    delete_team_handler,
    add_team_member_handler,
    remove_team_member_handler,
    set_team_permission_handler,
    delete_team_permission_handler,
    get_vault_config_handler,
    save_vault_config_handler,
    test_vault_connection_handler,
    list_secrets_engines_handler,
    enable_secrets_engine_handler,
    create_context_handler,
    list_contexts_handler,
    get_context_handler,
    update_context_handler,
    delete_context_handler,
    list_context_secrets_handler,
    add_context_secret_handler,
    delete_context_secret_handler,
    list_context_env_vars_handler,
    add_context_env_var_handler,
    delete_context_env_var_handler,
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


@app.template("/settings/ai-integration", template="settings_ai_integration.html.tpl")
def settings_ai_integration(request: Request) -> dict:
    """Render AI Integration settings page"""
    return {"title": "Colonia - AI Integration"}


@app.template("/settings/infracost", template="settings_infracost.html.tpl")
def settings_infracost(request: Request) -> dict:
    """Render Infracost settings page"""
    return {"title": "Colonia - Infracost"}


@app.template("/settings/backend-storage", template="settings_backend_storage.html.tpl")
def settings_backend_storage(request: Request) -> dict:
    """Render Backend Storage settings page"""
    return {"title": "Colonia - Backend Storage"}


@app.template("/settings/secrets-vault", template="settings_secrets_vault.html.tpl")
def settings_secrets_vault(request: Request) -> dict:
    """Render Secrets Vault settings page"""
    return {"title": "Colonia - Secrets Vault"}


@app.template("/settings/container-registry", template="settings_container_registry.html.tpl")
def settings_container_registry(request: Request) -> dict:
    """Render Container Registry settings page"""
    return {"title": "Colonia - Container Registry"}


@app.template("/settings/database-integration", template="settings_database_integration.html.tpl")
def settings_database_integration(request: Request) -> dict:
    """Render Database Integration settings page"""
    return {"title": "Colonia - Database Integration"}


@app.template("/settings/rabbitmq-integration", template="settings_rabbitmq_integration.html.tpl")
def settings_rabbitmq_integration(request: Request) -> dict:
    """Render RabbitMQ Integration settings page"""
    return {"title": "Colonia - RabbitMQ Integration"}


@app.template("/settings/redis-integration", template="settings_redis_integration.html.tpl")
def settings_redis_integration(request: Request) -> dict:
    """Render Redis Integration settings page"""
    return {"title": "Colonia - Redis Integration"}


@app.template("/settings/github-integration", template="settings_github_integration.html.tpl")
def settings_github_integration(request: Request) -> dict:
    """Render GitHub Integration settings page"""
    return {"title": "Colonia - GitHub Integration"}


@app.template("/settings/gitlab-integration", template="settings_gitlab_integration.html.tpl")
def settings_gitlab_integration(request: Request) -> dict:
    """Render GitLab Integration settings page"""
    return {"title": "Colonia - GitLab Integration"}


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


@app.route("/api/stats", methods=["GET"])
def api_stats(request: Request) -> Response:
    """Get dashboard statistics."""
    return get_stats_handler(request, app)


@app.route("/api/stacks/grouped", methods=["GET"])
def api_stacks_grouped(request: Request) -> Response:
    """Get stacks grouped by project and environment."""
    return get_stacks_grouped_handler(request, app)


@app.route("/api/environments/grouped", methods=["GET"])
def api_environments_grouped(request: Request) -> Response:
    """Get environments grouped by project."""
    return get_environments_grouped_handler(request, app)


# User API Routes
@app.route("/api/users", methods=["GET", "POST"])
def api_users(request: Request) -> Response:
    """Handle users API endpoint."""
    if request.method == "POST":
        return create_user_handler(request, app)
    else:  # GET
        return list_users_handler(request, app)


@app.route("/api/users/<user_id>", methods=["GET", "PUT", "DELETE"])
def api_user(request: Request, user_id: str) -> Response:
    """Handle single user API endpoint."""
    if request.method == "GET":
        return get_user_handler(request, app, user_id)
    elif request.method == "PUT":
        return update_user_handler(request, app, user_id)
    else:  # DELETE
        return delete_user_handler(request, app, user_id)


# Team API Routes
@app.route("/api/teams", methods=["GET", "POST"])
def api_teams(request: Request) -> Response:
    """Handle teams API endpoint."""
    if request.method == "POST":
        return create_team_handler(request, app)
    else:  # GET
        return list_teams_handler(request, app)


@app.route("/api/teams/<team_id>", methods=["GET", "PUT", "DELETE"])
def api_team(request: Request, team_id: str) -> Response:
    """Handle single team API endpoint."""
    if request.method == "GET":
        return get_team_handler(request, app, team_id)
    elif request.method == "PUT":
        return update_team_handler(request, app, team_id)
    else:  # DELETE
        return delete_team_handler(request, app, team_id)


@app.route("/api/teams/<team_id>/members", methods=["POST"])
def api_team_add_member(request: Request, team_id: str) -> Response:
    """Add a member to a team."""
    return add_team_member_handler(request, app, team_id)


@app.route("/api/teams/<team_id>/members/<member_id>", methods=["DELETE"])
def api_team_remove_member(request: Request, team_id: str, member_id: str) -> Response:
    """Remove a member from a team."""
    return remove_team_member_handler(request, app, team_id, member_id)


@app.route("/api/teams/<team_id>/permissions", methods=["POST"])
def api_team_set_permission(request: Request, team_id: str) -> Response:
    """Set or update a team permission."""
    return set_team_permission_handler(request, app, team_id)


@app.route("/api/teams/<team_id>/permissions/<permission_id>", methods=["DELETE"])
def api_team_delete_permission(request: Request, team_id: str, permission_id: str) -> Response:
    """Delete a team permission."""
    return delete_team_permission_handler(request, app, team_id, permission_id)


# Vault API Routes
@app.route("/api/vault/config", methods=["GET"])
def api_get_vault_config(request: Request) -> Response:
    """Get Vault configuration."""
    return get_vault_config_handler(request, app)


@app.route("/api/vault/config", methods=["POST"])
def api_save_vault_config(request: Request) -> Response:
    """Save Vault configuration."""
    return save_vault_config_handler(request, app)


@app.route("/api/vault/test", methods=["POST"])
def api_test_vault_connection(request: Request) -> Response:
    """Test Vault connection."""
    return test_vault_connection_handler(request, app)


@app.route("/api/vault/secrets-engines", methods=["GET"])
def api_list_secrets_engines(request: Request) -> Response:
    """List all secrets engines in Vault."""
    return list_secrets_engines_handler(request, app)


@app.route("/api/vault/secrets-engine", methods=["POST"])
def api_enable_secrets_engine(request: Request) -> Response:
    """Enable a secrets engine in Vault."""
    return enable_secrets_engine_handler(request, app)


# Context API Routes
@app.route("/api/contexts", methods=["GET", "POST"])
def api_contexts(request: Request) -> Response:
    """Handle contexts API endpoint."""
    if request.method == "POST":
        return create_context_handler(request, app)
    else:  # GET
        return list_contexts_handler(request, app)


@app.route("/api/contexts/<context_id>", methods=["GET", "PUT", "DELETE"])
def api_context(request: Request, context_id: str) -> Response:
    """Handle single context API endpoint."""
    if request.method == "GET":
        return get_context_handler(request, app, context_id)
    elif request.method == "PUT":
        return update_context_handler(request, app, context_id)
    else:  # DELETE
        return delete_context_handler(request, app, context_id)


@app.route("/api/contexts/<context_id>/secrets", methods=["GET", "POST"])
def api_context_secrets(request: Request, context_id: str) -> Response:
    """Handle context secrets API endpoint."""
    if request.method == "POST":
        return add_context_secret_handler(request, app, context_id)
    else:  # GET
        return list_context_secrets_handler(request, app, context_id)


@app.route("/api/contexts/<context_id>/secrets/<secret_id>", methods=["DELETE"])
def api_context_secret(request: Request, context_id: str, secret_id: str) -> Response:
    """Handle single context secret API endpoint."""
    return delete_context_secret_handler(request, app, context_id, secret_id)


@app.route("/api/contexts/<context_id>/env-vars", methods=["GET", "POST"])
def api_context_env_vars(request: Request, context_id: str) -> Response:
    """Handle context environment variables API endpoint."""
    if request.method == "POST":
        return add_context_env_var_handler(request, app, context_id)
    else:  # GET
        return list_context_env_vars_handler(request, app, context_id)


@app.route("/api/contexts/<context_id>/env-vars/<env_var_id>", methods=["DELETE"])
def api_context_env_var(request: Request, context_id: str, env_var_id: str) -> Response:
    """Handle single context environment variable API endpoint."""
    return delete_context_env_var_handler(request, app, context_id, env_var_id)


def main():
    """Run the Colonia web server."""
    # Initialize database
    create_db_and_tables()

    print("Starting Colonia Dashboard...")
    print("Access the dashboard at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
