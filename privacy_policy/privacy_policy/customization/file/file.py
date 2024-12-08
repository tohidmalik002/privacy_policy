import frappe

def after_insert(doc, method = None):
    frappe.enqueue(upload_file_to_google_drive, doc=doc)


def upload_file_to_google_drive(doc):
    if doc.attached_to_doctype == "Employee":
        from googleapiclient.http import MediaFileUpload

        doctype = doc.attached_to_doctype
        docname = doc.attached_to_name
        document_type = get_document_type(doc.attached_to_field)
        drive_service = get_google_drive_service()
        organization_parent = "1PxB37AaU9qdN7Abt25zld5Wo7pgf7sH2"
        doctype_folder_id = get_folder_id(drive_service, doctype, organization_parent)
        record_folder_id = get_folder_id(drive_service, docname, doctype_folder_id)
        document_type_folder_id = get_folder_id(drive_service, document_type, record_folder_id)
        file_path = frappe.get_site_path('private' if doc.is_private else 'public', doc.file_url.strip('/'))
        file_metadata = {'name': doc.file_name,
                         'parents': [document_type_folder_id]
                         }
        media = MediaFileUpload(file_path, resumable=True)
        drive_file = drive_service.files().create(
            body=file_metadata, media_body=media, fields='id'
        ).execute()
        frappe.db.set_value("File", doc.name, "google_drive_backup", 1)
        frappe.db.set_value("File", doc.name, "google_drive_file_id", drive_file.get("id"))

def get_folder_id(service, folder_name, parent_folder_id):
    query = (
        f"name = '{folder_name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"'{parent_folder_id}' in parents"
    )
    results = service.files().list(
        q=query,
        fields="files(id, name)",
        pageSize=1
    ).execute()
    
    folders = results.get('files', [])
    
    if folders:
        folder_id = folders[0]['id']
        return folder_id
    else:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        created_folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        folder_id = created_folder.get('id')
        return folder_id



def get_authenticated_user_info():
    """Get details of the account tied to the Google Drive service."""
    service = get_google_drive_service()  # Ensure proper initialization of the Drive service
    about_info = service.about().get(fields="user").execute()
    user_info = about_info.get('user', {})
    
    print(user_info)

def get_google_drive_service():
    from googleapiclient.discovery import build
    credentials = get_service_account_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service


def get_service_account_credentials():
    from google.oauth2 import service_account

    SERVICE_ACCOUNT_INFO = frappe.conf.google_drive_credentials
    SCOPES = ['https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)

    return credentials

def get_document_type(field_name):
    document_field_map = {
        "aadhar_card": "Aadhar Card",
        "pan_card": "Pan Card",
        "results": "Results"
    }
    return document_field_map.get(field_name, "Other Documents")




