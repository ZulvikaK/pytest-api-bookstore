import pytest
import requests
from unittest.mock import patch
import re  # validate password

# URLs
url = "https://bookstore.toolsqa.com/Account/v1/User"

headers = {"Content-Type": "application/json"}

# Function to validate password
def is_valid_password(password):
    """Validates the password based on specified criteria."""
    return (
        len(password) >= 8
        and re.search(r'[A-Z]', password)
        and re.search(r'[a-z]', password)
        and re.search(r'\d', password)
        and re.search(r'[^a-zA-Z0-9]', password)
    )

@pytest.mark.parametrize("user_data, expected_status_code, expected_message", [
    ({"userName": "ZulvikaTestke1", "password": "KucingMakanTuna22#"}, 201, "Registration successful"),
    ({"userName": "", "password": "KucingMakanTuna22#"}, 400, "UserName and Password required."),
    ({"userName": "ZulvikaTest", "password": ""}, 400, "UserName and Password required."),
    ({"userName": "ZulvikaTest", "password": "weakpass"}, 400, "Passwords must have at least one non alphanumeric character, one digit ('0'-'9'), one uppercase ('A'-'Z'), one lowercase ('a'-'z'), one special character and Password must be eight characters or longer."),
    ({"userName": "PixelPusher22", "password": "KucingMakanTuna22#"}, 406, "User exists!"),
])
def test_user_registration(user_data, expected_status_code, expected_message):
    """Test user registration with various cases."""
    response = requests.post(url, json=user_data, headers=headers)
    response_data = response.json()

    assert response.status_code == expected_status_code, f"Unexpected status code for {user_data['userName']}"

    if response.status_code == 201:
        assert response_data.get("userID"), "userID missing in successful response"
        assert expected_message in "Registration successful"
    else:
        assert response_data.get("message") == expected_message, f"Unexpected message: {response_data.get('message')}"

@patch("requests.post")
@pytest.mark.parametrize("mock_status_code, mock_message", [
    (500, "Internal Server Error"),
    (429, "Too Many Requests"),
])
def test_uncommon_status_codes(mock_post, mock_status_code, mock_message):
    """Test uncommon status codes using patch."""
    mock_post.return_value.status_code = mock_status_code
    mock_post.return_value.json.return_value = {"message": mock_message}

    user_data = {"userName": "TestUser", "password": "ValidP@ss123"}
    response = requests.post(url, json=user_data)

    assert response.status_code == mock_status_code, f"Unexpected status code: {response.status_code}"
    response_data = response.json()
    assert response_data.get("message") == mock_message, f"Unexpected message: {response_data.get('message')}"
