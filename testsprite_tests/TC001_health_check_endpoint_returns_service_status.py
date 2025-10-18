import requests

def test_health_check_service_status():
    base_url = "http://localhost:8000"
    url = f"{base_url}/health"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Health check request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    try:
        json_data = response.json()
    except ValueError as e:
        assert False, f"Response is not valid JSON: {e}"

    assert "status" in json_data, "Response JSON does not contain 'status' key"
    assert isinstance(json_data["status"], str), f"'status' should be a string, got {type(json_data['status'])}"
    assert json_data["status"].lower() in ("healthy", "ok", "up", "running"), f"Unexpected service status value: {json_data['status']}"

test_health_check_service_status()