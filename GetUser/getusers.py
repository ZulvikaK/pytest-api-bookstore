import csv
import requests
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# URLs
base_url = "https://bookstore.toolsqa.com/Account/v1/User/"

# File paths
input_file = "input.csv"
output_file = "output.csv"

# Headers template
headers_template = {
    "Authorization": "Bearer {token}",
    "Content-Type": "application/json"
}

# Time delay between requests in seconds
time_delay = 2

def get_user_details(user_id, token):
    """Fetch user details with the given userID and bearer token."""
    headers = headers_template.copy()
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(base_url + user_id, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Failed to fetch details for userID {user_id}: {response.status_code} - {response.text}")
    
    return response

def format_books(books):
    """Format the list of books into a string representation."""
    if not books:
        return "No books found"
    
    formatted_books = []
    for book in books:
        book_info = f"{book.get('title', 'Unknown Title')} by {book.get('author', 'Unknown Author')} (ISBN: {book.get('isbn', 'N/A')})"
        formatted_books.append(book_info)
    
    return '; '.join(formatted_books)

def main():
    responses = []

    # Read input CSV
    with open(input_file, mode="r") as infile:
        csv_reader = csv.DictReader(infile)
        
        for row in csv_reader:
            user_id = row.get("userID")
            token = row.get("token")
            
            if not user_id or not token:
                logging.warning("Missing userID or token in the input CSV.")
                continue
            
            response = get_user_details(user_id, token)
            response_data = response.json() if response.status_code == 200 else {}

            # Prepare output data
            result = {
                "userID": user_id,
                "status_code": response.status_code,
                "message": response_data.get("message", ""),
                "username": response_data.get("username", ""),
                "books": format_books(response_data.get("books", []))  # Format the books
            }
            responses.append(result)

            # Add delay between requests
            logging.info(f"Waiting for {time_delay} seconds before the next request...")
            time.sleep(time_delay)

    # Write to output CSV
    fieldnames = ["userID", "status_code", "message", "username", "books"]
    with open(output_file, mode="w", newline="") as outfile:
        csv_writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(responses)
    
    logging.info(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()