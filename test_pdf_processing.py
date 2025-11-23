#!/usr/bin/env python
"""
Test script to demonstrate PDF processing with Celery
"""
import requests
import time
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api/pdf"


def test_pdf_processing():
    """Test the PDF processing workflow"""

    print("🚀 Testing PDF Processing with Celery and RabbitMQ")
    print("=" * 50)

    # Check if we have any PDF files in the current directory
    pdf_files = list(Path("./Test").glob("*.pdf"))

    if not pdf_files:
        print("❌ No PDF files found in current directory")
        print("📝 To test the system, place a PDF file in the current directory")
        print("   or modify this script to point to an existing PDF file")
        return

    # Use the first PDF file found
    pdf_file = pdf_files[0]
    print(f"📄 Found PDF file: {pdf_file}")

    # Test 1: Upload PDF
    print("\n1️⃣ Uploading PDF file...")
    with open(pdf_file, "rb") as f:
        files = {"file": f}
        data = {"title": f"Test Document - {pdf_file.name}"}

        response = requests.post(f"{BASE_URL}/upload/", files=files, data=data)

    if response.status_code == 201:
        result = response.json()
        document_id = result["document_id"]
        task_id = result["task_id"]
        print(f"✅ Upload successful!")
        print(f"   Document ID: {document_id}")
        print(f"   Task ID: {task_id}")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return

    # Test 2: Check document status
    print(f"\n2️⃣ Checking document status...")
    response = requests.get(f"{BASE_URL}/documents/{document_id}/status/")

    if response.status_code == 200:
        status_data = response.json()
        print(f"✅ Status retrieved:")
        print(f"   Title: {status_data['title']}")
        print(f"   Status: {status_data['processing_status']}")
        print(f"   File Size: {status_data['file_size']} bytes")
    else:
        print(f"❌ Status check failed: {response.status_code}")

    # Test 3: Monitor processing
    print(f"\n3️⃣ Monitoring processing progress...")
    max_attempts = 30  # Wait up to 30 seconds
    attempt = 0

    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/documents/{document_id}/status/")

        if response.status_code == 200:
            status_data = response.json()
            current_status = status_data["processing_status"]

            print(f"   Status: {current_status} (attempt {attempt + 1}/{max_attempts})")

            if current_status == "completed":
                print("✅ Processing completed!")
                break
            elif current_status == "failed":
                print(
                    f"❌ Processing failed: {status_data.get('error_message', 'Unknown error')}"
                )
                return
            elif current_status == "processing":
                print("   ⏳ Processing in progress...")

            time.sleep(1)
            attempt += 1
        else:
            print(f"❌ Status check failed: {response.status_code}")
            break

    if attempt >= max_attempts:
        print("⏰ Processing timeout - check manually")
        return

    # Test 4: Get extracted content
    print(f"\n4️⃣ Retrieving extracted content...")
    response = requests.get(f"{BASE_URL}/documents/{document_id}/content/")

    if response.status_code == 200:
        content_data = response.json()
        print(f"✅ Content retrieved:")
        print(f"   Title: {content_data['title']}")
        print(f"   Page Count: {content_data['page_count']}")
        print(f"   Text Length: {len(content_data['extracted_text'])} characters")

        # Show first 200 characters of extracted text
        text_preview = content_data["extracted_text"][:200]
        print(f"   Text Preview: {text_preview}...")

        # Show metadata if available
        if content_data["metadata"]:
            print(f"   Metadata: {content_data['metadata']}")
    else:
        print(f"❌ Content retrieval failed: {response.status_code}")

    # Test 5: List all documents
    print(f"\n5️⃣ Listing all documents...")
    response = requests.get(f"{BASE_URL}/documents/")

    if response.status_code == 200:
        docs_data = response.json()
        print(f"✅ Found {docs_data['total_count']} documents:")
        for doc in docs_data["documents"]:
            print(f"   - {doc['title']} ({doc['processing_status']})")
    else:
        print(f"❌ Document listing failed: {response.status_code}")

    print(f"\n🎉 Test completed successfully!")
    print(
        f"📊 You can also check the RabbitMQ management interface at: http://localhost:15672"
    )
    print(f"   Username: guest, Password: guest")


if __name__ == "__main__":
    test_pdf_processing()
