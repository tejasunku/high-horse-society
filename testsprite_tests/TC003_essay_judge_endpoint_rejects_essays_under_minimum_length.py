import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_essay_judge_rejects_short_essay():
    url = f"{BASE_URL}/essay/judge"
    idempotency_key = str(uuid.uuid4())
    # Create a short essay body under 1000 words (e.g., 50 words)
    short_essay_body = " ".join(["word"] * 50)
    payload = {
        "idempotency_key": idempotency_key,
        "title": "Short Essay Test",
        "body": short_essay_body,
        "sources": []
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to /essay/judge failed: {e}"

    resp_json = response.json()

    # Validate response schema basics
    assert "isValid" in resp_json, "Response missing 'isValid'"
    assert "length" in resp_json, "Response missing 'length' validation"
    length_validation = resp_json["length"]
    assert isinstance(length_validation, dict), "'length' field is not a dict"
    assert "isValid" in length_validation, "'length' validation missing 'isValid'"
    assert "rationale" in length_validation, "'length' validation missing 'rationale'"

    # The essay should be rejected overall and length should be invalid
    assert resp_json["isValid"] is False, "Essay judged as valid despite being too short"
    assert length_validation["isValid"] is False, "Length validation passed for short essay"

    rationale_lower = length_validation["rationale"].lower()
    assert "too short" in rationale_lower or "minimum length" in rationale_lower or "under 1000 words" in rationale_lower, (
        f"Rationale does not clearly indicate essay is too short: {length_validation['rationale']}"
    )

test_essay_judge_rejects_short_essay()