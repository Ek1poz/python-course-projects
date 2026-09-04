from flask import render_template

from app import app

courses = [
    {"name": "Python", "teacher": "John", "duration": "3 months"},
    {"name": "Machine Learning", "teacher": "Anna", "duration": "4 months"},
    {"name": "HTML & CSS", "teacher": "Mike", "duration": "2 months"},
]


@app.route("/")
def index() -> str:
    """Show the home page."""
    return render_template("index.html")


@app.route("/courses")
def show_courses() -> str:
    """Show the list of courses."""
    return render_template("courses.html", courses=courses)


@app.route("/about")
def about() -> str:
    """Show information about the project."""
    return render_template("about.html")
