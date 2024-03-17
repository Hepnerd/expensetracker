import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv
import sys, os
import datetime
import re
import pandas as pd

def read_bank_csv_file(file_path):
    """
    Reads a CSV file and returns its data as a list of dictionaries.
    Each dictionary represents a row, with keys corresponding to column names.
    """
    data = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            data.append(row)
    return data

def remove_duplicates_from_final(output_filename):
    location = "output/"
    toclean = pd.read_csv(output_filename)
    deduped = toclean.drop_duplicates(['Date','Transaction','Description','transactionType'])
    deduped.to_csv(location + "transactions.csv", index=False)

def process_bank_csv_files(output_filename):
    """
    Processes all CSV files in the specified directory.
    Assumes that each file ends with 'transactions.csv'.
    """
    transactionFile = filedialog.askopenfilename(title="Open CSV File", filetypes=[("CSV files", "*.csv")])
    filename = os.path.basename(transactionFile)
    data = read_bank_csv_file(transactionFile)
    transactionArray = []
    
    # Manually assign fields based on file-specific logic
    for row in data:
        transactionDate = ""
        description = ""
        transaction = 0
        category = ""
        bank = ""
        transactionType = ""
        # Example: Assigning 'amount' field based on file name
        if 'pnc' in filename.lower():
            if row['Date'] != '':
                date = datetime.datetime.strptime(row['Date'], '%m/%d/%Y').strftime('%m/%d/%Y')
            else:
                date = ''
            transactionDate = date
            description = row['Description'].replace(",", "").replace(";", "").replace(":", "")
            transaction =+ abs(float(row['Withdrawals'].replace("$", "").replace(",", "") or 0))
            transaction += abs(float(row['Deposits'].replace("$", "").replace(",", "") or 0))
            if row['Withdrawals'] == '':
                transactionType = 'debit'
            else:
                transactionType = 'credit'
            category = row['Category']
            bank = 'PNC'
        elif 'key' in filename.lower():
            if row['Date'] != '' and "/" in row['Date'] and row['Date'] != 'Date':
                date = datetime.datetime.strptime(row['Date'], '%m/%d/%Y').strftime('%m/%d/%Y')
            else:
                date = ''
            transactionDate = date
            match = re.search('^[\d]+', row['Amount'])
            if not match:
                continue
            transaction = abs(float(row['Amount'] or 0))
            if float(row['Amount'] or 0) < 0:
                transactionType = 'credit'
            else:
                transactionType = 'debit'
            description = row['Description'].replace(",", "").replace(";", "").replace(":", "")
            category = row['Category']
            bank = 'KEYBANK'
        elif 'ally' in filename.lower():
            if row['Date'] != '':
                date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d').strftime('%m/%d/%Y')
            else:
                date = ''
            transactionDate = date
            transaction = abs(float(row['Amount']))
            category = row['Category']
            description = row['Description'].replace(",", "").replace(";", "").replace(":", "")
            bank = 'ALLY'
            if row['Type'] == 'Withdrawal':
                transactionType = 'credit'
            elif row['Type'] == 'Deposit':
                transactionType = 'debit'
        elif 'mint' in filename.lower():
            if row['Date'] != '':
                date = datetime.datetime.strptime(row['Date'], '%m/%d/%Y').strftime('%m/%d/%Y')
            else:
                date = ''
            transactionDate = date
            description = row['Description'].replace(",", "").replace(";", "").replace(":", "")
            transaction = abs(float(row['Amount']))
            transactionType = row['Transaction Type']
            category = row['Category']
            bank = 'MINT'

        # Add the filename as a prefix to each field
        # for key in row:
        #     bank = f"{filename.split('_')[0]}"
        
        transactionArray.insert(1, "{0},{1},{2},{3},{4},{5}".format(bank,transactionDate,transaction,description,category,transactionType))
    # Remove duplicates
    transactionArray = list(set(transactionArray))
    
    # Write the processed data to a new CSV file
    with open(output_filename, 'a+', newline='') as outfile:
        writer = csv.writer(outfile)
        for item in transactionArray:
            splititem = item.split(",")
            writer.writerow([[splititem[0]], [splititem[1]], splititem[2], splititem[3], splititem[4], splititem[5]])
    print(f"Processed data (without duplicates) written to {output_filename}")

# Function to sort the Treeview by column
def sort_treeview(tree, col, descending):
    data = [(tree.set(item, col), item) for item in tree.get_children('')]
    data.sort(reverse=descending)
    for index, (val, item) in enumerate(data):
        tree.move(item, '', index)
    tree.heading(col, command=lambda: sort_treeview(tree, col, not descending))

def transactionFileIntoList(fileName):
    try:
        with open(fileName, 'r', newline='') as f:
            reader = csv.reader(f)
            data = [tuple(row) for row in reader]
        return data
    except Exception as e:
        print("Ah dang")

def insert_transactions():
    output_filename = "output/transactions.csv"
    process_bank_csv_files(output_filename)
    remove_duplicates_from_final(output_filename)

def create_transactions_file_if_not_exist(output_filename):
    fields = ['Bank', 'Date', 'Transaction', 'Description', 'Category', 'transactionType']
    file_exists = os.path.isfile(output_filename)
    if not file_exists:
        with open(output_filename, 'w', newline='') as outfile:
                        writer = csv.writer(outfile)
                        writer.writerow(fields)

def new_iterable_list(transaction_PATH):
    global transactionList
    transactionList = iter(transactionFileIntoList(TRANSACTION_PATH))

TRANSACTION_PATH = "output/transactions.csv"

create_transactions_file_if_not_exist(TRANSACTION_PATH)

transactionList = iter(transactionFileIntoList(TRANSACTION_PATH))
# transactionIterable = iter(transactionList)

root = tk.Tk()
root.title("Hepnerd Transaction Viewer")

style = ttk.Style(root)
root.tk.call("source", "forest-light.tcl")
root.tk.call("source", "forest-dark.tcl")
style.theme_use("forest-dark")

root.geometry("1600x600")

#TODO: 
# Auto refresh table
# Filter by fields
# Edit data
# Insert data
# Tabs for income, debt, etc
# Custom dashboard - sql queries to build graphs
# Custom import rules
# Settings saved in CSV
# Budget tracker

insert_data = tk.Button(root, text="Insert transactions", command=insert_transactions)
insert_data.pack(padx=20, pady=10)

filter_dropdown = tk.Label(root, text="Filter Dropdown Here", padx=20, pady=10)
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

verscrlbar = ttk.Scrollbar(tree, orient ="vertical", command = tree.yview)

# Calling pack method w.r.to vertical 
# scrollbar
verscrlbar.pack(side ='right', fill ='y')
 
# Configuring treeview
tree.configure(yscrollcommand = verscrlbar.set)


root.mainloop()
