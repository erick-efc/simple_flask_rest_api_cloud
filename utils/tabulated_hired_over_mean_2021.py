import requests
from tabulate import tabulate

url = 'http://ec2-54-226-246-113.compute-1.amazonaws.com/api/sql/hired_over_mean_2021'

response = requests.get(url)
table = response.json()  # The response should already be the tabulated data as a string
formatted_table = tabulate(table, tablefmt='plain')
print(formatted_table)
