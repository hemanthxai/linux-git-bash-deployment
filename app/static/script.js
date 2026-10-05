const currency = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
});


function money(value) {
    return currency.format(value);
}


async function loadDashboard() {

    try {

        const response =
            await fetch("/api/dashboard");

        const data =
            await response.json();


        document.getElementById("income").textContent =
            money(data.income);

        document.getElementById("savingsGoal").textContent =
            money(data.savings_goal);

        document.getElementById("spendingLimit").textContent =
            money(data.spending_limit);

        document.getElementById("totalSpent").textContent =
            money(data.total_spent);

        document.getElementById("remaining").textContent =
            money(data.remaining_budget);

        document.getElementById("expected").textContent =
            money(data.expected_spending);

        document.getElementById("projectedSpending").textContent =
            money(data.projected_monthly_spending);

        document.getElementById("projectedSavings").textContent =
            money(data.projected_savings);


        document.getElementById("budgetPercent").textContent =
            data.budget_used_percent + "%";

        document.getElementById("monthPercent").textContent =
            data.month_elapsed_percent + "%";


        document.getElementById("budgetProgress").style.width =
            Math.min(
                data.budget_used_percent,
                100
            ) + "%";


        document.getElementById("monthProgress").style.width =
            data.month_elapsed_percent + "%";


        updateAlert(data);

    } catch (error) {

        console.error(error);

        const alertBox =
            document.getElementById("alertBox");

        alertBox.textContent =
            "Unable to load dashboard.";

        alertBox.className =
            "alert danger";
    }
}


function updateAlert(data) {

    const alertBox =
        document.getElementById("alertBox");

    alertBox.textContent =
        data.alert;

    alertBox.className = "alert";


    if (
        data.status === "WARNING" ||
        data.status === "SPENDING_FAST"
    ) {

        alertBox.classList.add("warning");

    } else if (
        data.status === "CRITICAL" ||
        data.status === "HIGH_RISK"
    ) {

        alertBox.classList.add("critical");

    } else if (
        data.status === "OVER_BUDGET"
    ) {

        alertBox.classList.add("danger");
    }
}


async function loadExpenses() {

    const response =
        await fetch("/api/expenses");

    const data =
        await response.json();

    const table =
        document.getElementById("expenseTable");

    table.innerHTML = "";


    data.expenses
        .slice()
        .reverse()
        .forEach(expense => {

            const row =
                document.createElement("tr");

            row.innerHTML = `
                <td>${expense.date}</td>
                <td>${expense.category}</td>
                <td>${expense.description}</td>
                <td>${money(expense.amount)}</td>
            `;

            table.appendChild(row);
        });
}


document
    .getElementById("expenseForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();


        const amount =
            parseFloat(
                document.getElementById("amount").value
            );

        const category =
            document.getElementById("category").value;

        const description =
            document.getElementById("description").value;


        const response =
            await fetch("/api/expenses", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    amount,
                    category,
                    description
                })
            });


        const result =
            await response.json();


        if (!response.ok) {

            alert(result.error);
            return;
        }


        document
            .getElementById("expenseForm")
            .reset();


        await loadDashboard();
        await loadExpenses();
    });


document
    .getElementById("budgetForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();


        const income =
            parseFloat(
                document.getElementById("incomeInput").value
            );

        const savings_goal =
            parseFloat(
                document.getElementById("savingsInput").value
            );

        const spending_limit =
            parseFloat(
                document.getElementById("limitInput").value
            );


        const response =
            await fetch("/api/budget", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    income,
                    savings_goal,
                    spending_limit
                })
            });


        const result =
            await response.json();


        if (!response.ok) {

            alert(result.error);
            return;
        }


        alert("Budget updated successfully.");

        await loadDashboard();
    });


loadDashboard();
loadExpenses();