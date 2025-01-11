import requests
import csv
import time
import re  # For password validation

# URL for the registration API
url = "https://bookstore.toolsqa.com/Account/v1/User"

# Function to validate password
def is_valid_password(password):
    """Validates the password based on specified criteria."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):  # Must contain uppercase letter
        return False
    if not re.search(r'[a-z]', password):  # Must contain lowercase letter
        return False
    if not re.search(r'\d', password):  # Must contain a digit
        return False
    if not re.search(r'[^a-zA-Z0-9]', password):  # Must contain a special character
        return False
    return True

# Open CSV file to read input data and prepare output file
with open('users.csv', mode='r') as input_file, open('registration_results.csv', mode='w', newline='') as output_file:
    csv_reader = csv.DictReader(input_file)
    fieldnames = ['userName', 'password', 'status_code', 'userID', 'message']  # Add new columns
    csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    
    csv_writer.writeheader()  # Write header to output file
    
    for row in csv_reader:
        user_data = {
            "userName": row['userName'],
            "password": row['password']
        }

        # Check if username or password is empty
        if not user_data["userName"] or not user_data["password"]:
            print(f"Skipped user: {user_data['userName']} (Missing username or password)")
            result_row = {
                'userName': user_data['userName'],
                'password': user_data['password'],
                'status_code': 400,
                'userID': 'N/A',
                'message': "User Name and Password required."
            }
            csv_writer.writerow(result_row)
            continue

        # Validate password
        if not is_valid_password(user_data["password"]):
            print(f"Invalid password for user: {user_data['userName']}")
            result_row = {
                'userName': user_data['userName'],
                'password': user_data['password'],
                'status_code': 400,
                'userID': 'N/A',
                'message': "Passwords must have at least one non alphanumeric character, one digit ('0'-'9'), one uppercase ('A'-'Z'), one lowercase ('a'-'z'), one special character and Password must be eight characters or longer."
            }
            csv_writer.writerow(result_row)
            continue

        # Send POST request
        response = requests.post(url, json=user_data)
        response_data = response.json()  # Response in JSON format
        
        # Process response based on status code and response body
        if response.status_code == 201:
            # Registration successful
            result_row = {
                'userName': user_data['userName'],
                'password': user_data['password'],
                'status_code': response.status_code,
                'userID': response_data.get('userID', 'N/A'),
                'message': "Registration successful"
            }
        elif response.status_code == 400:
            if response_data.get("code") == "1204":
                # User already registered
                result_row = {
                    'userName': user_data['userName'],
                    'password': user_data['password'],
                    'status_code': response.status_code,
                    'userID': 'N/A',
                    'message': "User  exists!"
                }
            elif response_data.get("code") == "1200":
                # Username or password is empty
                result_row = {
                    'userName': user_data['userName'],
                    'password': user_data['password'],
                    'status_code': response.status_code,
                    'userID': 'N/A',
                    'message': "User Name and Password required."
                }
            elif response_data.get("code") == "1300":
                # Invalid password format
                result_row = {
                    'userName': user_data['userName'],
                    'password': user_data['password'],
                    'status_code': response.status_code,
                    'userID': 'N/A',
                    'message': "Passwords must have at least one non alphanumeric character, one digit ('0'-'9'), one uppercase ('A'-'Z'), one lowercase ('a'-'z'), one special character and Password must be eight characters or longer."
                }
            else:
                # Other errors
                result_row = {
                    'userName': user_data['userName'],
                    'password': user_data['password'],
                    'status_code': response.status_code,
                    'userID': 'N/A',
                    'message': response_data.get("message", "Unknown error")
                }
        else:
            # Handle unexpected status codes
            result_row = {
                'userName': user_data['userName'],
                'password': user_data['password'],
                'status_code': response.status_code,
                'userID': 'N/A',
                'message': response_data.get("message", "Unknown error")
            }

        # Write result to output file
        csv_writer.writerow(result_row)
        
        # Print result to console
        print(f"Processed user: {user_data['userName']}, Message: {result_row['message']}")
        
        # Delay 1 second before processing the next user
        time.sleep(1)