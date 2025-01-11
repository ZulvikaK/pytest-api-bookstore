import pytest
import requests
from unittest.mock import patch

# URLs
login_url = "https://bookstore.toolsqa.com/Account/v1/Authorized"
generate_token_url = "https://bookstore.toolsqa.com/Account/v1/GenerateToken"

headers = {"Content-Type": "application/json"}

def login_user(username, password):
    """Login and return response."""
    payload = {"userName": username, "password": password}
    return requests.post(login_url, json=payload, headers=headers, timeout=10)

def generate_token(username, password):
    """Generate token and return response."""
    payload = {"userName": username, "password": password}
    return requests.post(generate_token_url, json=payload, headers=headers, timeout=10)

@pytest.mark.parametrize("username, password, expected_status, expected_message", [
    ("PixelPusher22", "KucingMakanTuna22#", 200, "true"),  # Successful login
    ("invalidUser", "WrongPassword", 404, "User not found!"),  # Invalid credentials
    ("", "Valid@123", 400, "UserName and Password required."),  # Missing username
    ("validUser", "", 400, "UserName and Password required.")  # Missing password
])
def test_login(username, password, expected_status, expected_message):
    response = login_user(username, password)

    # Validate status code
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code} for user {username}"
    )

    # Validate response content
    try:
        data = response.json()
    except ValueError:
        pytest.fail(f"Invalid JSON response: {response.text}")

    if response.status_code == 200:
        assert response.text == expected_message, f"Message incorrect for user: {username}"
    else:
        assert data.get("message", "Unknown error") == expected_message, (
            f"Expected message '{expected_message}', got '{data.get('message')}'"
        )

@pytest.mark.parametrize("username, password, expected_status, expected_result", [
    ("PixelPusher22", "KucingMakanTuna22#", "Success", "User authorized successfully."),  # Successful token
    ("invalidUser", "WrongPassword", "Failed", "User authorization failed."),  # Invalid credentials
    ("", "Valid@123", "Failed", "UserName and Password required.")  # Missing username
])
def test_generate_token(username, password, expected_status, expected_result):
    response = generate_token(username, password)

    # Validate response content
    try:
        data = response.json()
    except ValueError:
        pytest.fail(f"Invalid JSON response: {response.text}")

    actual_status = data.get("status", "Failed")
    actual_result = data.get("result", data.get("message", "Unknown error"))

    # Validate status and result
    assert actual_status == expected_status, (
        f"Expected status '{expected_status}', got '{actual_status}' for user {username}"
    )
    assert actual_result == expected_result, (
        f"Expected result '{expected_result}', got '{actual_result}' for user {username}"
    )

# Add tests for uncommon HTTP statuses
@pytest.mark.parametrize("mock_status, mock_response_text", [
    (500, "Internal Server Error"),  # Server error
    (429, "Too Many Requests")  # Rate limit exceeded
])
def test_uncommon_http_status(mock_status, mock_response_text):
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = mock_status
        mock_post.return_value.text = mock_response_text

        # Test login with simulated error
        response = login_user("testUser", "testPassword")
        assert response.status_code == mock_status, f"Unexpected status code: {response.status_code}"
        assert response.text == mock_response_text, f"Unexpected response text: {response.text}"

        # Test generate token with simulated error
        response = generate_token("testUser", "testPassword")
        assert response.status_code == mock_status, f"Unexpected status code: {response.status_code}"
        assert response.text == mock_response_text, f"Unexpected response text: {response.text}"
