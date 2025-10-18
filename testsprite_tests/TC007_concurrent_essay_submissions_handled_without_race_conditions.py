import requests
import concurrent.futures
import uuid
import time

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_concurrent_essay_submissions_handled_without_race_conditions():
    # Sample essay body with >1000 words (using repeated phrase)
    repeated_phrase = "This is a high quality essay. "
    body_text = repeated_phrase * 70  # ~350 words; multiply more to exceed 1000 words
    body_text = body_text * 3  # ~1050 words

    def judge_essay(idempotency_key):
        payload = {
            "idempotency_key": idempotency_key,
            "title": f"Concurrency Test Essay Judging {idempotency_key[:8]}",
            "body": body_text,
            "sources": ["https://example.com/source1", "https://example.com/source2"]
        }
        try:
            resp = requests.post(f"{BASE_URL}/essay/judge", json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
            result = resp.json()
            assert "isValid" in result and isinstance(result["isValid"], bool)
            # Checks for detailed criteria presence
            for crit in ["length", "density", "logical_validity"]:
                assert crit in result and "isValid" in result[crit] and "rationale" in result[crit]
            # Essay should be valid (pass) because essay >1000 words
            assert result["isValid"] is True
            return result["essay_id"], idempotency_key
        except Exception as e:
            return f"error: {str(e)}", idempotency_key

    def submit_essay(essay_id, idempotency_key):
        payload = {
            "idempotency_key": idempotency_key,
            "essay_id": essay_id,
            "title": f"Concurrency Test Essay Submission {idempotency_key[:8]}",
            "body": body_text,
            "sources": ["https://example.com/source1", "https://example.com/source2"]
        }
        try:
            resp = requests.post(f"{BASE_URL}/essay/submit", json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
            # According to PRD, submit returns 200 on success, no detailed schema provided
            return resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        except Exception as e:
            return f"error: {str(e)}"

    # Use unique idempotency keys for concurrency test
    N_CONCURRENT = 10

    judged_results = []
    submitted_results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=N_CONCURRENT*2) as executor:
        # Step 1: Concurrently judge essays
        future_judge = {executor.submit(judge_essay, str(uuid.uuid4())): i for i in range(N_CONCURRENT)}
        for future in concurrent.futures.as_completed(future_judge):
            result = future.result()
            judged_results.append(result)

        # Filter valid essay_ids from judging step; discard errors
        valid_essays = [(eid, key) for (eid, key) in judged_results if not isinstance(eid, str) or not eid.startswith("error")]

        # Step 2: Concurrently submit essays judged valid
        future_submit = {
            executor.submit(submit_essay, eid, key): (eid, key) for eid, key in valid_essays
        }
        for future in concurrent.futures.as_completed(future_submit):
            res = future.result()
            submitted_results.append(res)

    # Assertions: all judge requests succeeded without errors and indicated valid
    for res in judged_results:
        essay_id, idem_key = res
        assert not (isinstance(essay_id, str) and essay_id.startswith("error")), f"Judge error for idempotency_key {idem_key}: {essay_id}"

    # Assertions: all submit requests succeeded without errors
    for res in submitted_results:
        assert not (isinstance(res, str) and res.startswith("error")), f"Submit error: {res}"

    # Confirm no duplicated essay_ids among judged results
    essay_ids = [eid for eid, _ in valid_essays]
    assert len(essay_ids) == len(set(essay_ids)), "Duplicate essay_ids returned from judge step, possible race condition"

    # Confirm all submitted essay_ids exist in judged essay_ids
    # Since submit response structure is unknown, cannot check essay_id in submit response.
    # But if submit returns error we would have asserted above.

test_concurrent_essay_submissions_handled_without_race_conditions()