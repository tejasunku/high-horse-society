import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_logical_validity_validation_produces_boolean_and_rationale():
    idempotency_key = str(uuid.uuid4())
    essay_title = "The importance of critical thinking in modern society"
    # Construct an essay body with more than 1000 words (ensured)
    essay_body = (
        "Critical thinking is an essential skill in modern society. " * 100
    )

    payload = {
        "idempotency_key": idempotency_key,
        "title": essay_title,
        "body": essay_body
    }

    try:
        response = requests.post(
            f"{BASE_URL}/essay/judge",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        # Check top-level fields
        assert "isValid" in data and isinstance(data["isValid"], bool), "Missing or invalid 'isValid'"
        assert "idempotency_key" in data and data["idempotency_key"] == idempotency_key, "Missing or mismatched 'idempotency_key'"
        assert "length" in data and isinstance(data["length"], dict), "Missing or invalid 'length'"
        assert "density" in data and isinstance(data["density"], dict), "Missing or invalid 'density'"
        assert "logical_validity" in data and isinstance(data["logical_validity"], dict), "Missing or invalid 'logical_validity'"
        assert "sources" in data and isinstance(data["sources"], list), "Missing or invalid 'sources'"
        assert "essay_id" in data and (isinstance(data["essay_id"], str) or data["essay_id"] is None), "Missing or invalid 'essay_id'"

        # Validate length field
        length = data["length"]
        assert "isValid" in length and isinstance(length["isValid"], bool), "Missing or invalid 'isValid' in 'length'"
        assert "rationale" in length and isinstance(length["rationale"], str) and len(length["rationale"].strip()) > 0, "Missing or empty 'rationale' in 'length'"

        # Validate density field
        density = data["density"]
        assert "isValid" in density and isinstance(density["isValid"], bool), "Missing or invalid 'isValid' in 'density'"
        assert "rationale" in density and isinstance(density["rationale"], str) and len(density["rationale"].strip()) > 0, "Missing or empty 'rationale' in 'density'"

        # Validate logical_validity field
        logical_validity = data["logical_validity"]
        assert "isValid" in logical_validity and isinstance(logical_validity["isValid"], bool), "Missing or invalid 'isValid' in 'logical_validity'"
        assert "rationale" in logical_validity and isinstance(logical_validity["rationale"], str) and len(logical_validity["rationale"].strip()) > 0, "Missing or empty 'rationale' in 'logical_validity'"

    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_logical_validity_validation_produces_boolean_and_rationale()
