from flask import Flask, redirect, render_template
from flask_login import current_user

from app.backend.fireplaces import fireplace_manager
from app.blueprints.api import api
from app.blueprints.auth import auth, login_manager
from app.models import User, db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../database/database.db"
app.config["SECRET_KEY"] = "MASZIN"

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(api)
app.register_blueprint(auth)


@app.route("/")
def home():
    if current_user:
        return render_template("join.html")
    return redirect("/auth/login")


@app.route("/fireplace/<string:code>", methods=["GET"])
def fireplace(code: int):
    fireplace = fireplace_manager.get_fireplace(code)

    if not fireplace:
        return f"No fireplace with code {code}"

    if current_user.id == fireplace.host_id:
        names = User.query.filter(User.id.in_(fireplace.guests)).all()

        return render_template(
            "fireplacemaster.html",
            fireplace=(fireplace.code, fireplace.title, names),
        )

    if not current_user.id in fireplace.get_guest_ids():
        fireplace.add_guest(current_user.id)

    return render_template("fireplace.html", title=fireplace.title)


@app.route("/ranking", methods=["GET"])
def ranking():
    return render_template(
        "ranking.html", rank_list=User.query.order_by(User.points).all()
    )
