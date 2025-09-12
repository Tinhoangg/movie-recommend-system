"""
send_30_emails.py
Tạo 30 email (5 label, mỗi label 6 mail) và gửi đến 1 email cụ thể.
Yêu cầu: credentials.json (OAuth2) trong cùng thư mục.
"""

import base64
import os
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Quyền Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Danh sách label
LABEL_NAMES = ["newsletter", "ads", "invoice", "reminder", "other"]

# Email người nhận duy nhất
RECIPIENT = "riseofkingdom111a@gmail.com"   # <-- thay bằng email thật

# ========== STEP 1: AUTH =============
def gmail_auth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

# ========== STEP 2: LABEL ============
def get_or_create_labels(service):
    existing = service.users().labels().list(userId='me').execute().get('labels', [])
    name_to_id = {l['name']: l['id'] for l in existing}
    for name in LABEL_NAMES:
        if name not in name_to_id:
            body = {"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
            created = service.users().labels().create(userId='me', body=body).execute()
            name_to_id[name] = created['id']
            print(f"Tạo label: {name}")
    return name_to_id

# ========== STEP 3: CREATE MESSAGE ============
def create_message(sender, to, subject, body_text):
    message = MIMEText(body_text, "plain", "utf-8")
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, message_body):
    return service.users().messages().send(userId='me', body=message_body).execute()

def add_label(service, msg_id, label_id):
    body = {'addLabelIds': [label_id], 'removeLabelIds': []}
    service.users().messages().modify(userId='me', id=msg_id, body=body).execute()

# ========== STEP 4: TẠO 30 EMAIL ============
def prepare_30_emails():
    templates = {
        "newsletter": ("Bản tin tháng", "Chào bạn,\nĐây là bản tin cập nhật mới nhất."),
        "ads": ("Khuyến mãi hot", "Xin chào,\nChúng tôi gửi tới bạn chương trình giảm giá đặc biệt."),
        "invoice": ("Hóa đơn dịch vụ", "Kính gửi khách hàng,\nĐây là hóa đơn dịch vụ của bạn."),
        "reminder": ("Nhắc lịch quan trọng", "Xin nhắc bạn về sự kiện sắp tới."),
        "other": ("Thông báo chung", "Xin lưu ý một số thông tin quan trọng.")
    }

    subjects, bodies, labels = [], [], []
    for label in LABEL_NAMES:
        subj_base, body_base = templates[label]
        for i in range(1, 7):  # mỗi label 6 email
            subjects.append(f"{subj_base} #{i}")
            bodies.append(f"{body_base}\n\n(Email {i} thuộc label: {label})")
            labels.append(label)
    return subjects, bodies, labels

# ========== MAIN ============
def main():
    service = gmail_auth()
    label_map = get_or_create_labels(service)

    subjects, bodies, labels = prepare_30_emails()
    sender = "me"

    for idx in range(30):
        subject = subjects[idx]
        body = bodies[idx]
        label_name = labels[idx]
        label_id = label_map[label_name]

        msg_body = create_message(sender, RECIPIENT, subject, body)
        sent = send_message(service, msg_body)
        msg_id = sent.get('id')
        add_label(service, msg_id, label_id)

        print(f"[{idx+1}/30] Sent to {RECIPIENT} | Subject: {subject} | Label: {label_name}")

if __name__ == "__main__":
    main()

