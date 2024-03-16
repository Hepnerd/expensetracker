import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv
import sys, os

# Function to sort the Treeview by column
def sort_treeview(tree, col, descending):
    data = [(tree.set(item, col), item) for item in tree.get_children('')]
    data.sort(reverse=descending)
    for index, (val, item) in enumerate(data):
        tree.move(item, '', index)
    tree.heading(col, command=lambda: sort_treeview(tree, col, not descending))

def transactionFileIntoList(fileName):
    try:
        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            data = [tuple(row) for row in reader]
        return data
    except Exception as e:
        print("Ah dang")

TRANSACTION_PATH = "../formatTransactionCSV/output/transactions.csvfinal.csv"

transactionList = iter(transactionFileIntoList(TRANSACTION_PATH))
# transactionIterable = iter(transactionList)

root = tk.Tk()
root.title("Hepnerd Transaction Viewer")

root.geometry("1600x600")

#TODO: Insert data
#Insert button
#Choose files to insert
#insert_data = tk.Button(root, text="Insert transactions", command=insert_transactions)
#insert_data.pack(padx=20, pady=10)

filter_dropdown = tk.Label(root, text="Dropwdown", padx=20, pady=10)
filter_dropdown.pack()

tree = ttk.Treeview(root, show="headings")
tree.pack(padx=20, pady=20, fill="both", expand=True)

status_label = tk.Label(root, text="", padx=20, pady=10)
status_label.pack()

try:
        header = next(transactionList)  # Read the header row
        tree.delete(*tree.get_children())  # Clear the current data

        tree["columns"] = header
        for col in header:
            tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c, False))
            tree.column(col, width=200)

        for row in transactionList:
            tree.insert("", "end", values=row)

except Exception as e:
    status_label.config(text=f"Error: {str(e)}")

root.mainloop()

