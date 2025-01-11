import csv
import requests
import time

# URLs
login_url = "https://bookstore.toolsqa.com/Account/v1/Authorized"
generate_token_url = "https://bookstore.toolsqa.com/Account/v1/GenerateToken"

# File paths
input_csv = "credentials.csv"
output_csv = "responses.csv"

# Headers for API requests
headers = {
    "Content-Type": "application/json"
}

# Time delay in seconds
time_delay = 2

# Prepare output data
responses = []

# Read input CSV
with open(input_csv, mode="r") as infile:
    csv_reader = csv.DictReader(infile)
    
    for row in csv_reader:
        username = row.get("username")
        password = row.get("password")

        # Check if username or password is missing
        if not username or not password:
            print(f"Skipped user: {username} (Missing username or password)")
            responses.append({
                "username": username,
                "login_status": "Failed",
                "token": "",
                "expires": "",
                "result": "",
                "status": "Missing username or password"
            })
            continue

        # Prepare payload
        payload = {
            "userName": username,
            "password": password
        }

        try:
            # Step 1: Login
            login_response = requests.post(login_url, json=payload, headers=headers)
            login_data = login_response.json()

            if login_response.status_code == 200:
                print(f"Login request sent for user: {username}")

                # Step 2: Generate Token
                token_response = requests.post(generate_token_url, json=payload, headers=headers)
                token_data = token_response.json()

                if token_response.status_code == 200 and token_data.get("status") == "Success":
                    responses.append({
                        "username": username,
                        "login_status": "Success",
                        "token": token_data.get("token", ""),
                        "expires": token_data.get("expires", ""),
                        "result": token_data.get("result", ""),
                        "status": token_data.get("status", "")
                    })
                else:
                    responses.append({
                        "username": username,
                        "login_status": "Success",
                        "token": "Failed to generate token",
                        "expires": "",
                        "result": token_data.get("result", ""),
                        "status": token_data.get("status", "Failed")
                    })
            elif login_response.status_code == 400:
                if login_data.get("code") == "1200":
                    print("User  Name and Password required.")
                elif login_data.get("code") == "1207":
                    print("User  not found!")
                responses.append({
                    "username": username,
                    "login_status": "Failed",
                    "token": "",
                    "expires": "",
                    "result": "",
                    "status": "Unauthorized"
                })
            else:
                print(f"Unexpected response for user {username}: {login_response.status_code}")
                responses.append({
                    "username": username,
                    "login_status": "Failed",
                    "token": "",
                    "expires": "",
                    "result": "",
                    "status": "Unexpected error"
                })

        except Exception as e:
            # Handle errors
            responses.append({
                "username": username,
                "login_status": "Error",
                "token": "",
                "expires": "",
                "result": "",
                "status": str(e)
            })

        # Add delay between requests
        print(f"Waiting for {time_delay} seconds before the next request...")
        time.sleep(time_delay)

# Write to output CSV
with open(output_csv, mode="w", newline="") as outfile:
    fieldnames = ["username", "login_status", "token", "expires", "result", "status"]
    csv_writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    csv_writer.writeheader()
    csv_writer.writerows(responses)

print(f"Responses have been saved to {output_csv}")