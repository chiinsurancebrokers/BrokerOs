# Broker OS

White-label AI platform for insurance brokers. See `STATUS.md` for the plan.

## Run

    pip install -r requirements.txt
    uvicorn app.main:app --reload
    curl -X POST localhost:8000/api/demo/copilot/chat \
      -H 'content-type: application/json' \
      -d '{"message":"Do I need prior approval for hospital admission?"}'

Set `ANTHROPIC_API_KEY` for model-phrased answers; without it the API returns the matched policy facts verbatim (also used by the tests).

## Add a client
Create `tenants/<slug>/tenant.json` and `policy.json` (copy `tenants/demo`). Real tenants are git-ignored.

## Test

    pytest
