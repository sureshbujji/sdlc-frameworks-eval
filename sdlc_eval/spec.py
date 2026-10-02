"""Canonical feature specification used by every framework pipeline.

A single, fixed spec guarantees a fair comparison: all three frameworks
receive exactly the same requirements, and fidelity is measured against
this registry.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AcceptanceCriterion:
    id: str          # e.g. "R1-AC1"
    text: str


@dataclass(frozen=True)
class Requirement:
    id: str          # e.g. "R1"
    title: str
    description: str
    priority: str    # "must" | "should"
    criteria: tuple  # tuple[AcceptanceCriterion, ...]


def _req(req_id, title, description, priority, criteria):
    acs = tuple(
        AcceptanceCriterion(f"{req_id}-AC{i+1}", text)
        for i, text in enumerate(criteria)
    )
    return Requirement(req_id, title, description, priority, acs)


FEATURE_NAME = "webhook-dispatcher"
FEATURE_BLURB = (
    "A multi-tenant webhook event dispatcher: accept events via HTTP, verify "
    "signatures, enforce rate limits, deliver with retries, and quarantine "
    "permanently failing events."
)

REQUIREMENTS: tuple = (
    _req("R1", "Event ingestion endpoint",
         "Accept POST /events with a JSON body containing event_type, "
         "timestamp and payload; validate the schema and return 400 on "
         "malformed input.", "must",
         ["POST /events accepts a valid JSON event and returns 202",
          "Missing event_type, timestamp or payload returns 400",
          "Non-JSON body returns 400"]),
    _req("R2", "HMAC signature verification",
         "Verify the X-Signature header as HMAC-SHA256 of the raw body using "
         "the tenant's secret; reject mismatches with 401.", "must",
         ["Valid signature is accepted",
          "Wrong signature returns 401",
          "Missing signature header returns 401"]),
    _req("R3", "Retry with exponential backoff",
         "Retry failed deliveries up to 5 attempts with exponential backoff "
         "(base 2s) plus jitter; give up afterwards.", "must",
         ["Transient failure is retried",
          "Backoff delay grows exponentially with jitter",
          "Delivery stops after 5 attempts"]),
    _req("R4", "Per-tenant rate limiting",
         "Enforce 100 events/minute per tenant; exceeders get 429 with a "
         "Retry-After header.", "must",
         ["101st event within a minute returns 429",
          "429 response includes a Retry-After header",
          "Limits are isolated per tenant"]),
    _req("R5", "Dead-letter queue",
         "Persist events that exhaust retries, with the failure reason and "
         "attempt history, for later inspection.", "must",
         ["Exhausted event is persisted to the DLQ",
          "DLQ record includes failure reason and attempt count"]),
    _req("R6", "Idempotency",
         "Deduplicate on event_id: a repeat within 24h returns the original "
         "result without redelivery.", "should",
         ["Duplicate event_id returns the original 202 response",
          "No second delivery is attempted for duplicates",
          "Duplicates older than 24h are treated as new"]),
    _req("R7", "Observability",
         "Emit structured logs and per-tenant counters for delivered, "
         "failed and retried events.", "should",
         ["Each delivery emits a structured log line",
          "Per-tenant counters track delivered/failed/retried"]),
    _req("R8", "Graceful shutdown",
         "On SIGTERM, stop accepting new events and drain in-flight "
         "deliveries within 30 seconds.", "should",
         ["SIGTERM stops the listener from accepting new events",
          "In-flight deliveries complete before exit",
          "Shutdown completes within 30 seconds"]),
)

REQUIREMENT_IDS = tuple(r.id for r in REQUIREMENTS)
TOTAL_CRITERIA = sum(len(r.criteria) for r in REQUIREMENTS)
