frappe.query_reports["Procurement Requisition Report"] = {
    filters: [
        {
            fieldname: "department",
            label: "Department",
            fieldtype: "Link",
            options: "Department",
        },
        {
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options: "\nDraft\nPending Department Review\nPending Finance Review\nApproved\nRejected",
        },
    ],
};
