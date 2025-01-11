import csv
import requests
import logging
import pytest
from unittest.mock import patch

# Set up logging
logging.basicConfig(level=logging.INFO)

# Base URL for the API
base_url = "https://bookstore.toolsqa.com/Account/v1/User/"

# Headers template
headers_template = {
    "Authorization": "Bearer {token}",
    "Content-Type": "application/json"
}

def get_user_details(user_id, token):
    """Fetch user details with the given userID and bearer token."""
    headers = headers_template.copy()
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(base_url + user_id, headers=headers)
    logging.info(f"Response for userID {user_id}: {response.status_code} - {response.text}")
    return response

def load_test_data_from_csv(file_path):
    """Load test data from a CSV file."""
    test_data = []
    with open(file_path, mode="r") as infile:
        csv_reader = csv.DictReader(infile)
        for row in csv_reader:
            test_data.append((
                row["userID"],
                row["token"],
                int(row["expected_status_code"]),
                row["expected_message"]
            ))
    return test_data

# Load test data from the CSV file
csv_file_path = "input_test.csv"  # Update with your actual file path
test_data = load_test_data_from_csv(csv_file_path)

@pytest.mark.parametrize("user_id, token, expected_status_code, expected_message", test_data)
def test_get_user_details(user_id, token, expected_status_code, expected_message):
    """Test user details retrieval with various cases."""
    response = get_user_details(user_id, token)
    
    # Parse response JSON if available
    try:
        response_data = response.json()
    except ValueError:
        response_data = {}

    assert response.status_code == expected_status_code, f"Unexpected status code for userID {user_id}"

    if response.status_code == 200:
        # Validate successful response fields
        assert "userId" in response_data, "userId missing in successful response"
        assert "username" in response_data, "username missing in successful response"
    else:
        # Validate error response message
        actual_message = response_data.get("message", "No message provided")
        assert actual_message == expected_message, (
            f"Unexpected message: {actual_message}. Expected: {expected_message}"
        )

# Add tests for uncommon HTTP statuses
@pytest.mark.parametrize("mock_status, mock_response_text", [
    (500, "Internal Server Error"),  # Server error
    (429, "Too Many Requests")  # Rate limit exceeded
])
def test_uncommon_http_status(mock_status, mock_response_text):
    """Test for uncommon HTTP statuses."""
    with patch("requests.get") as mock_get:
        # Mock the response for uncommon statuses
        mock_get.return_value.status_code = mock_status
        mock_get.return_value.text = mock_response_text

        # Simulate a request
        response = get_user_details("testUserID", "testToken")

        # Validate the mocked response
        assert response.status_code == mock_status, f"Unexpected status code: {response.status_code}"
        assert response.text == mock_response_text, f"Unexpected response text: {response.text}"
