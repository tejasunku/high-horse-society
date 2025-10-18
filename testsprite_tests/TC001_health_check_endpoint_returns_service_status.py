import requests

def test_health_check_endpoint_returns_service_status():
    base_url = "http://localhost:8000"
    url = f"{base_url}/health"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed with exception: {e}"
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    try:
        json_data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"
    
    assert "status" in json_data, "Response JSON does not contain 'status' key"
    assert isinstance(json_data["status"], str), f"'status' value is not a string, got type {type(json_data['status'])}"
    assert json_data["status"].lower() in ["healthy", "ok", "healthy"], f"Unexpected service status value: {json_data['status']}"

test_health_check_endpoint_returns_service_status()