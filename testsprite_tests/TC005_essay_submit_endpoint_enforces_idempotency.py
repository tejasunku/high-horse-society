import requests
import uuid
import time

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_essay_submit_idempotency():
    submit_url = f"{BASE_URL}/essay/submit"
    judge_url = f"{BASE_URL}/essay/judge"

    # Create a valid essay to submit (1000+ words simulation)
    essay_title = "The Importance of High-Quality Essays in Social Platforms"
    essay_body = "word " * 1000  # 1000 repeated words to satisfy length validation
    idempotency_key = str(uuid.uuid4())

    # Step 1: Judge the essay to ensure it passes validation
    judge_payload = {
        "idempotency_key": idempotency_key,
        "title": essay_title,
        "body": essay_body,
        "sources": []
    }
    judge_resp = requests.post(judge_url, json=judge_payload, timeout=TIMEOUT)
    assert judge_resp.status_code == 200, f"Judge request failed with {judge_resp.status_code}"
    judge_data = judge_resp.json()

    assert judge_data.get("isValid") is True, "Essay judged as invalid, can't test submit idempotency"
    essay_id = judge_data.get("essay_id")
    assert essay_id, "Judgment response missing essay_id"
    # Use the same idempotency_key for submit requests
    submit_payload = {
        "idempotency_key": idempotency_key,
        "essay_id": essay_id,
        "title": essay_title,
        "body": essay_body,
        "sources": []
    }

    try:
        # First submission
        resp1 = requests.post(submit_url, json=submit_payload, timeout=TIMEOUT)
        assert resp1.status_code == 200, f"First submit failed with status {resp1.status_code}"
        submit_data_1 = resp1.json()
        returned_essay_id_1 = submit_data_1.get("essay_id")
        returned_idempotency_key_1 = submit_data_1.get("idempotency_key")
        assert returned_essay_id_1 == essay_id, "Submitted essay_id mismatch in first submission"
        assert returned_idempotency_key_1 == idempotency_key, "Idempotency key mismatch in first submission"

        # Second submission with identical payload and same idempotency_key
        resp2 = requests.post(submit_url, json=submit_payload, timeout=TIMEOUT)
        assert resp2.status_code == 200, f"Second submit failed with status {resp2.status_code}"
        submit_data_2 = resp2.json()
        returned_essay_id_2 = submit_data_2.get("essay_id")
        returned_idempotency_key_2 = submit_data_2.get("idempotency_key")
        assert returned_essay_id_2 == essay_id, "Submitted essay_id mismatch in second submission"
        assert returned_idempotency_key_2 == idempotency_key, "Idempotency key mismatch in second submission"

        # Assert that the response contents from both submissions are identical,
        # meaning no duplicate processing occurred.
        assert submit_data_1 == submit_data_2, "Different responses for identical submissions with same idempotency_key"

    finally:
        # Cleanup: Attempt to delete the essay using the essay_id if delete endpoint exists
        # Since no delete endpoint info in PRD, skipping explicit cleanup
        # Normally would add code here to delete the created essay resource
        pass

test_essay_submit_idempotency()