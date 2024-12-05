import os
import time
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select

#######################################################################  Login  ##############################################################################
#############################################################################################################################################################
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

#############################################################  Crate New Application 선택 ######################################################################
################################################################################################################################################################
# "main" 프레임으로 전환
iframe = driver.find_element(By.ID, "iFrm")
driver.switch_to.frame(iframe)
driver.switch_to.frame("main")

### 드롭다운 요소 찾기
# ddAsset에서 'Automotive' 선택 (value="AU")
asset_dropdown = Select(driver.find_element(By.ID, "ddAsset"))
asset_dropdown.select_by_value("AU")

# ddLenders에서 'Scotiabank' 선택 (value="BNS")
lenders_dropdown = Select(driver.find_element(By.ID, "ddLenders"))
lenders_dropdown.select_by_value("BNS")

# ddProduct에서 'Lease' 선택 (value="1")
time.sleep(1)

product_dropdown = Select(driver.find_element(By.ID, "ddProduct"))
product_dropdown.select_by_value("2")

time.sleep(1)

# 'Continue' 버튼 찾기
continue_button = driver.find_element(By.ID, "btnSave")
print(continue_button)
continue_button.click() # 버튼 클릭 (폼 제출)
print("Form submitted successfully!") # 브라우저가 새 페이지로 이동한 후 확인


########################################################### Deal Management page ###############################################################################
##################################################################################################################################################################

time.sleep(1)
# 드롭다운 요소 찾기
salutation_dropdown = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlSalutation")

# Selenium의 Select 클래스 사용
select = Select(salutation_dropdown)

# "Mr." 옵션 선택
select.select_by_visible_text("Mr.")
# 선택한 옵션 확인
selected_option = select.first_selected_option
print(f"Selected option: {selected_option.text}")  # 출력: "Mr."

time.sleep(1)
# First Name 입력 필드 찾기
first_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtFirstName")

# 텍스트 입력
first_name_input.send_keys("John")

# 입력된 값 확인
entered_value = first_name_input.get_attribute("value")
print(f"Entered value: {entered_value}")  # 출력: "John"

time.sleep(1)
# Middle Name 입력 필드 찾기
middle_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtMiddleName")

# Middle Name 데이터 입력
middle_name_input.send_keys("Edward")

# 입력된 값 확인
entered_value = middle_name_input.get_attribute("value")
print(f"Entered Middle Name: {entered_value}")  # 출력: "Edward"

time.sleep(1)
# Last Name 입력 필드 찾기
last_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtLastName")

# 데이터 입력
last_name_input.send_keys("Smith")

# 입력된 값 확인
entered_value = last_name_input.get_attribute("value")
print(f"Entered Last Name: {entered_value}")  # 출력: "Smith"

time.sleep(1)
# 드롭다운 메뉴 요소 찾기
suffix_dropdown = Select(driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlSuffix"))

# "SR" 값 선택
suffix_dropdown.select_by_value("SR")  # value 속성이 "SR"인 옵션 선택

# 선택된 옵션 확인
selected_option = suffix_dropdown.first_selected_option
print(f"Selected Suffix: {selected_option.text}")  # 출력: "SR"

####################################################################################################
# SIN 입력 필드 요소 찾기
sin_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtSIN")
sin_input.click()
sin_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")

# SIN 데이터 입력
sin_data = "555555555"  # 예시 SIN 번호
sin_input.send_keys(sin_data)  # 데이터 입력
time.sleep(1)

# 입력 확인
print(f"SIN Entered: {sin_input.get_attribute('value')}")
# class="MaskedEditFocus" 요소 찾기
phone_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 전화번호 입력
phone_number = "4374536013"  # 예시 전화번호
phone_input.send_keys(phone_number)  # 새로운 데이터 입력
time.sleep(1)
# 입력 확인
print(f"Phone Number Entered: {phone_input.get_attribute('value')}")


# class="MaskedEditFocus" 요소 찾기
mobile_phone_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 전화번호 입력
mobile_phone_number = "4374536003"  # 예시 전화번호
# phone_input.clear()  # 기존 값 삭제
mobile_phone_input.send_keys(mobile_phone_number)  # 새로운 데이터 입력
time.sleep(1)
# 입력 확인
print(f"Mobile Phone Number Entered: {mobile_phone_input.get_attribute('value')}")

# class="MaskedEditFocus" 요소 찾기
month_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_MM")

# 월 입력
month_value  = "12"
month_input.send_keys(month_value)  
time.sleep(1)
# 입력 확인
print(f"Month Entered: {month_input.get_attribute('value')}")



day_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_DD")
# 일 입력
day_value  = "6"  # 예시 전화번호
day_input.send_keys(day_value)  # 새로운 데이터 입력
time.sleep(1)
# 입력 확인
print(f"Day Entered: {day_input.get_attribute('value')}")


# class="MaskedEditFocus" 요소 찾기
year_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_YYYY")

# year 입력
year_value  = "2024"
year_input.send_keys(year_value)  
time.sleep(1)
# 입력 확인
print(f"Year Entered: {year_input.get_attribute('value')}")
####################################################################################################

# Gender 드롭다운 찾기
gender_select = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlGender")

# 드롭다운을 Select 객체로 변환
select = Select(gender_select)

# "Female" 옵션 선택
select.select_by_value("FEMALE")

# 선택된 값 확인
selected_option = select.first_selected_option
time.sleep(1)
print(f"Selected Gender: {selected_option.text}")



# Marital Status 드롭다운 찾기
marital_status_select = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlMaritalStatus")

# 드롭다운을 Select 객체로 변환
select = Select(marital_status_select)

# "Married" 옵션 선택
select.select_by_value("MR")

# 선택된 값 확인
selected_option = select.first_selected_option
time.sleep(1)
print(f"Selected Marital Status: {selected_option.text}")




# 이메일 입력 필드 찾기
email_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtEmail")

# 이메일 데이터 입력
email_input.send_keys("example@example.com")

# 입력된 이메일 값 확인
entered_email = email_input.get_attribute("value")
time.sleep(1)

print(f"Entered Email: {entered_email}")

# 'Language' 드롭다운 찾기
language_dropdown = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlLanguage")

# Select 객체로 드롭다운을 제어
select = Select(language_dropdown)

# 'English' 선택 (value="en-CA")
select.select_by_value("en-CA") # fr-CA


# Postal Code 입력 필드 찾기
postal_code_input = driver.find_element(By.ID, "ctl21_ctl21_ctl00_txtPostalCode")
postal_code_input.click()
postal_code_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")

# 우편번호 입력 (예시 값)
postal_code = "m2n 2y8"  # 원하는 우편번호로 대체하세요

# 우편번호 데이터 입력
postal_code_input.send_keys(postal_code)

# 입력된 값 확인
entered_value = postal_code_input.get_attribute("value")
# time.sleep(1)
print(f"Entered Postal Code: {entered_value}")

# 'Address Lookup' 버튼 찾기
address_lookup_button = driver.find_element(By.ID, "ctl21_ctl21_ctl00_btnPostalCodeLookup")

# 버튼 클릭
address_lookup_button.click()

# 버튼 클릭 후 결과를 확인할 수 있도록 시간 대기
time.sleep(1)  # 필요한 경우 기다려주세요.
print("Address Lookup button clicked successfully!")

#드라이버 종료
# time.sleep(1)
# time.sleep(1)
# time.sleep(1)
# driver.quit()