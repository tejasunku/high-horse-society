import requests
import uuid
import time

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_essay_submit_stores_approved_essays_with_versioning():
    # Step 1: Create a sufficiently long approved essay by judging it first
    judge_url = f"{BASE_URL}/essay/judge"
    submit_url = f"{BASE_URL}/essay/submit"
    get_url = f"{BASE_URL}/essay/get"

    # Generate a unique idempotency key for judge step
    judge_idempotency_key = str(uuid.uuid4())
    # Generate an essay_id to receive it in the judge response
    essay_id = str(uuid.uuid4())
    # Create essay body with >1000 words (approximate)
    body = "word " * 1100
    title = "Approved Essay for Versioning Test"
    judge_payload = {
        "idempotency_key": judge_idempotency_key,
        "essay_id": essay_id,
        "title": title,
        "body": body,
        "sources": ["source1", "source2"]
    }

    try:
        # Judge the essay to verify it passes validations
        judge_response = requests.post(judge_url, json=judge_payload, timeout=TIMEOUT)
        assert judge_response.status_code == 200, f"/essay/judge returned {judge_response.status_code}"
        judge_result = judge_response.json()
        assert "isValid" in judge_result and judge_result["isValid"] is True, "Essay was not approved by judge"
        # Extract essay_id from judge response for submission
        essay_id = judge_result.get("essay_id")
        assert essay_id, "Judge response missing essay_id"
        idempotency_key_submit_1 = str(uuid.uuid4())

        # Step 2: Submit the approved essay to /essay/submit for first version
        submit_payload_1 = {
            "idempotency_key": idempotency_key_submit_1,
            "essay_id": essay_id,
            "title": title,
            "body": body,
            "sources": ["source1", "source2"]
        }
        submit_response_1 = requests.post(submit_url, json=submit_payload_1, timeout=TIMEOUT)
        assert submit_response_1.status_code == 200, f"/essay/submit returned {submit_response_1.status_code} on first submit"
        submit_result_1 = submit_response_1.json()
        assert submit_result_1.get("essay_id") == essay_id, "Submitted essay_id mismatch"
        version_1 = submit_result_1.get("version", 1)

        # Step 3: Submit a second version by changing the essay body slightly
        time.sleep(0.5)  # slight delay if needed for DB operations
        idempotency_key_submit_2 = str(uuid.uuid4())
        new_body = body + " Additional sentence to create new version."
        submit_payload_2 = {
            "idempotency_key": idempotency_key_submit_2,
            "essay_id": essay_id,
            "title": title,
            "body": new_body,
            "sources": ["source1", "source2"]
        }
        submit_response_2 = requests.post(submit_url, json=submit_payload_2, timeout=TIMEOUT)
        assert submit_response_2.status_code == 200, f"/essay/submit returned {submit_response_2.status_code} on second submit"
        submit_result_2 = submit_response_2.json()
        assert submit_result_2.get("essay_id") == essay_id, "Submitted essay_id mismatch on second submit"
        version_2 = submit_result_2.get("version")
        assert version_2 is not None, "Second submit response missing version"
        assert version_2 > version_1, "Versioning did not increment on second submission"

        # Step 4: Retrieve latest version and check metadata
        params = {"essay_id": essay_id}
        get_latest_response = requests.get(get_url, params=params, timeout=TIMEOUT)
        assert get_latest_response.status_code == 200, f"/essay/get returned {get_latest_response.status_code} for latest essay retrieval"
        essay_latest = get_latest_response.json()
        assert essay_latest.get("essay_id") == essay_id, "Retrieved essay_id mismatch"
        assert essay_latest.get("version") == version_2, "Latest version mismatch"
        assert essay_latest.get("body") == new_body, "Latest essay body mismatch"
        assert essay_latest.get("title") == title, "Essay title mismatch"

        # Step 5: Retrieve specific version 1 and verify
        params_version_1 = {"essay_id": essay_id, "version": version_1}
        get_version_1_response = requests.get(get_url, params=params_version_1, timeout=TIMEOUT)
        assert get_version_1_response.status_code == 200, f"/essay/get returned {get_version_1_response.status_code} for version 1 retrieval"
        essay_v1 = get_version_1_response.json()
        assert essay_v1.get("version") == version_1, "Version 1 retrieval mismatch"
        assert essay_v1.get("body") == body, "Version 1 essay body mismatch"
        assert essay_v1.get("title") == title, "Version 1 essay title mismatch"

    finally:
        # Cleanup: Delete the essay to avoid cluttering DB if API supports delete (not specified).
        # Since delete endpoint is not specified in PRD, skip explicit cleanup.
        pass

test_essay_submit_stores_approved_essays_with_versioning()
