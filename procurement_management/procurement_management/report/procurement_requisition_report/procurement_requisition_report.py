import frappe


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": "Requisition No.",
            "fieldtype": "Link",
            "options": "Procurement Requisition",
            "width": 160,
        },
        {
            "fieldname": "request_date",
            "label": "Request Date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "requested_by",
            "label": "Requested By",
            "fieldtype": "Link",
            "options": "User",
            "width": 180,
        },
        {
            "fieldname": "department",
            "label": "Department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 160,
        },
        {
            "fieldname": "item_description",
            "label": "Item Description",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "estimated_budget",
            "label": "Estimated Budget",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Data",
            "width": 160,
        },
    ]


def get_data(filters):
    conditions = {}

    if filters.get("department"):
        conditions["department"] = filters["department"]

    if filters.get("status"):
        conditions["status"] = filters["status"]

    return frappe.get_all(
        "Procurement Requisition",
        filters=conditions,
        fields=[
            "name",
            "request_date",
            "requested_by",
            "department",
            "item_description",
            "estimated_budget",
            "status",
        ],
        order_by="request_date desc",
    )
