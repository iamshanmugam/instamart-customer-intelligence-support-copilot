# API Documentation

Base URL (local): `http://127.0.0.1:8000`

## GET /health

**Response:** `{"status": "ok"}`

## GET /customers/segments?limit=50

Returns rows from `outputs/segmentation/customer_segments.csv` (requires pipeline).

## GET /customers/retention?limit=50

Returns `outputs/segmentation/retention_list.csv`.

## POST /tickets/classify

**Body:**

```json
{
  "text": "I need a refund for a damaged item",
  "strategy": "zero_shot"
}
```

**Success:** category, priority, route, confidence  
**400:** guardrail rejection (`empty_ticket`, `oversized_input`, etc.)

## POST /assistant/ask

**Body:** `{"question": "What is the refund policy within 24 hours?"}`

**Response:** `answer`, `sources[]`, `escalate`

## POST /refund/request

**Body:**

```json
{
  "order_id": "ORD000001",
  "reason": "Item damaged — refund request"
}
```

**Response:** `status`, `decision`, `simulation: true`, optional `order`
