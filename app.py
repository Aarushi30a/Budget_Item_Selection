
from flask import Flask, render_template, request, jsonify
from db import get_items, save_selection

app = Flask(__name__)


# DAA: 0/1 Knapsack using Dynamic Programming
def select_items(budget, items):
    n = len(items)

    # dp[i][b] = maximum value using first i items
    # with a budget of b rupees
    dp = [[0] * (budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        item = items[i - 1]
        price = item["price"]
        value = item["value"]

        for b in range(budget + 1):
            # Option 1: Do not select the item
            dp[i][b] = dp[i - 1][b]

            # Option 2: Select the item if it fits
            if price <= b:
                new_value = value + dp[i - 1][b - price]
                dp[i][b] = max(dp[i][b], new_value)

    # Reconstruct the selected items
    selected = []
    b = budget

    for i in range(n, 0, -1):
        if dp[i][b] != dp[i - 1][b]:
            item = items[i - 1]
            selected.append(item)
            b -= item["price"]

    selected.reverse()

    total_cost = sum(item["price"] for item in selected)
    total_value = sum(item["value"] for item in selected)

    return {
        "selected_items": selected,
        "total_cost": total_cost,
        "remaining_budget": budget - total_cost,
        "total_value": total_value,
        "time_complexity": "O(n x B)",
        "space_complexity": "O(n x B)"
    }


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# API endpoint
@app.route("/api/select", methods=["POST"])
def calculate_selection():
    data = request.get_json(silent=True) or {}

    try:
        budget = data.get("budget")

        if isinstance(budget, bool):
            raise ValueError

        if isinstance(budget, int):
            pass
        elif isinstance(budget, str) and budget.strip().isdigit():
            budget = int(budget.strip())
        else:
            raise ValueError

        if budget < 0:
            return jsonify({
                "error": "Budget cannot be negative."
            }), 400

        if budget > 100000:
            return jsonify({
                "error": "Please enter a budget of Rs. 100000 or less."
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "error": "Please enter a valid whole-number budget."
        }), 400

    try:
        # Load current items from Oracle
        items = get_items()

        # Run the DAA algorithm
        result = select_items(budget, items)

        # Save the result through the PL/SQL procedure
        save_selection(
            budget,
            result["total_cost"],
            result["total_value"],
            result["selected_items"]
        )

        return jsonify(result)

    except Exception:
        app.logger.exception("Oracle budget selection failed")
        return jsonify({
            "error": (
                "Unable to retrieve items or save the selection. "
                "Check the Flask terminal for details."
            )
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
