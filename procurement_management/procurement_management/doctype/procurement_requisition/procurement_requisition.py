import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class ProcurementRequisition(Document):

    def validate(self):
        self.validate_quantity()
        self.validate_estimated_budget()
        self.validate_required_date()

    def validate_quantity(self):
        if self.quantity <= 0:
            frappe.throw("Quantity must be greater than zero.")

    def validate_estimated_budget(self):
        if self.estimated_budget <= 0:
            frappe.throw("Estimated Budget must be greater than zero.")

    def validate_required_date(self):
        if getdate(self.required_date) < getdate(today()):
            frappe.throw("Required Date cannot be earlier than today's date.")

    def on_update(self):
        if not self.workflow_state:
            return

        # Sync status field with workflow state
        frappe.db.set_value("Procurement Requisition", self.name, "status", self.workflow_state, update_modified=False)

        # Send notification when Approved
        if self.workflow_state == "Approved":
            self.notify_administration()

    def notify_administration(self):
        # Get all users with Purchase Manager role (Administration team)
        admin_users = frappe.get_all(
            "Has Role",
            filters={"role": "Purchase Manager", "parenttype": "User"},
            fields=["parent"],
        )

        for user in admin_users:
            frappe.publish_realtime(
                event="msgprint",
                message=f"Procurement Requisition {self.name} has been Approved and is ready for RFQ.",
                user=user.parent,
            )

        # Send email only if outgoing email is configured
        outgoing_email = frappe.db.get_value("Email Account", {"enable_outgoing": 1, "default_outgoing": 1}, "name")
        if not outgoing_email:
            return

        for user in admin_users:
            frappe.sendmail(
                recipients=[user.parent],
                subject=f"Procurement Requisition {self.name} Approved",
                message=f"""
                    <p>Dear Team,</p>
                    <p>Procurement Requisition <strong>{self.name}</strong> has been approved.</p>
                    <ul>
                        <li><strong>Item:</strong> {self.item_description}</li>
                        <li><strong>Quantity:</strong> {self.quantity}</li>
                        <li><strong>Estimated Budget:</strong> {self.estimated_budget}</li>
                        <li><strong>Requested By:</strong> {self.requested_by}</li>
                        <li><strong>Department:</strong> {self.department}</li>
                    </ul>
                    <p>Please initiate the Request for Quotation process.</p>
                """,
                now=True,
            )


@frappe.whitelist()
def create_rfq(procurement_requisition):
    doc = frappe.get_doc("Procurement Requisition", procurement_requisition)

    if doc.workflow_state != "Approved":
        frappe.throw("RFQ can only be created for Approved requisitions.")

    rfq = frappe.new_doc("Request for Quotation")
    rfq.transaction_date = today()
    rfq.status = "Draft"
    rfq.message_for_supplier = f"Procurement Requisition: {doc.name}\nItem: {doc.item_description}\nJustification: {doc.justification}"

    rfq.append("items", {
        "item_code": "PROC-ITEM",
        "item_name": doc.item_description,
        "description": doc.item_description,
        "qty": doc.quantity,
        "uom": "Nos",
        "stock_uom": "Nos",
        "conversion_factor": 1,
        "schedule_date": doc.required_date,
        "rate": doc.estimated_budget / doc.quantity if doc.quantity else 0,
    })

    rfq.insert(ignore_permissions=True, ignore_mandatory=True)

    frappe.msgprint(
        f"Request for Quotation <b>{rfq.name}</b> created successfully.",
        title="RFQ Created",
        indicator="green",
    )

    return rfq.name
