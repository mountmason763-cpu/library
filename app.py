import os
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, render_template, request, redirect, url_for, flash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "library-app-secret")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def index():
    response = supabase.table("students").select("*").order("id", desc=True).execute()
    students = response.data
    return render_template("index.html", students=students)


@app.route("/add", methods=["POST"])
def add_student():
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    semester = request.form.get("semester", "").strip()
    faculty = request.form.get("faculty", "").strip()
    book = request.form.get("book", "").strip()

    if not (full_name and phone and semester and faculty and book):
        flash("Please fill in all fields.", "error")
        return redirect(url_for("index"))

    try:
        supabase.table("students").insert(
            {
                "full_name": full_name,
                "phone": phone,
                "semester": semester,
                "faculty": faculty,
                "book": book,
            }
        ).execute()
    except Exception as exc:
        flash(f"Failed to save: {exc}", "error")
        return redirect(url_for("index"))

    flash("Record added successfully.", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    try:
        supabase.table("students").delete().eq("id", student_id).execute()
    except Exception as exc:
        flash(f"Failed to delete: {exc}", "error")
        return redirect(url_for("index"))
    flash("Record deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
