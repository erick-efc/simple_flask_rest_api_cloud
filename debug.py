import os
import json
import csv

HISTORICAL_DATA_FOLDER = './files'

table_name = 'hired_employees'
csv_file_path = os.path.join(HISTORICAL_DATA_FOLDER, f'{table_name}.csv')
        # BUILDING THE QUERY
data = []
columns = [["a",1],["b",1],["c",1],["d",1],["e",1],["f",1],]
keys = ', '.join([column[0] for column in columns])  # Extract the first element of each tuple
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        data.append(row)

for row_idx, row in enumerate(data):
    for value_idx, value in enumerate(row):
        if value == '990':
            data[row_idx][value_idx] = None

# Insert data into the corresponding table
for row in data:
    values_placeholder = ', '.join(['%s'] * len(row))
    query = f"INSERT INTO {table_name} ({keys}) VALUES ({row})"
    print (query)
