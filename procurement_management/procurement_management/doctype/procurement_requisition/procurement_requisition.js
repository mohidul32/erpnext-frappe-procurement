frappe.ui.form.on("Procurement Requisition", {
    refresh(frm) {
        // Show Create RFQ button only when Approved
        if (frm.doc.workflow_state === "Approved" && !frm.doc.__islocal) {
            frm.add_custom_button("Create RFQ", () => {
                frappe.confirm(
                    `Are you sure you want to create a Request for Quotation for <b>${frm.doc.name}</b>?`,
                    () => {
                        frappe.call({
                            method: "procurement_management.procurement_management.doctype.procurement_requisition.procurement_requisition.create_rfq",
                            args: { procurement_requisition: frm.doc.name },
                            callback(r) {
                                if (r.message) {
                                    frappe.set_route("Form", "Request for Quotation", r.message);
                                }
                            },
                        });
                    }
                );
            }, "Actions");
        }
    },

    quantity(frm) {
        if (frm.doc.quantity <= 0) {
            frappe.msgprint("Quantity must be greater than zero.");
            frm.set_value("quantity", "");
        }
    },

    estimated_budget(frm) {
        if (frm.doc.estimated_budget <= 0) {
            frappe.msgprint("Estimated Budget must be greater than zero.");
            frm.set_value("estimated_budget", "");
        }
    },

    required_date(frm) {
        if (frm.doc.required_date && frm.doc.required_date < frappe.datetime.get_today()) {
            frappe.msgprint("Required Date cannot be earlier than today's date.");
            frm.set_value("required_date", "");
        }
    },
});
