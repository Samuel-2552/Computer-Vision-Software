import datetime

# Get the current date and time
current_time = datetime.datetime.now()

print(type(current_time))

# Convert the current time to a string with a specific format
timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

print("Timestamp:", timestamp)
