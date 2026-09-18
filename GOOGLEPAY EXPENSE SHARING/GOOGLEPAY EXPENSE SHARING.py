import numpy as np
from prettytable import PrettyTable
from datetime import datetime           #datetime liabrary for transaction history

friends = ("Prashna", "Dhanshik", "Kamalesh", "Ragul")
expense_matrix = np.zeros((len(friends), len(friends)))
transaction_history = [] #Track and Record the expenses

def add_expense(payer, beneficiaries, amount, split_type="equal", custom_splits=None, description=""):
    payer_idx = friends.index(payer)

    if split_type == "equal":
        share_per_person = amount / len(beneficiaries)
        shares = {b: share_per_person for b in beneficiaries}

    elif split_type == "custom":
        if custom_splits is None:
            raise ValueError("Custom splits cannot be None")
        total_custom = sum(custom_splits.values())
        if abs(total_custom - amount) > 1e-6:
            raise ValueError(f"custom total split ({total_custom}) cannot be equal to amount ({amount})")
        shares = custom_splits

    else:
        raise ValueError("split_type must be equal to 'equal' or 'custom'")

 # update matrix
    for beneficiary, share in shares.items():
        beneficiary_idx = friends.index(beneficiary)
        expense_matrix[payer_idx, beneficiary_idx] += share

    # transaction history
    transaction_history.append({
        "timestamp": datetime.now().strftime("%d-%m-%Y"),
        "payer": payer,
        "amount": amount,
        "split_type": split_type,
        "shares": shares,
        "description": description
    })

def view_history(user=None):
    table = PrettyTable()
    table.field_names = ["date", "payer", "amount", "split", "description", "your share"]

    found = False
    for txn in transaction_history:
        if user is None:
            # show everything, "Your Share" column not relevant here
            for name, share in txn["shares"].items():
                table.add_row([
                    txn["timestamp"], txn["payer"], f"₹{txn['amount']:.2f}",
                    txn["split_type"], txn["description"], f"{name}: ₹{share:.2f}"
                ])
                found = True

        else:
            if user == txn["payer"] or user in txn["shares"]:
                your_share = txn["shares"].get(user, 0)
                role = "paid" if user == txn["payer"] else "owes share"
                table.add_row([
                    txn["timestamp"], txn["payer"], f"₹{txn['amount']:.2f}",
                    txn["split_type"], txn["description"], f"{role}: ₹{your_share:.2f}"
                ])
                found = True

    print(f"\nTransaction history{' for ' + user if user else ''}:")
    if found:
        print(table)
    else:
        print("No transaction history")

def calculate_settlements():
    total_paid = np.sum(expense_matrix, axis=1)
    total_owes = np.sum(expense_matrix, axis=0)
    net_balance = total_paid - total_owes
    return net_balance

def display_settlements():
    settlements = calculate_settlements()
    table = PrettyTable()
    table.field_names = ["friend", "settlement"]
    for i, friend in enumerate(friends):
        if settlements[i] > 0:
            table.add_row([friend, f"should receive ₹{settlements[i]:.2f}"])
        elif settlements[i] < 0:
            table.add_row([friend, f"owes ₹{-settlements[i]:.2f}"])
        else:
            table.add_row([friend, "is settled"])
    print("\nFinal settlement:")
    print(table)

def suggest_payments():
    settlements = calculate_settlements()
    creditors = [(friends[i], amt) for i, amt in enumerate(settlements) if amt > 0]
    debtors = [(friends[i], -amt) for i, amt in enumerate(settlements) if amt < 0]
    transactions = []
    while debtors and creditors:
        debtor, debt_amount = debtors.pop(0)
        creditor, credit_amount = creditors.pop(0)
        payment = min(debt_amount, credit_amount)
        transactions.append((debtor, creditor, payment))
        debt_amount -= payment
        credit_amount -= payment
        if debt_amount > 1e-9:
            debtors.insert(0, (debtor, debt_amount))
        if credit_amount > 1e-9:
            creditors.insert(0, (creditor, credit_amount))
    print("\nSuggested transactions:")
    if transactions:
        for debtor, creditor, amount in transactions:
            print(f"{debtor} should pay ₹{amount:.2f} to {creditor}")
    else:
        print("everyone settled")


if __name__ == "__main__":
    # Equal split example
    add_expense("Prashna", ["Prashna", "Dhanshik", "Kamalesh", "Ragul"], 800, split_type="equal", description="Dinner")

    # Custom split example
    add_expense("Dhanshik", ["Prashna", "Dhanshik"], 500, split_type="custom",
                custom_splits={"Prashna": 300, "Dhanshik": 200}, description="Cab fare")

    add_expense("Kamalesh", ["Kamalesh", "Ragul"], 300, split_type="equal", description="Groceries")

    display_settlements()
    suggest_payments()

    # transaction history
    view_history()
    view_history("Kamalesh")