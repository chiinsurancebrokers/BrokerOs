# Broker OS status

## Idea
White-label AI platform for insurance brokers: intake -> quote -> proposal -> application -> policy copilot -> claims -> renewal. Built from the Ashlar/CHI prototypes. CHI is customer #1.

## Done
- Tenant model: one folder per client (`tenants/<slug>/`), no repo per client.
- Module 1, policy copilot: emergency short-circuit, keyword retrieval, page-cited answers, hand-off when the policy is silent, offline test mode.
- Tests for the above (`pytest`).

## Next (in order)
1. Port the Arrow policy JSON as the first real tenant (private, outside git).
2. Auth: Supabase JWT per tenant, rate limit and daily spend cap.
3. Chat UI (single static page, branded from tenant.json, EN/GR).
4. Quote module: merge the three travel-quote sites and quote engines.
5. Form engine: home + restaurant liability as schemas (PDF, e-signature, 7-day link).
6. Proposal module: merge Proposal Studio + Offer-Builder.
7. Usage analytics per tenant (the number that proves product-market fit).

## Out of scope for now
Consumer app, billing, mobile apps, claims automation.

## Rules
- Never commit real client names, emails or policy extracts. Real tenants stay out of git.
- Coverage answers come from the policy JSON; the model only phrases them.
