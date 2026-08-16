import os
import requests
import time
import argparse


def get_twenty_url():
    return os.environ.get("TWENTY_API_URL", "http://localhost:3000")


def get_api_key():
    key = os.environ.get("TWENTY_API_KEY")
    if not key:
        raise ValueError("TWENTY_API_KEY environment variable is required")
    return key


def create_custom_object(name, label_plural, fields):
    """
    In a real Twenty CRM setup, creating custom objects requires hitting the Workspace Metadata API
    or using their GraphQL endpoint.
    This simulates the payload for creating an 'InteractionLog' object.
    """
    url = f"{get_twenty_url()}/rest/metadata/objects"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    payload = {
        "name": name,
        "labelPlural": label_plural,
        "labelSingular": name,
        "description": f"Custom object for {name}",
        "icon": "IconPhoneCall",
        "fields": fields,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Successfully created custom object: {name}")
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(
            f"Failed to create custom object {name}. Status: {e.response.status_code}"
        )
        print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None


def bootstrap():
    print("Starting CRM Bootstrap...")
    time.sleep(1)  # simulate connection delay

    interaction_log_fields = [
        {"name": "tenantId", "type": "TEXT", "label": "Tenant ID", "isRequired": True},
        {"name": "roomName", "type": "TEXT", "label": "Room Name", "isRequired": True},
        {"name": "durationSeconds", "type": "NUMBER", "label": "Duration (s)"},
        {"name": "summary", "type": "TEXT_LONG", "label": "Call Summary"},
        {"name": "recordingUrl", "type": "TEXT", "label": "Recording URL"},
    ]

    create_custom_object("interactionLog", "Interaction Logs", interaction_log_fields)
    print(
        "Bootstrap complete. Remember to restart Twenty CRM so it picks up the metadata schema changes."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bootstrap Twenty CRM Custom Objects for A.L.F.I.E"
    )
    args = parser.parse_args()

    try:
        get_api_key()  # verify key exists
        bootstrap()
    except ValueError as e:
        print(f"ERROR: {e}")
        print("Please generate an API key from the Twenty CRM settings and export it:")
        print("export TWENTY_API_KEY='your_key_here'")
