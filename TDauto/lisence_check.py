import os
import json
from pprint import pprint
from pyairtable import Api
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import vision
from input_data import DealerTrackAutomation



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
    
        # output_file_path = os.path.join(r"C:\Users\HF\Desktop\airtable\TDauto\image_detection_output", f"{client_data_id}.json")
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
            pass
            self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "Need at least G2 license(AI)"})
        elif keyword == 'G':
            self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "Need at least G2 license(AI)"})
        elif keyword == 'G2':
            print("G2 liscence")
            print(f"client_data_id : {client_data_id}")
            # Dealer check 매크로 실행
            # Dealer check에 고객 데이터 값 입력
            # AIRTABLE_CLIENT_DATA_ID값과 table_list_current_date.json을 조회해서 ID 값과 비교 후 매크로 값 입력
            automation = DealerTrackAutomation()
            try:
                automation.run(client_data_id)
            except:
                self.airtable_client.update_record(client_data_id, {"Notes": "Can't input Data with AI"})
                
            self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "Auto input Done"})
        else:
            self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "Can't find license CLASS(AI)"})

    def process_records(self):
        """Process records from Airtable and detect licenses"""
        table_list = self.airtable_client.get_all_records()
        # 현재 날짜를 파일 이름에 추가
        current_date = datetime.now().strftime('%Y-%m-%d')  # "YYYY-MM-DD" 형식
        # file_name = os.path.join(r"C:\Users\HF\Desktop\airtable\TDauto\airtable_data", f"table_list_{current_date}.json")
        file_name = os.path.join(".", "airtable_data", f"table_list_{current_date}.json")

        # 데이터를 JSON 파일로 저장
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(table_list, file, ensure_ascii=False, indent=4)

        print(f"Data saved to {file_name}")
        
        for record in table_list:
            if "Driver's License" in record["fields"] and record["fields"]["Status"] == "New Lead": # and record["fields"]["First Name"] == "Test":
                client_data_id = record["id"]
                uri = record["fields"]["Driver's License"][0]["url"]
                ## 이미지 디텍션한 파일이 있는지 확인
                output_file_path = f"./image_detection_output/{client_data_id}.json"
                if os.path.exists(output_file_path):
                    with open(output_file_path, 'r', encoding='utf-8') as file:
                        texts_list = json.load(file)
                        texts_list = texts_list['texts_list']
                    print("이미 인식한 이미지입니다.")
                else:
                    texts_list = self.detect_license_in_image(uri, client_data_id)
                    print("이미지 인식을 실행합니다..")

                found_keywords = self.check_keywords_in_texts(texts_list)

                if found_keywords:
                    for keyword in found_keywords:

                        self.perform_task_for_keyword(keyword, client_data_id)
                else:
                    self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "Can't find license CLASS(AI)"})

            elif "Driver's License" not in record["fields"] and record["fields"]["Status"] == "New Lead":
                self.airtable_client.update_record(record["id"], {"Status": "Follow Up", "Notes": "No image URL(AI)"})
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
