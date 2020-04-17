from app.home import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required


@blueprint.route("/<template>")
@login_required
def route_template(template):
    if template == "logout":
        return redirect(url_for("base_blueprint.logout"))
    return render_template(template + ".html")
