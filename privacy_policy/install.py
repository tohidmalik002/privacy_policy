from frappe.desk.page.setup_wizard.setup_wizard import make_records
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    print("Creating/Updating Fixtures for Privacy Policy")
    create_custom_fields(get_custom_fields(), ignore_validate=True)
    make_fixtures()
    insert_privacy_policy_in_home_workspace()

def before_unsintall():
    remove_fixtures()
    delete_custom_fields(get_custom_fields())



def get_custom_fields():
    return {
		"Employee": [
			{
				"fieldname": "documents_tab",
				"fieldtype": "Tab Break",
				"label": "Documents",
				"insert_after": "internal_work_history",
			},
			{
				"fieldname": "aadhar_card",
				"fieldtype": "Attach",
				"label": "Aadhar Card",
				"insert_after": "documents_tab",
			},
            {
				"fieldname": "results",
				"fieldtype": "Attach",
				"label": "Results",
				"insert_after": "column_break_epbgu",
			},
            {
				"fieldname": "column_break_epbgu",
				"fieldtype": "Column Break",
				"insert_after": "pan_card",
			}, 
            {
				"fieldname": "pan_card",
				"fieldtype": "Attach",
				"label": "Pan Card",
				"insert_after": "aadhar_card",
			}    
        ],
        "File": [
			{
				"fieldname": "google_drive_backup",
				"fieldtype": "Check",
				"label": "Google Drive Backup",
				"insert_after": "attached_to_doctype",
                "read_only": 1
			},
			{
				"fieldname": "google_drive_file_id",
				"fieldtype": "Data",
				"label": "Google Drive File ID",
				"insert_after": "google_drive_backup",
                "read_only": 1
			}     
        ]
    }


def delete_custom_fields(custom_fields: dict):
	for doctype, fields in custom_fields.items():
		frappe.db.delete(
			"Custom Field",
			{
				"fieldname": ("in", [field["fieldname"] for field in fields]),
				"dt": doctype,
			},
		)

		frappe.clear_cache(doctype=doctype)

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