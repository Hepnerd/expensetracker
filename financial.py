# TODO
# Retrieve and update budget
# Retrieve and update fields
# Update records 

import os
import csv

def read_csv_file(file_path):
    """
    Reads a CSV file and returns its data as a list of dictionaries.
    Each dictionary represents a row, with keys corresponding to column names.
    """
    data = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
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

def process_csv_files(directory_path):
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
                # Example: Assigning 'amount' field based on file name
                if 'pnc' in filename.lower():
                    transactionDate = row['Date']
                    description = row['Description']
                    transaction += float(row['Withdrawals'].replace("$", "").replace(",", "") or 0)
                    transaction -= float(row['Deposits'].replace("$", "").replace(",", "") or 0)
                    category = row['Category']
                elif 'key' in filename.lower():
                    transactionDate = row['Date']
                    transaction = row['Amount']
                    description = row['Description']
                    category = row['Category']
                elif 'ally' in filename.lower():
                    transactionDate = row['Date']
                    transaction += float(row['Amount'])
                    category = row['Category']
                    description = row['Description']

                # Add the filename as a prefix to each field
                for key in row:
                    bank = f"{filename.split('_')[0]}_{row[key]}"
                
                transactionArray.insert(1, "{0},{1},{2},{3},{4}".format(bank,transactionDate,transaction,description,category))
            # Remove duplicates
            # unique_data = remove_duplicates(transactionArray)
            print(transactionArray)
            transactionArray = list(set(transactionArray))
            print("gobbledeegook")
            print(transactionArray)
            
            # Write the processed data to a new CSV file
            output_filename = "output/transactions.csv"
            with open(output_filename, 'a+', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(fields)
                for item in transactionArray:
                    splititem = item.split(",")
                    writer.writerow([[splititem[0]], [splititem[1]], splititem[2], splititem[3], splititem[4]])
            print(f"Processed data (without duplicates) written to {output_filename}")

# Example usage: Provide the directory containing your CSV files
directory_to_process = '/home/hepnerd/Documents/python/Financial/input'
fields = ['Bank', 'Date', 'Transaction', 'Description', 'Category']
transactionArray = []
process_csv_files(directory_to_process)
