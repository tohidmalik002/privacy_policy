from frappe.desk.page.setup_wizard.setup_wizard import make_records
import frappe


def after_install():
    print("Creating/Updating Fixtures for Privacy Policy")
    make_fixtures()
    insert_privacy_policy_in_home_workspace()

def before_unsintall():
    remove_fixtures()


def make_fixtures():
	records = [
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Draft",
			"__condition": lambda: not frappe.db.exists("Workflow State", "Draft")
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Pending",
			"__condition": lambda: not frappe.db.exists("Workflow State", "Pending")

		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Resolved",
			"__condition": lambda: not frappe.db.exists("Workflow State", "Resolved")

		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Cancelled",
			"__condition": lambda: not frappe.db.exists("Workflow State", "Cancelled")

		},
		{
			"doctype": "Workflow Action Master",
			"workflow_action_name": "Raise Ticket",
			"__condition": lambda: not frappe.db.exists("Workflow Action Master", "Raise Ticket")

		},
		{
			"doctype": "Workflow Action Master",
			"workflow_action_name": "Submit",
			"__condition": lambda: not frappe.db.exists("Workflow Action Master", "Submit")

		},
		{
			"doctype": "Workflow Action Master",
			"workflow_action_name": "Cancel",
			"__condition": lambda: not frappe.db.exists("Workflow Action Master", "Cancel")
		},
		{
			"doctype": "Workflow",
            "workflow_name": "Help Desk",
            "document_type": "Help Desk",
            "is_active": 1,
            "override_status": 1,
            "transitions": [
                {            
                    "state": "Draft",
                    "action": "Raise Ticket",
                    "next_state": "Pending",
                    "allowed": "All",
                },
                {
            
                    "state": "Pending",
                    "action": "Submit",
                    "next_state": "Resolved",
                    "allowed": "HR User",
                },
                {
                    "state": "Pending",
                    "action": "Cancel",
                    "next_state": "Cancelled",
                    "allowed": "HR User",
                }
            ],
            "states": [
                {
                    "state": "Draft",
                    "doc_status": "0",
                    "update_field": "status",
                    "update_value": "Draft",
                    "allow_edit": "All",
                },
                {
                    "state": "Pending",
                    "doc_status": "1",
                    "update_field": "status",
                    "update_value": "Pending",
                    "allow_edit": "HR User",
                },
                {
                    "state": "Resolved",
                    "doc_status": "1",
                    "update_field": "status",
                    "update_value": "Resolved",
                    "allow_edit": "HR User",
                },
                {

                    "state": "Cancelled",
                    "doc_status": "2",
                    "update_field": "status",
                    "update_value": "Cancelled",
                    "allow_edit": "HR User",
                }
            ],
			"__condition": lambda: not frappe.db.exists("Workflow", "Help Desk")
        }
	]
	make_records(records)

def insert_privacy_policy_in_home_workspace():
    if not frappe.db.exists("Workspace Shortcut", {
        "type": "Page",
        "link_to": "privacy-policy"
    }):
        doc = frappe.get_doc("Workspace", "Home")
        doc.append("shortcuts", {
            "type": "Page",
            "link_to": "privacy-policy",
            "label": "Privacy Policy",
            "parent": "Home"
        })
        doc.save()

def set_system_notification_for_help_desk():
    if not frappe.db.exists("Notification", "Help Desk"):
            doc = {
                "name": 'Help Desk',
                "doctype": "Notification",
                "enabled": 1,
                "channel": "System Notification",
                "subject": "Query Update",
                "event": "Value Change",
                "document_type": "Help Desk",
                "value_changed": "status",
                "send_system_notification": 1,
                "condition": "doc.status == \"Resolved\" or doc.status == \"Cancelled\"",
                "send_to_all_assignees": 0,
                "doctype": "Notification",
                "recipients": [
                    {
                        "receiver_by_document_field": "owner",
                    }
                ],
            }
            frappe.get_doc(doc).insert()

def remove_fixtures():
    if frappe.db.exists("Workflow", "Help Desk"):
        frappe.delete_doc("Workflow", "Help Desk")
    if frappe.db.exists("Notification", "Help Desk"):
        frappe.delete_doc("Notification", "Help Desk")