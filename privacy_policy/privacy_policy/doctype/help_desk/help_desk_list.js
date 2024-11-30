frappe.listview_settings["Help Desk"] = {
	get_indicator: function (doc) {
		const status_colors = {
			Draft: "grey",
			Pending: "orange",
			Resolved: "green",
			Cancelled: "red",
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},

};
