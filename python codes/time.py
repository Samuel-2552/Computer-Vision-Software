# from datetime import datetime

# # Get the current date and time
# current_time = datetime.datetime.now()

# print(type(current_time))

# # Convert the current time to a string with a specific format
# timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

# print("Timestamp:", timestamp)


# # Assuming current_date_string is obtained as a string from datetime.datetime.now()
# current_date_string = str(datetime.datetime.now())

from datetime import datetime

# Get the current date and time
current_time = datetime.now()

# Convert the current date and time to a string
current_time_string = str(current_time)

print(type(current_time_string))  # Output the string representation of the current date and time


# Convert the string to a datetime object
current_date = datetime.strptime(current_time_string,  "%Y-%m-%d %H:%M:%S.%f")  # Adjust format if needed

print(type(current_date))  # Output the datetime object

another_date = "2023-10-01 17:00:20.098953"
another_date = datetime.strptime(another_date,  "%Y-%m-%d %H:%M:%S.%f")
difference = current_date - another_date

# # Extract the number of days from the timedelta object
difference_in_days = difference.days

print("Difference in days:", type(difference_in_days))
