from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

create_table()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()

    if request.method == "POST":
        item = request.form["item"]
        amount = float(request.form["amount"])
        date = request.form["date"]

        conn.execute(
            "INSERT INTO expenses (item, amount, date) VALUES (?, ?, ?)",
            (item, amount, date)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY date DESC"
    ).fetchall()

    overall_total = conn.execute(
        "SELECT SUM(amount) FROM expenses"
    ).fetchone()[0] or 0

    grouped_expenses = {}
    daily_totals = {}   # 🔹 NEW

    for expense in expenses:
        date = expense["date"]

        if date not in grouped_expenses:
            grouped_expenses[date] = []
            daily_totals[date] = 0   # 🔹 initialize total for that day

        grouped_expenses[date].append(expense)
        daily_totals[date] += expense["amount"]  # 🔹 add amount

    conn.close()

    return render_template(
        "index.html",
        grouped_expenses=grouped_expenses,
        daily_totals=daily_totals,   # 🔹 PASS TO TEMPLATE
        total=overall_total
    )

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):
    conn = get_db_connection()

    if request.method == "POST":
        item = request.form["item"]
        amount = float(request.form["amount"])
        date = request.form["date"]

        conn.execute(
            "UPDATE expenses SET item = ?, amount = ?, date = ? WHERE id = ?",
            (item, amount, date, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()
    return render_template("edit.html", expense=expense)

@app.route("/delete/<int:id>", methods=["POST"])
def delete_expense(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
