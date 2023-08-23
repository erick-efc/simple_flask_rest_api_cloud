import os
from utils.functions import sort

UPLOAD_HIST = './historical_upload' 
update_order = ["departments", "jobs", "hired_employees"] # HIRED_EMPLOYEES IS A CHILD TABLE IN THE SCHEMA
file_list = [os.path.splitext(file)[0] for file in os.listdir(UPLOAD_HIST)]
print (sort(update_order, file_list))