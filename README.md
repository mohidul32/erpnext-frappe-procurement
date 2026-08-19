# Procurement Management — ERPNext Custom App

A custom Frappe/ERPNext app implementing an internal procurement requisition workflow.

---

## Installation

```bash
bench get-app procurement_management /path/to/app
bench --site [site-name] install-app procurement_management
bench --site [site-name] migrate
bench build --app procurement_management
```

---

## Task 1 — Procurement Requisition DocType

A new DocType `Procurement Requisition` was created with the following fields:

| Field | Type | Notes |
|---|---|---|
| Requisition No. | Data (autoname) | Format: `PR-.YYYY.-.#####` |
| Request Date | Date | Defaults to today |
| Requested By | Link → User | The employee making the request |
| Department | Link → Department | Requester's department |
| Item Description | Data | Description of item needed |
| Quantity | Float | Number of units required |
| Estimated Budget | Currency | Estimated cost |
| Required Date | Date | When the item is needed |
| Justification | Small Text | Business reason for the request |
| Status | Select | Synced from workflow state |
| Workflow State | Data (hidden) | Managed by Frappe workflow engine |

**Design decisions:**
- `Status` is a read-only Select field synced from `workflow_state` via `on_update` hook, giving a clean user-facing status indicator
- `autoname` uses `PR-.YYYY.-.#####` for readable, year-based sequential numbering

---

## Task 2 — Business Validations

Validations are implemented in **two layers**:

### Server-side (Python controller — `procurement_requisition.py`)
```python
def validate(self):
    self.validate_quantity()
    self.validate_estimated_budget()
    self.validate_required_date()
```
- Quantity must be > 0
- Estimated Budget must be > 0
- Required Date cannot be earlier than today

**Why server-side?** Server validation is the source of truth — it cannot be bypassed by disabling JavaScript or making direct API calls. This ensures data integrity regardless of how the document is saved.

### Client-side (JavaScript — `procurement_requisition.js`)
Instant feedback on field change events for better UX — clears invalid values and shows a message immediately without requiring a save attempt.

---

## Task 3 — Approval Workflow

Workflow: `Procurement Requisition Approval`

```
Draft
  └─► Pending Department Review   (Action: Submit for Review, Role: Employee)
        └─► Pending Finance Review (Action: Approve, Role: Purchase Manager)
        └─► Rejected               (Action: Reject,  Role: Purchase Manager)
              └─► Approved         (Action: Approve, Role: Accounts Manager)
              └─► Rejected         (Action: Reject,  Role: Accounts Manager)

Rejected
  └─► Draft                       (Action: Resubmit, Role: Employee)
```

**Role mapping:**
| Workflow Stage | ERPNext Role |
|---|---|
| Submit for Review | Employee |
| Department Head Approval | Purchase Manager |
| Finance Approval | Accounts Manager |

**Key configurations:**
- `allow_self_approval: 0` on all approval transitions — requester cannot approve their own request
- Stages cannot be skipped — each transition is locked to a specific role
- Rejected requisitions can be resubmitted by the Employee

---

## Task 4 — Procurement Report

A **Script Report** named `Procurement Requisition Report` with:

**Columns:** Requisition No, Request Date, Requested By, Department, Item Description, Estimated Budget, Status

**Filters:** Department (Link), Status (Select)

Located at: `procurement_management/report/procurement_requisition_report/`

---

## Part B — Automation

Both Option A and Option B were implemented.

### Option A — Create RFQ Button
- A `Create RFQ` button appears in the **Actions** menu when the requisition is in `Approved` state
- Clicking shows a confirmation dialog
- On confirm, calls the whitelisted server method `create_rfq()` which:
  - Creates a `Request for Quotation` document
  - Pre-fills item description, quantity, rate, and required date from the requisition
  - Redirects the user to the new RFQ

### Option B — Approval Notification
- When workflow state reaches `Approved`, `notify_administration()` is triggered via `on_update`
- Sends a **real-time system notification** to all users with the `Purchase Manager` role
- Sends an **email notification** if an outgoing email account is configured

---

## File Structure

```
procurement_management/
├── procurement_management/
│   ├── doctype/
│   │   └── procurement_requisition/
│   │       ├── procurement_requisition.json   ← DocType definition
│   │       ├── procurement_requisition.py     ← Controller, validations, RFQ method
│   │       └── procurement_requisition.js     ← Client script, Create RFQ button
│   ├── report/
│   │   └── procurement_requisition_report/
│   │       ├── procurement_requisition_report.json
│   │       ├── procurement_requisition_report.py
│   │       └── procurement_requisition_report.js
│   ├── fixtures/
│   │   └── workflow.json                      ← Workflow definition
│   └── hooks.py                               ← App hooks, fixtures config
└── README.md
```

---

## Developer Notes

- All customizations are in a portable custom app — no in-app customizations used
- Workflow is exported as a fixture and auto-imported on `bench migrate`
- Server-side validation is the authoritative layer; client-side is UX only
- Email notification gracefully skips if no outgoing email account is configured
