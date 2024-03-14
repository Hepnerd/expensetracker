# TODO
# Retrieve and update budget
# Retrieve and update fields
# Update records 

import os
import csv
import datetime
import re
import pandas as pd

def read_csv_file(file_path):
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

def remove_duplicates(data):
    """
    Removes duplicate rows from the data list.
    Assumes that each row is represented as a dictionary.
    """
    seen = set()
    unique_data = []
    for row in data:
        row_tuple = tuple(row.items())
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_data.append(row)
    return unique_data

def remove_duplicates_from_final(output_filename):
    toclean = pd.read_csv(output_filename)
    deduped = toclean.drop_duplicates(['Date','Transaction','Description','transactionType'])
    deduped.to_csv(output_filename + "final.csv")
    os.remove(output_filename)

def process_csv_files(directory_path, output_filename):
    """
    Processes all CSV files in the specified directory.
    Assumes that each file ends with 'transactions.csv'.
    """
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('transactions.csv'):
            file_path = os.path.join(directory_path, filename)
            data = read_csv_file(file_path)
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
            # unique_data = remove_duplicates(transactionArray)
            transactionArray = list(set(transactionArray))
            
            # Write the processed data to a new CSV file
            with open(output_filename, 'a+', newline='') as outfile:
                writer = csv.writer(outfile)
                for item in transactionArray:
                    splititem = item.split(",")
                    writer.writerow([[splititem[0]], [splititem[1]], splititem[2], splititem[3], splititem[4], splititem[5]])
            print(f"Processed data (without duplicates) written to {output_filename}")

# Example usage: Provide the directory containing your CSV files
directory_to_process = '/home/hepnerd/Documents/python/Financial/formatTransactionCSV/input'
output_filename = "output/transactions.csv"
fields = ['Bank', 'Date', 'Transaction', 'Description', 'Category', 'transactionType']
file_exists = os.path.isfile(output_filename)
if not file_exists:
    with open(output_filename, 'w', newline='') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerow(fields)
                    print("header written")
process_csv_files(directory_to_process, output_filename)
remove_duplicates_from_final(output_filename)
