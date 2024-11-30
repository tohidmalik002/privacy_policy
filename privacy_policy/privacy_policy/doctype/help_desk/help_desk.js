// Copyright (c) 2024, Touhid Mullick and contributors
// For license information, please see license.txt

frappe.ui.form.on("Help Desk", {
	refresh(frm) {
        if ((frappe.user_roles.includes("HR Manager") || frappe.user_roles.includes("HR User")) && frm.doc.status == "Pending") {
            frm.set_df_property("response", "hidden", 0);
            frm.set_df_property("response", "read_only", 0);
        }
        if (frm.doc.status == "Resolved") {
            frm.set_df_property("response", "hidden", 0);
            frm.set_df_property("response", "read_only", 1);
        }
	},
});
