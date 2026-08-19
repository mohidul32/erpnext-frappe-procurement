import frappe

def create_proc_item():
    if not frappe.db.exists("Item", "PROC-ITEM"):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": "PROC-ITEM",
            "item_name": "Procurement Item",
            "item_group": "All Item Groups",
            "stock_uom": "Nos",
            "is_stock_item": 0,
        })
        item.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Item PROC-ITEM created")
    else:
        print("Already exists:", frappe.db.get_value("Item", "PROC-ITEM", "name"))
