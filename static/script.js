
const budgetInput = document.getElementById("budget");
const findButton = document.getElementById("findButton");
const resetButton = document.getElementById("resetButton");

const selectedItems = document.getElementById("selectedItems");
const totalCost = document.getElementById("totalCost");
const remainingBudget = document.getElementById("remainingBudget");
const totalValue = document.getElementById("totalValue");
const errorMessage = document.getElementById("errorMessage");


function formatRupees(amount) {
    return "₹" + Number(amount).toLocaleString("en-IN");
}


function showResults(data) {
    selectedItems.replaceChildren();

    if (data.selected_items.length === 0) {
        selectedItems.textContent =
            "No items fit within your budget.";
    } else {
        data.selected_items.forEach(item => {
            const row = document.createElement("div");
            row.className = "selected-item";

            const name = document.createElement("span");
            name.textContent = item.name;

            const price = document.createElement("strong");
            price.textContent = formatRupees(item.price);

            row.append(name, price);
            selectedItems.appendChild(row);
        });
    }

    totalCost.textContent = formatRupees(data.total_cost);

    remainingBudget.textContent =
        formatRupees(data.remaining_budget);

    totalValue.textContent = data.total_value;
}


async function findSelection() {
    errorMessage.textContent = "";

    const rawBudget = budgetInput.value.trim();

    if (rawBudget === "") {
        errorMessage.textContent = "Please enter your budget.";
        return;
    }

    const budget = Number(rawBudget);

    if (
        !Number.isSafeInteger(budget) ||
        budget < 0 ||
        budget > 100000
    ) {
        errorMessage.textContent =
            "Enter a whole-number budget from ₹0 to ₹1,00,000.";
        return;
    }

    findButton.disabled = true;
    findButton.textContent = "Calculating...";

    try {
        const response = await fetch("/api/select", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ budget: budget })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to calculate.");
        }

        showResults(data);

    } catch (error) {
        errorMessage.textContent =
            error.message || "Could not connect to the server.";
    } finally {
        findButton.disabled = false;
        findButton.textContent = "Find Best Selection";
    }
}


function resetResults() {
    budgetInput.value = "2000";
    errorMessage.textContent = "";

    selectedItems.textContent =
        "Enter a budget and click Find Best Selection.";

    totalCost.textContent = "₹0";
    remainingBudget.textContent = "₹0";
    totalValue.textContent = "0";
}


findButton.addEventListener("click", findSelection);
resetButton.addEventListener("click", resetResults);

// Allow Enter to submit the budget
budgetInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        findSelection();
    }
});
