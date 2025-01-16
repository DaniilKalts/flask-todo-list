from flask import Flask, render_template, request, jsonify, redirect
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

# ==================== #

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task_manager.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
Scss(app)

# ==================== #

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(30), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"Task ID: {self.id}"


with app.app_context():
    db.create_all()


# ==================== #


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        tasks = Task.query.order_by(Task.created_at).all()
        return render_template("index.html", tasks=tasks)
    else:
        content = request.form["content"]

        new_task = Task(content=content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as error:
            return f"ERROR: {error}"


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int):
    task = Task.query.get_or_404(task_id)

    try:
        db.session.delete(task)
        db.session.commit()
        return (
            jsonify(
                {"success": True, "message": f"Task with ID {task_id} was deleted"}
            ),
            200,
        )
    except Exception as error:
        return f"ERROR: {error}"


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Task with ID {task_id} was {'completed' if task.completed else 'uncompleted'}",
                }
            ),
            200,
        )
    except Exception as error:
        return f"ERROR: {error}"


# ==================== #

if __name__ == "__main__":
    app.run()
