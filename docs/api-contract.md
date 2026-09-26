# MoTA Scholarship Management API Contract

Version: 0.1.0

## Base URL

http://127.0.0.1:8000

---

## GET /health

### Purpose

Check whether the backend is running.

### Response

200 OK

```json
{
  "status": "ok",
  "service": "mota-scholarship-api"
}