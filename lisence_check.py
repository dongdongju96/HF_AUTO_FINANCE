import os
import json
from pprint import pprint
from dotenv import load_dotenv
from google.cloud import vision
from pyairtable import Api


class AirtableAPI:
    def __init__(self, api_key, base_id, table_name):
        self.api = Api(api_key)
        self.table = self.api.table(base_id, table_name)
    
    def get_all_records(self):
        """Retrieve all records from Airtable"""
        return self.table.all()

    def update_record(self, record_id, fields):
        """Update a record in Airtable"""
        self.table.update(record_id, fields)


class GoogleVisionAPI:
    def __init__(self, credentials):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
        self.client = vision.ImageAnnotatorClient()

    def detect_text(self, uri):
        """Detects text in the image provided by the URI"""
        image = vision.Image()
        image.source.image_uri = uri
        response = self.client.text_detection(image=image)
        texts = response.text_annotations

        if response.error.message:
            raise Exception(f"Error: {response.error.message}")

        texts_list = [text.description for text in texts]
        structured_texts = [{
            "description": text.description,
            "bounding_poly": [{"x": vertex.x, "y": vertex.y} for vertex in text.bounding_poly.vertices]
        } for text in texts]

        return texts_list, structured_texts


class LicenseDetection:
    def __init__(self, airtable_client, vision_client, license_keywords):
        self.airtable_client = airtable_client
        self.vision_client = vision_client
        self.license_keywords = license_keywords

    def detect_license_in_image(self, uri, client_data_id):
        """Detect text in the image, save result to JSON"""
        texts_list, structured_texts = self.vision_client.detect_text(uri)

        output_data = {
            "texts": structured_texts,
            "texts_list": texts_list
        }

        output_file_path = f"./image_detection_output/{client_data_id}.json"
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)

        return texts_list

    def check_keywords_in_texts(self, texts_list):
        """Check for license keywords in detected texts"""
        found_keywords = [keyword for keyword in self.license_keywords if keyword in texts_list]
        return found_keywords

    def perform_task_for_keyword(self, keyword, client_data_id):
        """Perform task based on detected license keyword"""
        if keyword == 'G1':
            self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "G1 license"})
        elif keyword == 'G':
            pass
        elif keyword == 'G2':
            pass
        else:
            self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "Can't find license CLASS"})

    def process_records(self):
        """Process records from Airtable and detect licenses"""
        table_list = self.airtable_client.get_all_records()
        
        for record in table_list:
            if "Driver's License" in record["fields"] and record["fields"]["Status"] == "New Lead":
                client_data_id = record["id"]
                uri = record["fields"]["Driver's License"][0]["url"]

                texts_list = self.detect_license_in_image(uri, client_data_id)
                found_keywords = self.check_keywords_in_texts(texts_list)

                if found_keywords:
                    for keyword in found_keywords:
                        self.perform_task_for_keyword(keyword, client_data_id)
                else:
                    self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "Can't find license CLASS"})

            elif "Driver's License" not in record["fields"] and record["fields"]["Status"] == "New Lead":
                self.airtable_client.update_record(record["id"], {"Status": "Follow Up", "Notes": "No image URL"})
            else:
                # Update the status when the image URL is not available or the status is not 'New Lead'
                pass


# Main execution

# Load environment variables
load_dotenv()
AIRTABLE_API_KEY = os.getenv("AIRTABLE_WRITE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
LICENSE_KEYWORDS = ["G", "G1", "G2"]

# Initialize Airtable and Google Vision clients
airtable_client = AirtableAPI(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
vision_client = GoogleVisionAPI(GOOGLE_APPLICATION_CREDENTIALS)

# Initialize LicenseDetection
license_detection = LicenseDetection(airtable_client, vision_client, LICENSE_KEYWORDS)

# Process records and perform tasks
license_detection.process_records()
