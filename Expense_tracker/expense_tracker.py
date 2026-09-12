import json
from datetime import date

def load_expenses():
    try:
        with open ("expenses.json","r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
def save_expenses(expenses):
        with open("expenses.json","w") as file:
            json.dump(expenses,file,indent=4)
            
expenses = load_expenses()

def add_expense():
    name = input("enter expense name:")
    amount =float(input("enter the expense amount :"))
    category = input("enter the expense category ")
    
    expense ={
        "date" : str(date.today()),
        "name" : name,
        "amount" : amount,
        "category" : category
    }
    
    expenses.append(expense)
    save_expenses(expenses)
    print("Expense added successfully")
    
def today_spent():
    today = str(date.today())
    total = 0
    
    print("\n_____Today's Expenses_____")
    
    for expense in expenses:
        if expense["date"] == today:
            print(
                expense["name"],
                "-",
                expense["category"],
                "- ₹",
                expense["amount"]
            )
            total +=expense["amount"]
            
    print("Total spent today: ₹", total)
    
def history():
    print("\n_____Expense History_____")
    
    if len(expenses) == 0:
        print("No expenses recorded yet.")
        return
    
    for expense in expenses:
        print(
            expense["date"],
            "-",
            expense["name"],
            "-",
            expense["category"],
            "- ₹",
            expense["amount"]
        )

def dashboard():
    if len(expenses)==0:
        print("\n No expenses recorded yet.")
        return
    
    total = 0
    highest = 0
    today_total = 0
    
    today = str(date.today())
    
    for expense in expenses:
        amount = expense["amount"]
        
        total += amount
        
        if amount>highest:
            highest = amount
            
        if expense["date"]==today:
            today_total += amount
            
    count = len(expenses)
    average = total / count
    
    print("--------dashboard--------")
    print("total amount spent :",total)
    print("today total expense",today_total)
    print("highest expense :",highest)
    print("average amount :",round(average,2))
    print("nuber of expenses :",count)
    
    daily_limit = 1500
    
    if today_total > daily_limit:
        print("\n⚠️ high spending alert")
        print(f"you have spent ₹{today_total} today.")
        print("try to reduce your expenses")
    else:
        print("\n your total is under control")
        print("keep going and continue saving")
        
def main():
    while True:
        print("\n---------- EXPENSE TRACKER-----------")
        print("1. Dashboard")
        print("2. Add Expense")
        print("3. Today Spent")
        print("4. History")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            dashboard()

        elif choice == "2":
            add_expense()

        elif choice == "3":
            today_spent()

        elif choice == "4":
            history()

        elif choice == "5":
            print("Thank you for using Expense Tracker!")
            break

        else:
            print("Invalid choice. Please try again.")
            
main()