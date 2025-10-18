import requests

def test_TC010_local_dev_environment_spins_up_postgres_and_service():
    url = "http://localhost:8000/health"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Service is not available at {url}. Error: {e}"

    # Validate response content
    try:
        json_data = response.json()
    except ValueError:
        assert False, "Response is not a valid JSON."

    assert "status" in json_data, "Response JSON does not contain 'status' key."
    assert isinstance(json_data["status"], str), "'status' value should be a string."
    assert json_data["status"].lower() in ["healthy", "ok", "running", "available", "up"], (
        f"Service status value unexpected: {json_data['status']}")

test_TC010_local_dev_environment_spins_up_postgres_and_service()