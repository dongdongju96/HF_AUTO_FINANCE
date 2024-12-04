import os
from dotenv import load_dotenv
from pprint import pprint
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time 

# .env 파일에서 환경 변수 로드
load_dotenv()
DEALERTRACK_ID = os.getenv("DEALERTRACK_ID")
DEALERTRACK_PASS = os.getenv("DEALERTRACK_PASS")

# URL 설정
login_url = "https://auth.dealertrack.ca/idp/startSSO.ping?PartnerSpId=prod_dtc_sp_pingfed"  # form의 action 속성에서 가져옴
dealertrack_default_url = "https://www.dealertrack.ca/default1.aspx"

# 로그인 정보
username = DEALERTRACK_ID
password = DEALERTRACK_PASS

# POST 요청에 필요한 데이터
login_data = {
    "pf.username": username,
    "pf.pass": password,
    "pf.ok": "",
    "pf.cancel": "",
    "pf.adapterId": "ARTHTMLLOGINPAGE",
}

# 세션 생성 (쿠키 관리용)
session = requests.session()

# 로그인 요청
response = session.post(login_url, data=login_data)
response.raise_for_status()

# 로그인 성공 후 페이지 요청
res = session.get(dealertrack_default_url)
res.raise_for_status()

# BeautifulSoup으로 HTML 내용 확인
soup = BeautifulSoup(res.text, 'html.parser')

options = Options()
options.add_experimental_option("detach", True)
# 크롬 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 웹페이지 로드
driver.get(dealertrack_default_url)

# Requests 세션의 쿠키를 Selenium으로 복사
cookies = session.cookies.get_dict()
for name, value in cookies.items():
    driver.add_cookie({'name': name, 'value': value})

# 쿠키를 적용한 후 새로고침
driver.refresh()
driver.get("https://www.dealertrack.ca/DTCanada/Core/application/application_new_type.aspx")
# iframe = driver.find_element("xpath", "/html/frameset/frame[1]")

# "main" 프레임으로 전환
iframe = driver.find_element(By.ID, "iFrm")
driver.switch_to.frame(iframe)
driver.switch_to.frame("main")

### 드롭다운 요소 찾기
# ddAsset에서 'Automotive' 선택 (value="AU")
asset_dropdown = Select(driver.find_element(By.ID, "ddAsset"))
asset_dropdown.select_by_value("AU")
time.sleep(1)
# print("Selected Asset 1 :", asset_dropdown.first_selected_option.text)

# ddLenders에서 'Scotiabank' 선택 (value="BNS")
lenders_dropdown = Select(driver.find_element(By.ID, "ddLenders"))
lenders_dropdown.select_by_value("BNS")
time.sleep(1)
# print("Selected Lender 1 :", lenders_dropdown.first_selected_option.text)

# ddProduct에서 'Lease' 선택 (value="1")
product_dropdown = Select(driver.find_element(By.ID, "ddProduct"))
product_dropdown.select_by_value("2")
time.sleep(1)
# print("Selected Product 1 :", product_dropdown.first_selected_option.text)

# ddApplicantType에서 'Consumer' 선택 (value="1")
# ApplicantType_dropdown = Select(driver.find_element(By.ID, "ddApplicantType"))
# ApplicantType_dropdown.select_by_value("1")

# 선택한 옵션 출력 (선택된 옵션 확인)
print("Selected Asset 2 :", asset_dropdown.first_selected_option.text)
print("Selected Lender 2 :", lenders_dropdown.first_selected_option.text)
print("Selected Product 2 :", product_dropdown.first_selected_option.text)

# 'Continue' 버튼 찾기
continue_button = driver.find_element(By.ID, "btnSave")
print(continue_button)
continue_button.click() # 버튼 클릭 (폼 제출)
print("Form submitted successfully!") # 브라우저가 새 페이지로 이동한 후 확인

# creatapp.click()


# # iframe 전환 (frameset 내의 첫 번째 프레임으로 전환)
# iframe = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, "iFrm"))
# )
# driver.switch_to.frame(iframe)  # 해당 iframe으로 전환
# print(f"---{iframe}---")
# # Create App 버튼 클릭 (ID가 "PrepareApp"인 요소를 클릭)
# create_app_element = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.ID, "PrepareApp"))
# )
# print(f"---{create_app_element}---")
# # 클릭하여 Create App 활성화
# create_app_element.click()

# # 드롭다운 요소 (ddLenders) 기다리기
# dropdown_element = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, "ddLenders"))
# )

# # 드롭다운에서 "Scotiabank" 선택
# select = Select(dropdown_element)
# select.select_by_visible_text("Scotiabank")

# # 선택한 옵션 확인
# selected_option = select.first_selected_option
# print(f"Selected option: {selected_option.text}")

# # 페이지의 현재 URL 출력
# print(f"New URL after click: {driver.current_url}")


# # 브라우저 종료
# driver.quit()
