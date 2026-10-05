from flask import Flask, jsonify, request, render_template
from datetime import date
import calendar
import json
import os

app = Flask(__name__)

VERSION = "1.0.0"

DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    "data",
    "budget.json"
)


def load_data():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def calculate_dashboard(data):
    today = date.today()

    days_in_month = calendar.monthrange(
        today.year,
        today.month
    )[1]

    day_of_month = today.day

    month_progress = (
        day_of_month / days_in_month
    ) * 100

    total_spent = sum(
        expense["amount"]
        for expense in data["expenses"]
    )

    spending_limit = data["spending_limit"]

    if spending_limit > 0:
        budget_used = (
            total_spent / spending_limit
        ) * 100
    else:
        budget_used = 0

    remaining_budget = spending_limit - total_spent

    expected_spending = (
        spending_limit * month_progress
    ) / 100

    spending_difference = (
        total_spent - expected_spending
    )

    # Determine spending status
    if budget_used >= 100:
        status = "OVER_BUDGET"
        alert = "🚨 VERY HIGH ALERT: You have exceeded your monthly spending limit."

    elif budget_used >= 90:
        status = "CRITICAL"
        alert = "🚨 CRITICAL: You are very close to your monthly spending limit."

    elif budget_used >= 70:
        if budget_used > month_progress + 15:
            status = "HIGH_RISK"
            alert = "⚠️ WARNING: You are spending much faster than planned."
        else:
            status = "WARNING"
            alert = "⚠️ WARNING: You have crossed 70% of your spending budget."

    elif budget_used > month_progress + 15:
        status = "SPENDING_FAST"
        alert = "⚠️ Your spending is ahead of the expected monthly pace."

    else:
        status = "ON_TRACK"
        alert = "✅ Your spending is currently on track."

    # Project spending for the entire month
    if day_of_month > 0:
        projected_spending = (
            total_spent / day_of_month
        ) * days_in_month
    else:
        projected_spending = 0

    projected_savings = (
        data["income"] - projected_spending
    )

    savings_progress = 0

    if data["savings_goal"] > 0:
        savings_progress = (
            projected_savings /
            data["savings_goal"]
        ) * 100

    return {
        "date": today.isoformat(),
        "month": today.strftime("%B %Y"),

        "days_in_month": days_in_month,
        "day_of_month": day_of_month,

        "income": data["income"],
        "savings_goal": data["savings_goal"],
        "spending_limit": spending_limit,

        "total_spent": round(total_spent, 2),
        "remaining_budget": round(
            remaining_budget,
            2
        ),

        "budget_used_percent": round(
            budget_used,
            2
        ),

        "month_elapsed_percent": round(
            month_progress,
            2
        ),

        "expected_spending": round(
            expected_spending,
            2
        ),

        "spending_difference": round(
            spending_difference,
            2
        ),

        "projected_monthly_spending": round(
            projected_spending,
            2
        ),

        "projected_savings": round(
            projected_savings,
            2
        ),

        "savings_progress": round(
            savings_progress,
            2
        ),

        "status": status,
        "alert": alert
    }


# -----------------------------
# UI
# -----------------------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        version=VERSION
    )


# -----------------------------
# Health Check
# -----------------------------

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "BudgetGuard",
        "version": VERSION
    }), 200


# -----------------------------
# Budget API
# -----------------------------

@app.route("/api/budget", methods=["GET"])
def get_budget():

    data = load_data()

    return jsonify({
        "income": data["income"],
        "savings_goal": data["savings_goal"],
        "spending_limit": data["spending_limit"]
    })


@app.route("/api/budget", methods=["POST"])
def set_budget():

    data = request.get_json()

    required_fields = [
        "income",
        "savings_goal",
        "spending_limit"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    income = float(data["income"])
    savings_goal = float(data["savings_goal"])
    spending_limit = float(data["spending_limit"])

    if income <= 0:

        return jsonify({
            "error": "Income must be greater than zero"
        }), 400

    if savings_goal < 0:

        return jsonify({
            "error": "Savings goal cannot be negative"
        }), 400

    if spending_limit < 0:

        return jsonify({
            "error": "Spending limit cannot be negative"
        }), 400

    if savings_goal + spending_limit > income:

        return jsonify({
            "error": "Savings goal and spending limit cannot exceed income"
        }), 400

    budget = load_data()

    budget["income"] = income
    budget["savings_goal"] = savings_goal
    budget["spending_limit"] = spending_limit

    save_data(budget)

    return jsonify({
        "message": "Budget updated successfully"
    })


# -----------------------------
# Expenses API
# -----------------------------

@app.route("/api/expenses", methods=["GET"])
def get_expenses():

    data = load_data()

    return jsonify({
        "expenses": data["expenses"],
        "total_expenses": round(
            sum(
                expense["amount"]
                for expense in data["expenses"]
            ),
            2
        )
    })


@app.route("/api/expenses", methods=["POST"])
def add_expense():

    expense = request.get_json()

    required_fields = [
        "amount",
        "category",
        "description"
    ]

    for field in required_fields:

        if field not in expense:

            return jsonify({
                "error": f"{field} is required"
            }), 400

    amount = float(expense["amount"])

    if amount <= 0:

        return jsonify({
            "error": "Amount must be greater than zero"
        }), 400

    data = load_data()

    new_expense = {
        "date": expense.get(
            "date",
            date.today().isoformat()
        ),

        "amount": amount,

        "category": expense["category"],

        "description": expense["description"]
    }

    data["expenses"].append(
        new_expense
    )

    save_data(data)

    return jsonify({
        "message": "Expense added successfully",
        "expense": new_expense
    }), 201


# -----------------------------
# Dashboard API
# -----------------------------

@app.route("/api/dashboard")
def dashboard():

    data = load_data()

    return jsonify(
        calculate_dashboard(data)
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )