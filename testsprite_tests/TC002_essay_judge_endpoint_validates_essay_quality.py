import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def test_essay_judge_endpoint_validates_essay_quality():
    url = f"{BASE_URL}/essay/judge"
    
    # Essays for testing various validation scenarios
    essays = [
        {
            "title": "Too Short Essay",
            "body": "Word " * 50,  # 50 words, below 1000 words minimum
            "sources": [],
            "expected": {
                "length": False,
            }
        },
        {
            "title": "Low Information Density Essay",
            "body": "This is a lengthy text but it contains a lot of filler words and little real information. " * 50,  # ~600 words, likely low density
            "sources": [],
            "expected": {
                "length": False,  # May fail length, adjusted to test length or density fail
            }
        },
        {
            "title": "Logically Invalid Essay",
            "body": (
                "This essay has enough length " + ("word " * 980) + 
                " but it contradicts itself and lacks logical coherence."  # Over 1000 words, logically invalid content simulated
            ),
            "sources": [],
            "expected": {
                "length": True,
                "logical_validity": False,
            }
        },
        {
            "title": "Valid Essay",
            "body": " ".join(["word"] * 1000),  # Exactly 1000 words, neutral content assumed valid
            "sources": ["source1", "source2"],
            "expected": {
                "length": True,
                "density": True,
                "logical_validity": True,
            }
        }
    ]
    
    for essay in essays:
        idempotency_key = str(uuid.uuid4())
        payload = {
            "title": essay["title"],
            "body": essay["body"],
            "sources": essay.get("sources", []),
            "idempotency_key": idempotency_key
        }
        response = None
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            assert False, f"Request failed for essay titled '{essay['title']}': {e}"
        
        resp_json = response.json()
        
        # Validate required fields are present
        required_fields = [
            "isValid",
            "length",
            "density",
            "logical_validity",
            "sources",
            "essay_id",
            "idempotency_key"
        ]
        for field in required_fields:
            assert field in resp_json, f"Response missing required field '{field}' for essay titled '{essay['title']}'"
        
        # Validate idempotency_key matches
        assert resp_json["idempotency_key"] == idempotency_key, "Returned idempotency_key does not match request"
        
        # Validate essay_id is a non-empty string
        assert isinstance(resp_json["essay_id"], str) and resp_json["essay_id"].strip() != "", "Invalid or empty essay_id"
        
        # Validate subfields of length, density, logical_validity
        def validate_validation_result(field_name):
            field = resp_json[field_name]
            assert "isValid" in field and isinstance(field["isValid"], bool), f"{field_name} missing or invalid isValid"
            assert "rationale" in field and isinstance(field["rationale"], str), f"{field_name} missing or invalid rationale"
        
        validate_validation_result("length")
        validate_validation_result("density")
        validate_validation_result("logical_validity")
        
        expected = essay["expected"]
        
        # Validate expected outcomes if provided
        if "length" in expected:
            assert resp_json["length"]["isValid"] == expected["length"], f"Essay '{essay['title']}' length validation mismatch"
        if "density" in expected:
            assert resp_json["density"]["isValid"] == expected["density"], f"Essay '{essay['title']}' density validation mismatch"
        if "logical_validity" in expected:
            assert resp_json["logical_validity"]["isValid"] == expected["logical_validity"], f"Essay '{essay['title']}' logical_validity validation mismatch"
        
        # Validate overall isValid matches all criteria
        overall_pass = (
            resp_json["length"]["isValid"] and
            resp_json["density"]["isValid"] and
            resp_json["logical_validity"]["isValid"]
        )
        assert resp_json["isValid"] == overall_pass, f"Overall isValid does not match criteria for essay '{essay['title']}'"
        
        # sources field should reflect input
        assert resp_json["sources"] == essay.get("sources", []), f"Sources mismatch for essay '{essay['title']}'"

test_essay_judge_endpoint_validates_essay_quality()