from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import json
import os
from datetime import date

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "expenses.json")

DAILY_LIMIT = 1500


def load_expenses():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_expenses(expenses):
    with open(DATA_FILE, "w") as file:
        json.dump(expenses, file, indent=4)

# HOME / TEST ROUTE

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/expenses", methods=["GET"])
def get_expenses():

    expenses = load_expenses()

    return jsonify(expenses)

# ADD NEW EXPENSE

@app.route("/api/expenses", methods=["POST"])
def add_expense():

    data = request.get_json()

    # Check whether data was received
    if not data:
        return jsonify({
            "error": "No data received"
        }), 400

    # Get values from frontend
    name = data.get("name")
    amount = data.get("amount")
    category = data.get("category")

    # Validate name
    if not name:
        return jsonify({
            "error": "Expense name is required"
        }), 400

    # Validate amount
    if amount is None:
        return jsonify({
            "error": "Amount is required"
        }), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({
            "error": "Amount must be a number"
        }), 400

    if amount <= 0:
        return jsonify({
            "error": "Amount must be greater than 0"
        }), 400

    # Validate category
    if not category:
        return jsonify({
            "error": "Category is required"
        }), 400

    # Load existing expenses
    expenses = load_expenses()

    # Create new expense
    new_expense = {
        "date": str(date.today()),
        "name": name,
        "category": category,
        "amount": amount
    }

    # Add new expense to list
    expenses.append(new_expense)

    # Save updated list to JSON
    save_expenses(expenses)

    return jsonify({
        "message": "Expense added successfully!",
        "expense": new_expense
    }), 201


# TODAY'S EXPENSES

@app.route("/api/expenses/today", methods=["GET"])
def today_expenses():

    expenses = load_expenses()

    today = str(date.today())

    today_list = []

    for expense in expenses:

        if expense["date"] == today:
            today_list.append(expense)

    total_today = 0

    for expense in today_list:
        total_today += expense["amount"]

    return jsonify({
        "date": today,
        "expenses": today_list,
        "total": total_today
    })



# DASHBOARD
@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    expenses = load_expenses()

    # If there are no expenses
    if len(expenses) == 0:
        return jsonify({
            "total": 0,
            "today": 0,
            "highest": 0,
            "average": 0,
            "count": 0,
            "high_spending": False,
            "message": "No expenses available."
        })

    # Variables
    total = 0
    highest = 0
    today_total = 0

    today = str(date.today())

    # Go through every expense
    for expense in expenses:

        amount = expense["amount"]

        # Calculate total
        total += amount

        # Find highest expense
        if amount > highest:
            highest = amount

        # Calculate today's spending
        if expense["date"] == today:
            today_total += amount

    # Number of expenses
    count = len(expenses)

    # Average expense
    average = total / count

    # Check spending limit
    if today_total > DAILY_LIMIT:

        high_spending = True

        message = (
            f"High Spending Alert! "
            f"You have spent ₹{today_total:.2f} today. "
            f"Try to reduce your spending and save more."
        )

    else:

        high_spending = False

        message = (
            "Your spending is under control! "
            "Keep going and continue saving."
        )

    return jsonify({
        "total": total,
        "today": today_total,
        "highest": highest,
        "average": round(average, 2),
        "count": count,
        "daily_limit": DAILY_LIMIT,
        "high_spending": high_spending,
        "message": message
    })

# RUN FLASK SERVER
if __name__ == "__main__":
    app.run(debug=True)