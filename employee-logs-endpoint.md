# Employee logs endpoint (paginated)

Returns the employee logs, newest first, a page at a time. Use it for the logs page: show the latest 30, then load the next 30 when the user scrolls or presses "load more".

## Before you start

1. **Drop the old log table once.** The log table has new columns, and the backend doesn't change an existing table. Run `DROP TABLE employee_log;` in your database, then restart the backend so it recreates the table. Without this, creating logs fails.
2. **Update the `EmployeeLog` type** in `pennie-work/frontend/src/api/employees.ts`. It still has `approved` and is missing the new fields. The replacement is under [Response](#response).
3. **Send the admin token.** Like `/api/employee`, this endpoint requires `Authorization: Bearer <token>`. Use the existing `authHeaders()` function, as the employee calls already do.

## Request

```
GET /api/employee_logs/?limit=30&before=<timestamp>
Authorization: Bearer <token>
```

| Parameter | Required | Default | Meaning |
|---|---|---|---|
| `limit` | no | `30` | How many logs to return. Must be between 1 and 100. |
| `before` | no | none | Only return logs older than this timestamp. Leave it out for the first page. |

The endpoint requires the admin token. Without a valid token the backend answers **401**.

## Response

A list of logs, newest first. Only approved entries are logged, so every log means someone was let in.

```json
[
  {
    "uuid": "305127ec-45f5-448a-b78e-5f9d107e6983",
    "employee_uuid": "25ea02aa-4f0e-475c-8585-e2dcc1ce4f9f",
    "timestamp": "2026-10-20T12:59:33.901652+02:00",
    "camera_id": "door1",
    "detection_confidence": 0.93,
    "face_width": 120,
    "face_height": 150
  }
]
```

| Field | Type | Meaning |
|---|---|---|
| `uuid` | string | The log's own id. |
| `employee_uuid` | string | The employee who was let in. |
| `timestamp` | string | When it happened, ISO 8601 with timezone offset. |
| `camera_id` | string | Which camera (door) recognized the person. |
| `detection_confidence` | number, 0–1 | How sure the face detector was that it saw a face. |
| `face_width`, `face_height` | number (whole pixels) | Size of the detected face in the camera image. |

The `EmployeeLog` type in `api/employees.ts` is out of date (it still has `approved`). Replace it with:

```ts
export type EmployeeLog = {
  uuid: string;
  employee_uuid: string;
  timestamp: string;
  camera_id: string;
  detection_confidence: number;
  face_width: number;
  face_height: number;
};
```

The same log objects also appear in `employee_logs` in the response from `GET /api/employee/{uuid}`.

To show the employee's name, look it up from `employee_uuid` in the employee list you already fetch from `GET /api/employee/`.

## How to page through the logs

1. **First page:** `GET /api/employee_logs/?limit=30`
2. **Next page:** take the `timestamp` of the **last** log in the list you just received and send it as `before`:
   `GET /api/employee_logs/?limit=30&before=<that timestamp>`
3. Repeat. When a page comes back with fewer than `limit` logs, there are no more. An empty list (`[]`) means the same thing.

Pages are based on a timestamp, not on page numbers. If someone walks up to the door while the admin is scrolling, the new log won't push older logs onto the next page, so nothing is shown twice. To see newly created logs, fetch the first page again.

## Two rules for `before`

- **Encode it in the URL.** Timestamps include the timezone offset, such as `+02:00`, and a raw `+` in a URL turns into a space, which gives a **422**. Always use `encodeURIComponent`, or build the URL with `URLSearchParams`, which encodes it for you.
- **Send the timestamp back exactly as you received it.** Don't reformat it or create your own date string. A timestamp without a timezone is read in the database's local time, not UTC, and gives the wrong page.

## Example

```ts
export async function getLogs(before?: string, limit = 30): Promise<EmployeeLog[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (before) params.set("before", before);

  const res = await fetch(`${BACKEND_URL}/api/employee_logs/?${params}`, {
    headers: authHeaders(),
  });
  if (res.status === 401) logout();
  if (!res.ok) throw new Error(`Could not fetch logs (${res.status})`);
  return res.json();
}

// usage
const firstPage = await getLogs();
const nextPage = await getLogs(firstPage[firstPage.length - 1].timestamp);
```

## Errors

| Status | When |
|---|---|
| 401 | Missing, invalid or expired token. Send the admin back to the login. |
| 422 | `limit` outside 1–100 or not a number, or `before` is not a valid timestamp (often an unencoded `+`). |
