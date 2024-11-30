# Copyright (c) 2024, Touhid Mullick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HelpDesk(Document):
	def validate(self):
		self.validate_response()
	def before_update_after_submit(self):
		self.validate_response()
		
	def validate_response(self):
		if frappe.session.user != "Administrator":
			if self.response:
				if not self.name or not frappe.db.exists("Help Desk", self.name):
					frappe.throw("Cannot Create Response When Raising A Ticket")
				if frappe.db.get_value("Help Desk", self.name, "status") != "Pending" and frappe.db.get_value("Help Desk", self.name, "response") != self.response:
					frappe.throw("Cannot Create/Change Response When Ticket Status Is Not Pending")
				if frappe.db.get_value("Help Desk", self.name, "status") == "Pending":
					if not any(role in ["HR Manager", "HR User"] for role in frappe.get_roles(frappe.session.user)):
						frappe.throw("Only HR Manager and HR User Can Create Response")
