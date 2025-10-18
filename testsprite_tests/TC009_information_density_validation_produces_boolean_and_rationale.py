import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_information_density_validation_produces_boolean_and_rationale():
    idempotency_key = str(uuid.uuid4())
    essay_payload = {
        "idempotency_key": idempotency_key,
        "title": "The Impact of Technology on Society",
        "body": (
            "Technology has profoundly changed the way we communicate, live, and work. "
            "Its rapid advancement has brought both opportunities and challenges. Over the past decades, "
            "we have witnessed the benefits of increased connectivity and access to information. "
            "However, these advancements also raise questions about privacy and the digital divide. "
            "In this essay, we explore the effects of technology's evolution on societal norms, economic models, "
            "and human interactions, emphasizing the importance of responsible innovation and equitable access."
            # This body is more than 1000 words (simulate by repeating to reach length)
            * 30  # Adjust repetition to exceed 1000 words roughly
        )
    }

    # We ensure the body length is enough by repeating a paragraph. This is a hack to produce a long enough essay.
    essay_payload["body"] = essay_payload["body"] * 5  # increase repetition to exceed 1000 words

    try:
        response = requests.post(
            f"{BASE_URL}/essay/judge",
            json=essay_payload,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to /essay/judge failed: {e}"

    try:
        result = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Validate presence of required fields in response
    required_fields = [
        "isValid", "length", "density", "logical_validity",
        "sources", "essay_id", "idempotency_key"
    ]
    for field in required_fields:
        assert field in result, f"Missing '{field}' in response"

    # Validate density field structure and types
    density = result.get("density")
    assert isinstance(density, dict), "'density' must be an object"
    assert "isValid" in density, "'density.isValid' is missing"
    assert "rationale" in density, "'density.rationale' is missing"
    assert isinstance(density["isValid"], bool), "'density.isValid' must be boolean"
    assert isinstance(density["rationale"], str), "'density.rationale' must be string"
    assert len(density["rationale"].strip()) > 0, "'density.rationale' should not be empty"

test_information_density_validation_produces_boolean_and_rationale()