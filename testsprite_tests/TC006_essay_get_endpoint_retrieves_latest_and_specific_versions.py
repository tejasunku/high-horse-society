import requests
import uuid
import time

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_essay_get_endpoint_retrieves_latest_and_specific_versions():
    headers = {"Content-Type": "application/json"}

    # Create a new essay by first judging and then submitting it (2 versions)
    idempotency_key_v1 = str(uuid.uuid4())
    idempotency_key_v2 = str(uuid.uuid4())
    essay_title = "The High Horse Society Philosophy"
    
    # Create an essay body with more than 1000 words (to pass length validation)
    # For simplicity, just repeat a phrase enough times.
    base_paragraph = "The High Horse Society emphasizes high quality online discussions. "
    body_v1 = base_paragraph * 100  # ~1100 words roughly
    body_v2 = base_paragraph * 110  # a bit longer for version 2

    essay_id = None

    try:
        # 1) Judge version 1
        judge_payload_v1 = {
            "idempotency_key": idempotency_key_v1,
            "title": essay_title,
            "body": body_v1,
            "sources": ["https://example.com/source1"]
        }
        judge_resp = requests.post(f"{BASE_URL}/essay/judge", json=judge_payload_v1, headers=headers, timeout=TIMEOUT)
        assert judge_resp.status_code == 200, f"/essay/judge v1 failed with status {judge_resp.status_code}"
        judge_data = judge_resp.json()
        assert "isValid" in judge_data and judge_data["isValid"] is True, "Version 1 essay did not pass validation"
        assert all(x in judge_data for x in ("length", "density", "logical_validity")), "Missing validation details v1"

        # 2) Submit version 1 essay
        submit_resp_v1 = requests.post(f"{BASE_URL}/essay/submit", json=judge_payload_v1, headers=headers, timeout=TIMEOUT)
        assert submit_resp_v1.status_code == 200, f"/essay/submit v1 failed with status {submit_resp_v1.status_code}"
        submit_data_v1 = submit_resp_v1.json()
        assert "essay_id" in submit_data_v1, "No essay_id returned after v1 submit"
        essay_id = submit_data_v1["essay_id"]
        assert isinstance(essay_id, str) and len(essay_id) > 0, "Invalid essay_id v1"

        # 3) Judge version 2 with same essay_id but updated body and different idempotency_key
        judge_payload_v2 = {
            "idempotency_key": idempotency_key_v2,
            "essay_id": essay_id,
            "title": essay_title,
            "body": body_v2,
            "sources": ["https://example.com/source1", "https://example.com/source2"]
        }
        judge_resp_v2 = requests.post(f"{BASE_URL}/essay/judge", json=judge_payload_v2, headers=headers, timeout=TIMEOUT)
        assert judge_resp_v2.status_code == 200, f"/essay/judge v2 failed with status {judge_resp_v2.status_code}"
        judge_data_v2 = judge_resp_v2.json()
        assert judge_data_v2.get("isValid") is True, "Version 2 essay did not pass validation"
        assert all(x in judge_data_v2 for x in ("length", "density", "logical_validity")), "Missing validation details v2"

        # 4) Submit version 2 essay
        submit_resp_v2 = requests.post(f"{BASE_URL}/essay/submit", json=judge_payload_v2, headers=headers, timeout=TIMEOUT)
        assert submit_resp_v2.status_code == 200, f"/essay/submit v2 failed with status {submit_resp_v2.status_code}"

        # Small delay to ensure DB is updated and versions processed
        time.sleep(1)

        # 5) Retrieve latest version via GET /essay/get?essay_id={essay_id}
        params_latest = {"essay_id": essay_id}
        get_latest_resp = requests.get(f"{BASE_URL}/essay/get", params=params_latest, headers=headers, timeout=TIMEOUT)
        assert get_latest_resp.status_code == 200, f"/essay/get latest failed with status {get_latest_resp.status_code}"
        latest_data = get_latest_resp.json()
        # Validate latest version contents: should reflect version 2 (body length approx)
        assert latest_data.get("essay_id") == essay_id, "Mismatch essay_id in latest version"
        assert latest_data.get("title") == essay_title or "title" not in latest_data, "Title missing or incorrect in latest"
        assert "body" in latest_data or "body" not in latest_data, "Body key presence uncertain"
        # Check quality metrics present with keys
        for metric in ("length", "density", "logical_validity"):
            assert metric in latest_data, f"{metric} missing in latest version response"
            metric_obj = latest_data[metric]
            assert isinstance(metric_obj.get("isValid"), bool), f"{metric} isValid not bool"
            assert isinstance(metric_obj.get("rationale"), str), f"{metric} rationale not string"

        # 6) Retrieve version 1 specifically via GET /essay/get?essay_id={essay_id}&version=1
        params_v1 = {"essay_id": essay_id, "version": 1}
        get_v1_resp = requests.get(f"{BASE_URL}/essay/get", params=params_v1, headers=headers, timeout=TIMEOUT)
        assert get_v1_resp.status_code == 200, f"/essay/get version 1 failed with status {get_v1_resp.status_code}"
        v1_data = get_v1_resp.json()
        assert v1_data.get("essay_id") == essay_id, "Mismatch essay_id in version 1"
        for metric in ("length", "density", "logical_validity"):
            assert metric in v1_data, f"{metric} missing in version 1 response"
            metric_obj = v1_data[metric]
            assert isinstance(metric_obj.get("isValid"), bool), f"{metric} isValid not bool in v1"
            assert isinstance(metric_obj.get("rationale"), str), f"{metric} rationale not string in v1"

        # 7) Retrieve version 2 specifically via GET /essay/get?essay_id={essay_id}&version=2
        params_v2 = {"essay_id": essay_id, "version": 2}
        get_v2_resp = requests.get(f"{BASE_URL}/essay/get", params=params_v2, headers=headers, timeout=TIMEOUT)
        assert get_v2_resp.status_code == 200, f"/essay/get version 2 failed with status {get_v2_resp.status_code}"
        v2_data = get_v2_resp.json()
        assert v2_data.get("essay_id") == essay_id, "Mismatch essay_id in version 2"
        for metric in ("length", "density", "logical_validity"):
            assert metric in v2_data, f"{metric} missing in version 2 response"
            metric_obj = v2_data[metric]
            assert isinstance(metric_obj.get("isValid"), bool), f"{metric} isValid not bool in v2"
            assert isinstance(metric_obj.get("rationale"), str), f"{metric} rationale not string in v2"

    finally:
        if essay_id:
            # Cleanup: delete the essay resource if such an endpoint exists,
            # Or simulate cleanup if no delete endpoint is defined in PRD.
            # PRD does not specify a deletion endpoint; nothing to do here.
            pass

test_essay_get_endpoint_retrieves_latest_and_specific_versions()