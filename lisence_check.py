import os
import json
from pprint import pprint
from dotenv import load_dotenv
from google.cloud import vision


# load token, ID
load_dotenv()
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
AIRTABLE_CLIENT_DATA_ID = os.getenv("AIRTABLE_CLIENT_DATA_ID")
URI = os.getenv("URI")

# lisence 키워드
lisence_keywords = ["G", "G1", "G2"]

# Example usage
file_path = os.path.join(".", "image_detection_output", f"{AIRTABLE_CLIENT_DATA_ID}.json")

################################################################################################################################################
# airtableAPI load and id, uricheck

################################################################################################################################################


def detect_text_uri(uri, id):
    """Detects text in the file located in Google Cloud Storage or on the Web."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations

    # print("Texts:")
    texts_list = []
    structured_texts = []

    # Process detected texts
    for text in texts:
        texts_list.append(text.description)
        structured_texts.append({
            "description": text.description,
            "bounding_poly": [
                {"x": vertex.x, "y": vertex.y} for vertex in text.bounding_poly.vertices
            ],
        })

        # print(f'\n"{text.description}"')
        vertices = [
            f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
        ]
        # print("bounds: {}".format(",".join(vertices)))

    # Save results to JSON file
    output_data = {
        "response": json.loads(response.__class__.to_json(response)),
        "texts": structured_texts,
        "texts_list": texts_list
    }

    output_file_path = f"./image_detection_output/{id}.json"

    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    # print(f"Results saved to {output_file_path}")

    # Error handling
    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )


# 결과 리스트 값 리턴 필요
def check_texts_in_json(file_path, keywords):
    """JSON 파일에서 texts_list를 탐색하고 특정 키워드 확인"""
    try:
        # JSON 파일 읽기
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # texts_list 필드 확인
        texts_list = data.get("texts_list", [])
        if not isinstance(texts_list, list):
            print(f"'texts_list' is not a list: {texts_list}")
            return
        
        # 키워드 검색
        found_keywords = [keyword for keyword in keywords if keyword in texts_list]
        
        # 결과 출력
        if found_keywords:
            print(f"Found keywords in 'texts_list': {found_keywords}")
            return found_keywords
        else:
            print("No matching keywords found in 'texts_list'.")
            return None

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


# 실행
# detect_text_uri(URI, AIRTABLE_CLIENT_DATA_ID)
check_texts_in_json(file_path, lisence_keywords)
