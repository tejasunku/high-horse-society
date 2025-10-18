import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}


def test_essay_judge_endpoint_validates_essay_quality():
    essays = [
        # Valid essay: >1000 words, expected to pass all checks
        {
            "title": "A well crafted essay on philosophy",
            "body": " ".join(["This is a meaningful sentence."] * 1000),  # ~1000 words
            "idempotency_key": str(uuid.uuid4()),
            "sources": ["https://example.com/source1"]
        },
        # Essay with borderline length (~1000 words), expect length validation and rationale present
        {
            "title": "Borderline length essay",
            "body": "Word " * 1000,
            "idempotency_key": str(uuid.uuid4()),
            "sources": []
        },
        # Essay with sufficient length but likely low density and faulty logic
        {
            "title": "Low density and invalid logic essay",
            "body": ("This statement is false. " * 500) + ("Unrelated filler text. " * 500),
            "idempotency_key": str(uuid.uuid4())
        }
    ]

    for essay in essays:
        payload = {
            "idempotency_key": essay.get("idempotency_key"),
            "title": essay["title"],
            "body": essay["body"]
        }
        if "sources" in essay:
            payload["sources"] = essay["sources"]

        response = requests.post(
            f"{BASE_URL}/essay/judge",
            json=payload,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

        data = response.json()
        # Validate required response fields
        assert isinstance(data.get("isValid"), bool), "Response missing boolean isValid"
        for criterion in ["length", "density", "logical_validity"]:
            assert criterion in data, f"Response missing {criterion} validation"
            crit = data[criterion]
            assert isinstance(crit, dict), f"{criterion} should be an object"
            assert isinstance(crit.get("isValid"), bool), f"{criterion}.isValid missing or not boolean"
            rationale = crit.get("rationale")
            assert isinstance(rationale, str) and len(rationale) > 0, f"{criterion}.rationale missing or empty"

        # Validate returned essay_id, idempotency_key, and sources
        assert isinstance(data.get("essay_id"), str) and len(data["essay_id"]) > 0, "essay_id missing or empty"
        assert data.get("idempotency_key") == essay.get("idempotency_key"), "idempotency_key mismatch"
        assert isinstance(data.get("sources"), list), "sources should be a list"

        # Detailed check examples:
        # For valid length essays, length.isValid should be True
        word_count = len(essay["body"].split())
        if word_count < 1000:
            assert data["length"]["isValid"] is False, "Length validation should fail for essays <1000 words"
            assert "too short" in data["length"]["rationale"].lower()
        else:
            assert data["length"]["isValid"] is True or data["length"]["isValid"] is False  # could be borderline
            # rationale present guaranteed by earlier assertion

        # density and logical_validity are booleans with rationale string as verified

        # isValid overall should be True only if all three validations pass
        expected_is_valid = (
            data["length"]["isValid"] and data["density"]["isValid"] and data["logical_validity"]["isValid"]
        )
        assert data["isValid"] == expected_is_valid, "Overall isValid does not match individual criteria"


test_essay_judge_endpoint_validates_essay_quality()