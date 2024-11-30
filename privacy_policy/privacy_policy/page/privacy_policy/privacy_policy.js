frappe.pages['privacy-policy'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Privacy Policy',
		single_column: true
	});
	page.add_button(__('Raise A Ticket'), function() {
        frappe.new_doc('Help Desk');
    });
	
	frappe.call({
		method: 'frappe.desk.form.load.getdoc',
		args: {
			"doctype": "Company Privacy Policy",
			"name": "Company Privacy Policy"
		},
		callback: function(response) {
			doc = {}
			if (response.docs){
				doc = response.docs[0]
			}
			console.log(doc)
			$(frappe.render_template("privacy_policy", {doc: doc})).appendTo(page.body);
		},
		error: function(error) {
			$(frappe.render_template("privacy_policy", {doc: error})).appendTo(page.body);
		},
		freeze: true,  // Optional: freeze the UI during the call (display a loading screen)
		freeze_message: 'Loading...',  // Optional: custom message while the UI is frozen
	});
}

document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
});

document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'p') {
    event.preventDefault();
    }
});    