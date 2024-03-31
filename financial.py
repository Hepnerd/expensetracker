import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
import csv
import os
import datetime
import re
import pandas as pd

def read_bank_csv_file(file_path):
    """
    Reads a CSV file and returns its data as a list of dictionaries.
    Each dictionary represents a row, with keys corresponding to column names.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            data.append(row)
    return data

def remove_duplicates_from_final(output_filename):
    location = "database/"
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
            bank = "PNC"
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
            bank = "KEYBANK"
        elif 'ally' in filename.lower():
            if row['Date'] != '':
                date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d').strftime('%m/%d/%Y')
            else:
                date = ''
            transactionDate = date
            transaction = abs(float(row['Amount']))
            category = row['Category']
            description = row['Description'].replace(",", "").replace(";", "").replace(":", "")
            bank = "ALLY"
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
            bank = "MINT"
        
        transactionArray.insert(1, "{0},{1},{2},{3},{4},{5}".format(bank,transactionDate,transaction,description,category,transactionType))
        transactionFiller = {'Bank': bank, 'Date': transactionDate, 'Transaction': str(transaction), 'Description': description, 'Category': category, 'transactionType': transactionType}
        if transactionFiller not in transactionReference:
            transactionReference.insert(0, transactionFiller)
    # Remove duplicates
    transactionArray = list(set(transactionArray))
    
    # Write the processed data to a new CSV file
    with open(output_filename, 'a+', newline='', encoding='utf-8-sig') as outfile:
        writer = csv.writer(outfile)
        for item in transactionArray:
            splititem = item.split(",")
            writer.writerow([splititem[0], splititem[1], splititem[2], splititem[3], splititem[4], splititem[5]])
    refreshTransactionTable(transactionReference, None, None, None)

# Function to sort the Treeview by column
def sort_treeview(tree, col, descending):
    data = [(tree.set(item, col), item) for item in tree.get_children('')]
    data.sort(reverse=descending)
    for index, (val, item) in enumerate(data):
        tree.move(item, '', index)
    tree.heading(col, command=lambda: sort_treeview(tree, col, not descending))

def transactionFileIntoList(fileName):
    try:
        with open(fileName, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=',')
            next(reader, None)
            data = list(reader)
        return data
    except Exception as e:
        print("Ah dang")

def insert_transactions():
    try:
        output_filename = "database/transactions.csv"
        process_bank_csv_files(output_filename)
        remove_duplicates_from_final(output_filename)
    except TypeError:
        pass

def create_transactions_file_if_not_exist(output_filename):
    fields = ['Bank', 'Date', 'Transaction', 'Description', 'Category', 'transactionType']
    file_exists = os.path.isfile(output_filename)
    if not file_exists:
        with open(output_filename, 'w', newline='', encoding='utf-8-sig') as outfile:
                        writer = csv.writer(outfile)
                        writer.writerow(fields)

def extractFirstFromList(lst):
    if len(lst) == 0:
        return ""
    else:
        return [item['Bank'] for item in lst]

def extractSecondFromList(lst):
    if len(lst) == 0:
        return ""
    else:
        return [item['Category'] for item in lst]

def refreshTransactionTable(transactionList, bankFilter, dateFilter, categoryFilter):
    print("Table Refreshed")
    # Figure out how to update and not create a new one
    # listCount = ttk.Label(treeFrame, text="Number of Records:\t" + str(len(transactionList)))
    # listCount.pack()
    header = ("Bank", "Date", "Transaction", "Description", "Category", "Transaction Type")
    tree.delete(*tree.get_children())  # Clear the current data
    for i in tree.get_children():
        tree.delete(i)

    tree["columns"] = header
    for col in header:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c, False))
        tree.column(col, width=200)

    # print("categoryFilter: " + str(categoryFilter))
    # print("dateFilter: " + str(dateFilter))
    # print("bankFilter: " + str(bankFilter))
    if bankFilter == "All":
        bankFilter = ""
    if (categoryFilter is None or categoryFilter == "") and (dateFilter is None or dateFilter == "") and (bankFilter is None or bankFilter == ""):
        for row in transactionList:
            Bank = row['Bank']
            Date = row['Date']
            Transaction = row['Transaction']
            Description = row['Description']
            Category = row['Category']
            transactionType = row['transactionType']
            tree.insert("", "end", values=(Bank, Date, Transaction, Description, Category, transactionType))
            tree.bind("<<TreeviewSelect>>", selectItem)
    else:
        if categoryFilter != "" and bankFilter == "":
            for row in transactionList:
                if categoryFilter == row['Category']:
                    Bank = row['Bank']
                    Date = row['Date']
                    Transaction = row['Transaction']
                    Description = row['Description']
                    Category = row['Category']
                    transactionType = row['transactionType']
                    tree.insert("", "end", values=(Bank, Date, Transaction, Description, Category, transactionType))
                    tree.bind("<<TreeviewSelect>>", selectItem)
        elif categoryFilter == "" and bankFilter != "":
            for row in transactionList:
                if bankFilter == row['Bank']:
                    Bank = row['Bank']
                    Date = row['Date']
                    Transaction = row['Transaction']
                    Description = row['Description']
                    Category = row['Category']
                    transactionType = row['transactionType']
                    tree.insert("", "end", values=(Bank, Date, Transaction, Description, Category, transactionType))
                    tree.bind("<<TreeviewSelect>>", selectItem)
        elif categoryFilter != "" and bankFilter != "":
            for row in transactionList:
                if bankFilter == row['Bank']:
                    if categoryFilter == row['Category']:
                        Bank = row['Bank']
                        Date = row['Date']
                        Transaction = row['Transaction']
                        Description = row['Description']
                        Category = row['Category']
                        transactionType = row['transactionType']
                        tree.insert("", "end", values=(Bank, Date, Transaction, Description, Category, transactionType))
                        tree.bind("<<TreeviewSelect>>", selectItem)

def refreshTransactionEdit(bank, date, transactionAmount, description, category, transactionType):
    # print(bank_combo_list, date, transactionAmount, description, category, transactionType)
    if bank is None:
        status_combobox = ttk.Combobox(transactionEdit, values=bank_combo_list)
        status_combobox.insert(0, "Bank")
    else:
        bank_entry_edit_index = bank_combo_list.index(bank)
        status_combobox = ttk.Combobox(transactionEdit, values=bank_combo_list)
        status_combobox.current(bank_entry_edit_index)

    file_exists = os.path.isfile(TRANSACTION_PATH)
    if not file_exists:
        status_combobox.current(0)
    status_combobox.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

    date_entry = ttk.Entry(transactionEdit)
    date_entry.insert(0, date)
    # date_entry.bind("<FocusIn>", lambda e: date_entry.delete('0', 'end'))
    date_entry.grid(row=1, column=0, padx=5, pady=10, sticky="ew")

    transaction_entry = ttk.Entry(transactionEdit)
    transaction_entry.insert(0, transactionAmount)
    # transaction_entry.bind("<FocusIn>", lambda e: transaction_entry.delete('0', 'end'))
    transaction_entry.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

    description_entry = tk.Text(transactionEdit, width=1, height=4)
    description_entry.insert(INSERT, description)
    # description_entry.bind("<FocusIn>", lambda e: description_entry.delete('0', 'end'))
    description_entry.grid(row=3, column=0, padx=5, pady=10, sticky="ew")

    if category != "Category":
        category_entry_edit_index = category_combo_list.index(category)
    else:
        category_entry_edit_index = 0
    category_entry = ttk.Combobox(transactionEdit, values=category_combo_list)
    # category_entry.insert(0, category)
    if len(category_combo_list) != 0:
        category_entry.current(category_entry_edit_index)
    # category_entry.bind("<FocusIn>", lambda e: category_entry.delete('0', 'end'))
    category_entry.grid(row=4, column=0, padx=5, pady=10, sticky="ew")

    transactionType_list = ("credit", "debit")
    if (transactionType == "credit"):
        transactionTypeNumeric = 0
    else:
        transactionTypeNumeric = 1

    # transactionType_entry = ttk.Combobox(transactionEdit, values=transactionType_list)
    transactionType_entry = ttk.Combobox(transactionEdit, state= "readonly", values=transactionType_list)
    # transactionType_entry.insert(0, transactionType)
    transactionType_entry.current(transactionTypeNumeric)
    # transactionType_entry.bind("<FocusIn>", lambda e: transactionType_entry.delete('0', 'end'))
    transactionType_entry.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

    seperator = ttk.Separator(transactionEdit)
    seperator.grid(row=6, column=0, padx=5, pady=5, sticky="nsew")

    editConfirm_button = ttk.Button(transactionEdit, text="Update Transaction", command=lambda: updateTransaction(status_combobox.get(), date_entry.get(), transaction_entry.get(), description_entry.get('1.0', 'end-1c'), category_entry.get(), transactionType_entry.get()))
    editConfirm_button.grid(row=7, column=0, padx=5, pady=5, sticky="nsew")

    DeleteConfirm_button = ttk.Button(transactionEdit, text="Delete Transaction", command=lambda: deleteTransaction(status_combobox.get(), date_entry.get(), transaction_entry.get(), description_entry.get('1.0', 'end-1c'), category_entry.get(), transactionType_entry.get()))
    DeleteConfirm_button.grid(row=8, column=0, padx=5, pady=5, sticky="nsew")

    CreateConfirm_button = ttk.Button(transactionEdit, text="Create Transaction", command=lambda: createTransaction(status_combobox.get(), date_entry.get(), transaction_entry.get(), description_entry.get('1.0', 'end-1c'), category_entry.get(), transactionType_entry.get()))
    CreateConfirm_button.grid(row=9, column=0, padx=5, pady=5, sticky="nsew")

def selectItem(a):
    try:
        curItem = tree.focus()
        # print(tree.item(curItem)['values'])
        selectedTransactionList = list(tree.item(curItem)['values'])
        Bank = selectedTransactionList[0]
        Date = selectedTransactionList[1]
        Transaction = selectedTransactionList[2]
        Description = selectedTransactionList[3]
        Category = selectedTransactionList[4]
        transactionType = selectedTransactionList[5]
        # print(Bank, Date, Transaction, Description, Category, transactionType)
        refreshTransactionEdit(Bank, Date, "$" + Transaction, Description, Category, transactionType)
    except IndexError:
        pass

# Update/Create/Delete from file and list. Then refresh table without having to reread file.
def updateTransaction(Bank, Date, Transaction, Description, Category, TransactionType):
    newLinePrint = ','.join([Bank, Date, Transaction.replace('$', ''), Description, Category, TransactionType])
    print(newLinePrint)

def deleteTransaction(Bank, Date, Transaction, Description, Category, TransactionType):
    print(Bank, Date, Transaction.replace('$', ''), Description, Category, TransactionType + " deleted")
    # df = pd.read(csv(TRANSACTION_PATH))
    # df = df.drop(df[df.Bank == Bank, df.Date == Date, df.Transaction == Transaction.replace('$', ''), df.Category == Category, df.transactionType == TransactionType].index)
    # df.to_csv(TRANSACTION_PATH, index=FALSE)
    print(transactionReference[1])    

def createTransaction(Bank, Date, Transaction, Description, Category, TransactionType):
    newLinePrint = ','.join([Bank, Date, Transaction.replace('$', ''), Description, Category, TransactionType])
    print(newLinePrint + " deleted")
    transactionFiller = {'Bank': Bank, 'Date': Date, 'Transaction': Transaction.replace('$', ''), 'Description': Description, 'Category': Category, 'transactionType': TransactionType}
    if transactionFiller not in transactionReference:
            transactionReference.insert(0, transactionFiller)
    transactionFileWrite = open(TRANSACTION_PATH, "a", encoding='utf-8-sig')  # Add to end of file
    transactionFileWrite.write(newLinePrint)
    transactionFileWrite.close()
    refreshTransactionTable(transactionReference, bank_filter_dropdown.get(), date_filter_dropdown.get(), category_filter_dropdown.get())
    if Bank not in bank_combo_list:
        bank_combo_list.append(Bank)
    if Category not in category_combo_list:
        category_combo_list.append(Category)


TRANSACTION_PATH = "database/transactions.csv"

create_transactions_file_if_not_exist(TRANSACTION_PATH)

transactionReference = transactionFileIntoList(TRANSACTION_PATH)

root = tk.Tk()
transactions = ttk.Frame(root)
transactions.pack()

dashboard = ttk.Frame(root)
dashboard.pack()

income = ttk.Frame(root)
income.pack()

spending = ttk.Frame(root)
spending.pack()

budget = ttk.Frame(root)
budget.pack()

transactionsTable = ttk.Frame(transactions)
transactionsTable.grid(row=0, column=1, padx=10, pady=10)

transactionEdit = ttk.LabelFrame(transactions, text="Transaction Interact")
transactionEdit.grid(row=0, column=0, padx=10)

root.title("Hepnerd Transaction Viewer")

# style = ttk.Style(root)
# root.tk.call("source", "forest-light.tcl")
# root.tk.call("source", "forest-dark.tcl")
# style.theme_use("forest-dark")

root.geometry("1800x1000")
# root.attributes('-zoomed', True)

#TODO: 
# Auto refresh table
    # Only refresh a list so we aren't reading the file each time
# Edit data
# Insert data
# Tabs for income, debt, etc
# Custom dashboard - sql queries to build graphs
# Custom import rules
# Settings saved in CSV
# Budget tracker
# Fix counter label
# Bank dropdown in transaction Edit
# Date picker in transaction Edit
# Category dropdown in transaction Edit
# Todo date picker
# Delete button verification


bank_combo_list = sorted((list(set(extractFirstFromList(transactionReference)))))
filter_bank_combo_list = bank_combo_list.copy()
filter_bank_combo_list.insert(0,"All")
category_combo_list = sorted((list(set(extractSecondFromList(transactionReference)))))
date_combo_list = {"Placeholder Date Filter"}

refreshTransactionEdit(None, "Date (mm/dd/yyyy)", "Transaction Amount", "Description", "Category", "Transaction Type")

insert_data = tk.Button(transactionsTable, text="Insert transactions", command=insert_transactions)
insert_data.grid(row=0, column=0, padx=20, pady=10)

bank_filter_dropdown = ttk.Combobox(transactionsTable, state="readonly", values=filter_bank_combo_list)
bank_filter_dropdown.bind("<<ComboboxSelected>>", lambda event:refreshTransactionTable(transactionReference, bank_filter_dropdown.get(), date_filter_dropdown.get(), category_filter_dropdown.get()))
bank_filter_dropdown.grid(row=1, column=0, padx=20, pady=10)

date_filter_dropdown = ttk.Combobox(transactionsTable, state="readonly", values=date_combo_list)
# filter_dropdown.bind("<<ComboboxSelected>>", lambda event:testMethod(event, event.widget.get()))
# date_filter_dropdown.bind("<<ComboboxSelected>>", lambda event:refreshTransactionTable(transactionReference, bank_filter_dropdown.get(), date_filter_dropdown.get(), category_filter_dropdown.get()))
date_filter_dropdown.grid(row=2, column=0, padx=20, pady=10)

category_filter_dropdown = ttk.Combobox(transactionsTable, state="readonly", values=category_combo_list)
# filter_dropdown.bind("<<ComboboxSelected>>", lambda event:testMethod(event, event.widget.get()))
category_filter_dropdown.bind("<<ComboboxSelected>>", lambda event:refreshTransactionTable(transactionReference, bank_filter_dropdown.get(), date_filter_dropdown.get(), category_filter_dropdown.get()))
category_filter_dropdown.grid(row=3, column=0, padx=20, pady=10)

treeFrame = ttk.Frame(transactionsTable)
treeFrame.grid(row=4, column=0, padx=20, pady=20)

treeScroll = ttk.Scrollbar(treeFrame, orient ="vertical")
treeScroll.pack(side ='right', fill ='y')

tree = ttk.Treeview(treeFrame, show="headings", height=30, yscrollcommand=treeScroll.set)
tree.pack(fill="both", expand=True)

refreshTransactionTable(transactionReference, None, None, None)

treeScroll.config(command=tree.yview)
 
tree.configure(yscrollcommand = treeScroll.set)

root.mainloop()
