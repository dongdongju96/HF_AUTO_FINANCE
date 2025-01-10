import os
import re
import json
import requests
from pprint import pprint
from pyairtable import Api
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import vision
from google.cloud import storage
from google.oauth2 import service_account
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
        credentials = service_account.Credentials.from_service_account_file(
            credentials
        )
        self.client = vision.ImageAnnotatorClient()
        self.storage_client = storage.Client(credentials=credentials)

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
    
    def upload_file_to_gcs(self, bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the specified GCS bucket."""
        
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    def async_detect_document(self, gcs_source_uri, gcs_destination_uri, batch_size=2):
        """Performs asynchronous document OCR on a PDF file stored in GCS."""
        feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
        gcs_source = vision.GcsSource(uri=gcs_source_uri)
        input_config = vision.InputConfig(gcs_source=gcs_source, mime_type="application/pdf")
        gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
        output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

        async_request = vision.AsyncAnnotateFileRequest(
            features=[feature], input_config=input_config, output_config=output_config
        )
        operation = self.client.async_batch_annotate_files(requests=[async_request])
        print("Waiting for the operation to finish...")
        operation.result(timeout=420)

        # Retrieve output files from GCS
        bucket_name, prefix = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri).groups()
        bucket = self.storage_client.bucket(bucket_name)
        blob_list = [blob for blob in bucket.list_blobs(prefix=prefix) if not blob.name.endswith("/")]

        output_data = []
        for blob in blob_list:
            json_string = blob.download_as_bytes().decode("utf-8")
            response = json.loads(json_string)
            output_data.append(response)

        return output_data


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
    
    def detect_license_in_pdf(self, gcs_source_uri, gcs_destination_uri, client_data_id):
        """Process the PDF, extract text, and save results."""
        output_data = self.vision_client.async_detect_document(gcs_source_uri, gcs_destination_uri)

        # Save results to a JSON file
        output_file_path = f"./image_detection_output/{client_data_id}.json"
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        return output_data

    def check_keywords_in_texts(self, texts_list):
        """Check for license keywords in detected texts"""
        found_keywords = [keyword for keyword in self.license_keywords if keyword in texts_list]
        return found_keywords

    def perform_task_for_keyword(self, keyword, client_data_id, origin_notes):
        """Perform task based on detected license keyword"""
        if keyword == 'G1':
            self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": f"{origin_notes} - Need at least G1 license(AI)"})

        elif keyword == 'G' or keyword == 'A' or keyword == 'AZ' or keyword == 'B' or keyword == 'C' or keyword == 'D' or keyword == 'E' or keyword == 'F':
            print("G liscence")
            print(f"client_data_id : {client_data_id}")
            # Dealer check 매크로 실행
            # Dealer check에 고객 데이터 값 입력
            # AIRTABLE_CLIENT_DATA_ID값과 table_list_current_date.json을 조회해서 ID 값과 비교 후 매크로 값 입력
            automation = DealerTrackAutomation()
            try:
                automation.run(airtable_client, client_data_id)
            except:
                self.airtable_client.update_record(client_data_id, {"Notes": f"{origin_notes} - Can't input Data with AI"})
                
            # self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": "Auto input Done"})

        elif keyword == 'G2':
            print("G2 liscence")
            print(f"client_data_id : {client_data_id}")
            # Dealer check 매크로 실행
            # Dealer check에 고객 데이터 값 입력
            # AIRTABLE_CLIENT_DATA_ID값과 table_list_current_date.json을 조회해서 ID 값과 비교 후 매크로 값 입력
            automation = DealerTrackAutomation()
            try:
                automation.run(airtable_client, client_data_id)
                self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": f"{origin_notes} - Auto input Done"})
            except:
                self.airtable_client.update_record(client_data_id, {"Notes": f"{origin_notes} - Can't input Data with AI"})
                
        else:
            self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": f"{origin_notes} - Can't find license CLASS(AI)"})

    def process_records(self):
        """Process records from Airtable and detect licenses"""
        table_list = self.airtable_client.get_all_records()
        # 현재 날짜를 파일 이름에 추가
        current_date = datetime.now().strftime('%Y-%m-%d')  # "YYYY-MM-DD" 형식
        # file_name = os.path.join(r"C:\Users\HF\Desktop\airtable\TDauto\airtable_data", f"table_list_{current_date}.json")
        file_name = os.path.join(".", "airtable_data", f"table_list_{current_date}.json")
        print(file_name)

        # 데이터를 JSON 파일로 저장
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(table_list, file, ensure_ascii=False, indent=4)

        print(f"Data saved to {file_name}")
        
        cus_phone_numer = input("Enter the customer's phone number: ")
        for record in table_list:
            if "Driver's License" in record["fields"] and record["fields"]["Status"] == "New Lead" and record["fields"]["Phone"]==int(cus_phone_numer) and record["fields"]["First Name"] == "TEST":
                client_data_id = record["id"]
                uri = record["fields"]["Driver's License"][0]["url"]
                origin_notes = record["fields"]["Notes"]

                ## 이미지 디텍션한 파일이 있는지 확인
                output_file_path = f"image_detection_output/{client_data_id}.json"
                if os.path.exists(output_file_path):
                    try:
                        with open(output_file_path, 'r', encoding='utf-8') as file:
                            texts_list = json.load(file)
                            texts_list = texts_list['texts_list']

                    except:
                        with open(output_file_path, 'r', encoding='utf-8') as file:
                            texts_list = json.load(file)
                            texts_list = texts_list[0]["responses"][0]["fullTextAnnotation"]["text"].split("\n")
                    print("이미 인식한 이미지입니다.")
                else:
                    try:
                        print("이미지 인식 테스트 진행")
                        texts_list = self.detect_license_in_image(uri, client_data_id)
                        
                    except:
                        print("PDF 인식 테스트 진행")
                        # pdf 로컬에 다운로드
                        response = requests.get(uri)
                        file = open(f"airtable_data/{client_data_id}.pdf", "wb")
                        file.write(response.content)
                        file.close()
                        # pdf 파일을 gcs에 업로드
                        vision_client.upload_file_to_gcs( "drive_licence_pdf", f"airtable_data/{client_data_id}.pdf", f"{client_data_id}.pdf")
                        # pdf 파일을 gcs에서 읽어와서 이미지 디텍션
                        texts_list = self.detect_license_in_pdf(f"gs://drive_licence_pdf/{client_data_id}.pdf", f"gs://drive_licence_pdf/output-folder/{client_data_id}/", client_data_id)[0]["responses"][0]["fullTextAnnotation"]["text"].split("\n")
                    print("이미지 인식을 실행합니다..")

                found_keywords = self.check_keywords_in_texts(texts_list)

                if found_keywords:
                    # 고객 이름과 면허증 비교
                    if str(record["fields"]["First Name"]) in found_keywords and str(record["fields"]["Last Name"]) in found_keywords:
                        print("Customer name matches with license")
                        # 라이센스 Class 비교
                        # 고객 이름과 면허증이 일치할 경우 아래 코드 실행
                        # for keyword in found_keywords:
                        #     self.perform_task_for_keyword(keyword, client_data_id, origin_notes)
                    elif str(record["fields"]["First Name"]) in found_keywords and str(record["fields"]["Last Name"]) not in found_keywords:
                        print("Only First name matches with license")
                        self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": f"{origin_notes}- Only First name matches with license"})
                    elif str(record["fields"]["First Name"]) not in found_keywords and str(record["fields"]["Last Name"]) in found_keywords:
                        print("Only Last name matches with license")
                        self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": f"{origin_notes}- Only Last name matches with license"})
                    elif str(record["fields"]["First Name"]) not in found_keywords and str(record["fields"]["Last Name"]) not in found_keywords:
                        print("Customer name does not match with license")
                        self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": f"{origin_notes}- Customer name does not match with license"})
                    # 라이센스 Class 비교
                    # 테스트가 끝난 뒤 실제 사용시에는 이 부분 삭제 한 뒤 위의 주석 처리된 코드를 사용
                    # 고객 이름과 면허증이 일치할 경우 아래 코드 실행
                    for keyword in found_keywords:

                        self.perform_task_for_keyword(keyword, client_data_id, origin_notes)
                    
                else:
                    self.airtable_client.update_record(client_data_id, {"Status": "Follow Up", "Notes": f"{origin_notes}- Can't find license CLASS(AI)"})

            elif "Driver's License" not in record["fields"] and record["fields"]["Status"] == "New Lead" and record["fields"]["Phone"] == int(cus_phone_numer):
                self.airtable_client.update_record(record["id"], {"Status": "Follow Up", "Notes": f"{origin_notes}- No image URL(AI)"})
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
LICENSE_KEYWORDS = ["G", "G1", "G2", "A", "AZ", "B", "C", "D", "E", "F"]

# Initialize Airtable and Google Vision clients
airtable_client = AirtableAPI(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
vision_client = GoogleVisionAPI(GOOGLE_APPLICATION_CREDENTIALS)

# Initialize LicenseDetection
license_detection = LicenseDetection(airtable_client, vision_client, LICENSE_KEYWORDS)

# Process records and perform tasks
license_detection.process_records()
