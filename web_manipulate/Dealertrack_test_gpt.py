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
from selenium.webdriver.support.ui import WebDriverWait

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
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################

############################################################### Applicant(s) ###################################################################################
################################################################################################################################################################
################################################################################################################################################################


########################################################### Personal Information ###############################################################################
################################################################################################################################################################

try:
    salutation_dropdown = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ctl21_ctl20_ctl00_ddlSalutation"))
    )
    print("salutation_dropdown field is loaded.")
except:
    print("Timeout: salutation_dropdown field was not found.")

# # 드롭다운 요소 찾기
# salutation_dropdown = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlSalutation")

# Selenium의 Select 클래스 사용
select = Select(salutation_dropdown)

# "Mr." 옵션 선택
select.select_by_visible_text("Mr.")
# 선택한 옵션 확인
selected_option = select.first_selected_option
print(f"Selected option: {selected_option.text}")  # 출력: "Mr."

# time.sleep(1)
# First Name 입력 필드 찾기
first_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtFirstName")

# 텍스트 입력
first_name_input.send_keys("John")

# 입력된 값 확인
entered_value = first_name_input.get_attribute("value")
print(f"Entered value: {entered_value}")  # 출력: "John"

# time.sleep(1)
# Middle Name 입력 필드 찾기
middle_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtMiddleName")

# Middle Name 데이터 입력
middle_name_input.send_keys("Edward")

# 입력된 값 확인
entered_value = middle_name_input.get_attribute("value")
print(f"Entered Middle Name: {entered_value}")  # 출력: "Edward"

# time.sleep(1)
# Last Name 입력 필드 찾기
last_name_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtLastName")

# 데이터 입력
last_name_input.send_keys("Smith")

# 입력된 값 확인
entered_value = last_name_input.get_attribute("value")
print(f"Entered Last Name: {entered_value}")  # 출력: "Smith"

# time.sleep(1)
# 드롭다운 메뉴 요소 찾기
suffix_dropdown = Select(driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlSuffix"))

# "SR" 값 선택
suffix_dropdown.select_by_value("SR")  # value 속성이 "SR"인 옵션 선택

# 선택된 옵션 확인
selected_option = suffix_dropdown.first_selected_option
print(f"Selected Suffix: {selected_option.text}")  # 출력: "SR"

################################################################# Number 입력 ####################################################################################
# SIN 입력 필드 요소 찾기
sin_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtSIN")
sin_input.click()
sin_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")

# SIN 데이터 입력
sin_data = "555555555"  # 예시 SIN 번호
sin_input.send_keys(sin_data)  # 데이터 입력
# time.sleep(1)

# 입력 확인
print(f"SIN Entered: {sin_input.get_attribute('value')}")

# class="MaskedEditFocus" 요소 찾기
phone_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 전화번호 입력
phone_number = "4374536013"  # 예시 전화번호
phone_input.send_keys(phone_number)  # 새로운 데이터 입력
# time.sleep(1)
# 입력 확인
print(f"Phone Number Entered: {phone_input.get_attribute('value')}")


# class="MaskedEditFocus" 요소 찾기
mobile_phone_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 전화번호 입력
mobile_phone_number = "4374536003"  # 예시 전화번호
# phone_input.clear()  # 기존 값 삭제
mobile_phone_input.send_keys(mobile_phone_number)  # 새로운 데이터 입력
# time.sleep(1)
# 입력 확인
print(f"Mobile Phone Number Entered: {mobile_phone_input.get_attribute('value')}")

# class="MaskedEditFocus" 요소 찾기
month_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_MM")

# 월 입력
month_value  = "12"
month_input.send_keys(month_value)  
# time.sleep(1)
# 입력 확인
print(f"Month Entered: {month_input.get_attribute('value')}")



day_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_DD")
# 일 입력
day_value  = "6"  # 예시 전화번호
day_input.send_keys(day_value)  # 새로운 데이터 입력
# time.sleep(1)
# 입력 확인
print(f"Day Entered: {day_input.get_attribute('value')}")


# class="MaskedEditFocus" 요소 찾기
year_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_YYYY")

# year 입력
year_value  = "2024"
year_input.send_keys(year_value)  
# time.sleep(1)
# 입력 확인
print(f"Year Entered: {year_input.get_attribute('value')}")
################################################################################################################################################################## 


# Gender 드롭다운 찾기
gender_select = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlGender")

# 드롭다운을 Select 객체로 변환
select = Select(gender_select)

# "Female" 옵션 선택
select.select_by_value("FEMALE")

# 선택된 값 확인
selected_option = select.first_selected_option
# time.sleep(1)
print(f"Selected Gender: {selected_option.text}")



# Marital Status 드롭다운 찾기
marital_status_select = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlMaritalStatus")

# 드롭다운을 Select 객체로 변환
select = Select(marital_status_select)

# "Married" 옵션 선택
select.select_by_value("MR")

# 선택된 값 확인
selected_option = select.first_selected_option
# time.sleep(1)
print(f"Selected Marital Status: {selected_option.text}")




# 이메일 입력 필드 찾기
email_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtEmail")

# 이메일 데이터 입력
email_input.send_keys("example@example.com")

# 입력된 이메일 값 확인
entered_email = email_input.get_attribute("value")
# time.sleep(1)

print(f"Entered Email: {entered_email}")

# 'Language' 드롭다운 찾기
language_dropdown = driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlLanguage")

# Select 객체로 드롭다운을 제어
select = Select(language_dropdown)

# 'English' 선택 (value="en-CA")
select.select_by_value("en-CA") # fr-CA

######################################################## Current Address ##################################################################
###########################################################################################################################################
# Suite No : example 3108
# SUITE 3108 , 호텔이나 럭셔리 빌딩
# UNIT 3108 , GENERAL
# 3108-STnumber(107)
# APT 3108 , 큰 방

# Postal Code 입력 필드 찾기
try:
    postal_code_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ctl21_ctl21_ctl00_txtPostalCode"))
    )
    print("postal_code_input field is loaded.")
except:
    print("Timeout: postal_code_input field was not found.")
# postal_code_input = driver.find_element(By.ID, "ctl21_ctl21_ctl00_txtPostalCode")
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
time.sleep(5)  # 필요한 경우 기다려주세요.
print("Address Lookup button clicked successfully!")

# 'Duration in Years' 텍스트 필드 요소 찾기
try:
    duration_years_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ctl21_ctl21_ctl00_CDurationCurrentAddress_Y"))
    )
    print("Duration field is loaded.")
except:
    print("Timeout: Duration input field was not found.")

# 값 입력 (예: '5')
duration_years_value = "2"
duration_years_input.send_keys(duration_years_value)

# 입력된 값 확인
entered_value = duration_years_input.get_attribute("value")
print(f"Entered Duration in Years: {entered_value}")  # 출력: Entered Duration in Years: 5

# 'Duration in Months' 텍스트 필드 요소 찾기
duration_months_input = driver.find_element(By.ID, "ctl21_ctl21_ctl00_CDurationCurrentAddress_M")

# 값 입력 (예: '6')
duration_months_value = "6"
duration_months_input.send_keys(duration_months_value)

# 입력된 값 확인
entered_value = duration_months_input.get_attribute("value")
print(f"Entered Duration in Months: {entered_value}")  # 출력: Entered Duration in Months: 6




######################################################## Previous Address #################################################################
###########################################################################################################################################
# Duration < 2 면 작성

###################################################### Home/Mortgage Details ##############################################################
###########################################################################################################################################

# 'Home' 드롭다운 요소 찾기
home_dropdown = driver.find_element(By.ID, "ctl21_ctl23_ctl00_ddlHome")

# Selenium의 Select 객체 생성
select = Select(home_dropdown)

# 특정 옵션 선택 (예: 'Own with Mortgage')
# OW : Own with Mortage
# OF : Own Free & Clear
# OM : Own Mobile Home
# RE : Rent
# PA : With parents
# RH : Reserve Housing
# OT : Other
select.select_by_value("OW")  # value 속성이 'OW'인 옵션 선택

# 선택한 옵션 확인
selected_option = select.first_selected_option
print(f"Selected Home Option: {selected_option.text}")  # 출력: Own with Mortgage

# # JSON 데이터에서 옵션 값 로드 (예시)
# home_option_value = json_data["home_status"]  # 예: 'OW'

# # 옵션 선택
# select.select_by_value(home_option_value)


# 'Market Value' 입력 필드 찾기
market_value_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtmarketValue")

# 값 입력 (예: 500000)
market_value = "500000"
market_value_input.clear()  # 기존 값 삭제
market_value_input.send_keys(market_value)

# 입력된 값 확인
entered_value = market_value_input.get_attribute("value")
print(f"Entered Market Value: {entered_value}")  # 출력: Entered Market Value: 500000


# # JSON 데이터에서 값 로드 (예시)
# market_value = json_data["market_value"]  # 예: '500000'

# # 값 입력
# market_value_input.clear()
# market_value_input.send_keys(market_value)

# 'Mortgage Amount' 입력 필드 찾기
mortgage_amount_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMortgageAmount")

# 값 입력 (예: 200000)
mortgage_amount = "200000"
mortgage_amount_input.clear()  # 기존 값 삭제
mortgage_amount_input.send_keys(mortgage_amount)

# 입력된 값 확인
entered_value = mortgage_amount_input.get_attribute("value")
print(f"Entered Mortgage Amount: {entered_value}")  # 출력: Entered Mortgage Amount: 200000

# 'Mortgage Holder' 입력 필드 찾기
mortgage_holder_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMortgageHolder")

# 값 입력 (예: 'ABC Bank')
mortgage_holder = "ABC Bank"
mortgage_holder_input.clear()  # 기존 값 삭제
mortgage_holder_input.send_keys(mortgage_holder)

# 입력된 값 확인
entered_value = mortgage_holder_input.get_attribute("value")
print(f"Entered Mortgage Holder: {entered_value}")  # 출력: Entered Mortgage Holder: ABC Bank


# 'Monthly Payment' 입력 필드 찾기
monthly_payment_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMonthlyPayment")

# 값 입력 (예: '1200')
monthly_payment = "1200"
monthly_payment_input.clear()  # 기존 값 삭제
monthly_payment_input.send_keys(monthly_payment)

# 입력된 값 확인
entered_value = monthly_payment_input.get_attribute("value")
print(f"Entered Monthly Payment: {entered_value}")  # 출력: Entered Monthly Payment: 1200




######################################################## Current Employment ###############################################################
###########################################################################################################################################

# 'Type of Current Employment' 드롭다운 요소 찾기
current_employment_type_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlTypeCurEmp")

# Selenium의 Select 객체 생성
select_employment_type = Select(current_employment_type_dropdown)

# 원하는 옵션 선택 (예: 'Self-Employed')
# At home
# Executive
# Labourer
# Management
# Office Staff
# Other
# Production
# Progessional
# Retired
# Sales
# Self- Employed
# Service
# Student
# Trades
# Unemployed
employment_type = "Self-Employed"
select_employment_type.select_by_visible_text(employment_type)

# 선택된 옵션 확인
selected_option = select_employment_type.first_selected_option
print(f"Selected Employment Type: {selected_option.text}")  # 출력: Selected Employment Type: Self-Employed

# 'Current Employer' 입력 필드 찾기
current_employer_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtEmployerCurEmp")

# 값 입력
current_employer_name = "Tech Solutions Inc."
current_employer_input.send_keys(current_employer_name)

# 입력된 값 확인
entered_value = current_employer_input.get_attribute("value")
print(f"Entered Current Employer: {entered_value}")  # 출력: Entered Current Employer: Tech Solutions Inc.

# 'Employment Status' 드롭다운 요소 찾기
employment_status_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlStatusCurEmp")

# Select 객체 생성
select = Select(employment_status_dropdown)

# 값 선택 (예: 'Full time')
# FT : Full time
# FTP : Full Time (Probation)
# PTC : Part Time (Casual)
# PTR : Part Time (Regular)
# RET : Retired
# SEAS : Seasonal Summer
# SEAW : Seasonal Winter
# SE : Self Employed
employment_status_value = "FT"
select.select_by_value(employment_status_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Employment Status: {selected_option.text}")  # 출력: Selected Employment Status: Full time


# 'Occupation' 입력 필드 찾기
occupation_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtOccupationCurEmp")

# 값 입력
occupation_value = "Software Engineer"
occupation_input.send_keys(occupation_value)

# 입력된 값 확인
entered_value = occupation_input.get_attribute("value")
print(f"Entered Occupation: {entered_value}")  # 출력: Entered Occupation: Software Engineer

# 'Duration Current Employer Address' 입력 필드 찾기
duration_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_CDurationCurrentEmployerAddress_Y")

# 값 설정 (예: "12" - 2자리 숫자)
duration_value = "2"
duration_input.send_keys(duration_value)

# 입력된 값 확인
entered_value = duration_input.get_attribute("value")
print(f"Entered Duration: {entered_value}")  # 출력: Entered Duration: 12

# 'Duration Current Employer Address - Month' 입력 필드 찾기
month_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_CDurationCurrentEmployerAddress_M")

# 값 설정 (예: "06" - 2자리 숫자)
month_value = "6"
month_input.send_keys(month_value)

# 입력된 값 확인
entered_value = month_input.get_attribute("value")
print(f"Entered Month Duration: {entered_value}")  # 출력: Entered Month Duration: 06

# 'Address Type Current Employer' 드롭다운 찾기
address_type_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlAddressTypeCurEmp")

# Select 객체로 드롭다운을 제어
select = Select(address_type_dropdown)

# "Street" 옵션 선택 (value="ST")
# ST : Street
# RR : Rural Route
# PB : Postal Box
select.select_by_value("ST")

# 선택된 옵션 확인
selected_option = select.first_selected_option
print(f"Selected Address Type: {selected_option.text}")  # 출력: Selected Address Type: Street

# 'Suite Number Current Employer' 입력 필드 찾기
suite_number_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtSuiteNumberCurEmp")

# 텍스트 입력
suite_number_input.send_keys("123A")

# 입력된 값 확인
entered_value = suite_number_input.get_attribute("value")
print(f"Entered Suite Number: {entered_value}")  # 출력: Entered Suite Number: 123A

# 'Street Number Current Employer' 입력 필드 찾기
street_number_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtStreetNumberCurEmp")

# 텍스트 입력
street_number_input.send_keys("456")

# 입력된 값 확인
entered_value = street_number_input.get_attribute("value")
print(f"Entered Street Number: {entered_value}")  # 출력: Entered Street Number: 456


# 'Street Name Current Employer' 입력 필드 찾기
street_name_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtStreetNameCurEmp")

# 텍스트 입력
street_name_input.send_keys("Maple Street")

# 입력된 값 확인
entered_value = street_name_input.get_attribute("value")
print(f"Entered Street Name: {entered_value}")  # 출력: Entered Street Name: Maple Street



# 'Street Type Current Employer' 드롭다운 메뉴 찾기
street_type_select = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlStreetTypeCurEmp")

# 드롭다운 메뉴로 옵션 선택하기
# AB : ABBEY
# AS : ACRES
# AE : ALLEE
# AL : ALLEY
# AU : AUTOROUTE
# AV : AVENUE
# BA : BAY
# BE : BEACH
# BN : BEND
# BV : BLVD
# BO : BOUL
# BP : BYPASS
# CA : CAMPUS
# CP : CAPE
# CR : CARRE
# CN : CENTRE
# CC : CERCLE
# CE : CHASE
# CH : CHEMIN
# CI : CIRCLE
# CF : CIRCUIT
# CL : CLOSE
# CM : COMMON
# CQ : CONCESSION
# CB : COMRNERS
# CO : COTE
# CU : COUR
# CY : COURS
# CT : COURT
# CV : COVE
# CS : CRESENT
# CW : CROISSANT
# CD : CUL-DE-SAC
# DA : DALE
# DE : DELL
# DI : DIVERSION
# EN : END
# EP : ESPLANADE
# ES : ESTATES
# EX : EXPRESSWAY
# ET : EXTENSION
# FI : FIELD
# FY : FREEWAY
# FR : FRONT
# GD : GARDENS
# GT : GATE
# GL : GLADE
# GE : GLEN
# GN : 

# value="ST": 텍스트 "STREET"
# value="RR": 텍스트 "Rural Route"
# value="PB": 텍스트 "Postal Box"
# value="AV": 텍스트 "AVENUE"
# value="BA": 텍스트 "BAY"
# value="BE": 텍스트 "BEACH"
# value="BN": 텍스트 "BEND"
# value="BV": 텍스트 "BLVD"
# value="BO": 텍스트 "BOUL"
# value="BP": 텍스트 "BYPASS"
# value="CA": 텍스트 "CAMPUS"
# value="CP": 텍스트 "CAPE"
# value="CR": 텍스트 "CARRE"
# value="CN": 텍스트 "CENTRE"
# value="CC": 텍스트 "CERCLE"
# value="CE": 텍스트 "CHASE"
# value="CH": 텍스트 "CHEMIN"
# value="CI": 텍스트 "CIRCLE"
# value="CF": 텍스트 "CIRCUIT"
# value="CL": 텍스트 "CLOSE"
# value="CM": 텍스트 "COMMON"
# value="CQ": 텍스트 "CONCESSION"
# value="CB": 텍스트 "CORNERS"
# value="CO": 텍스트 "COTE"
# value="CU": 텍스트 "COUR"
# value="CY": 텍스트 "COURS"
# value="CT": 텍스트 "COURT"
# value="CV": 텍스트 "COVE"
# value="CS": 텍스트 "CRESCENT"
# value="CW": 텍스트 "CROISSANT"
# value="CX": 텍스트 "CROSSING"
# value="CD": 텍스트 "CUL-DE-SAC"
# value="DA": 텍스트 "DALE"
# value="DE": 텍스트 "DELL"
# value="DI": 텍스트 "DIVERSION"
# value="DO": 텍스트 "DOWNS"
# value="DR": 텍스트 "DRIVE"
# value="EN": 텍스트 "END"
# value="EP": 텍스트 "ESPLANADE"
# value="ES": 텍스트 "ESTATES"
# value="EX": 텍스트 "EXPRESSWAY"
# value="ET": 텍스트 "EXTENSION"
# value="FI": 텍스트 "FIELD"
# value="FY": 텍스트 "FREEWAY"
# value="FR": 텍스트 "FRONT"
# value="GD": 텍스트 "GARDENS"
# value="GT": 텍스트 "GATE"
# value="GL": 텍스트 "GLADE"
# value="GE": 텍스트 "GLEN"
# value="GN": 텍스트 "GREEN"
# value="GA": 텍스트 "GROUNDS"
# value="GR": 텍스트 "GROVE"
# value="HA": 텍스트 "HARBOUR"
# value="HE": 텍스트 "HEATH"
# value="HT": 텍스트 "HEIGHTS"
# value="HG": 텍스트 "HIGHLANDS"
# value="HW": 텍스트 "HIGHWAY"
# value="HL": 텍스트 "HILL"
# value="HO": 텍스트 "HOLLOW"
# value="IL": 텍스트 "ILE"
# value="IM": 텍스트 "IMPASSE"
# value="IN": 텍스트 "INLET"
# value="IS": 텍스트 "ISLAND"
# value="KE": 텍스트 "KEY"
# value="KN": 텍스트 "KNOLL"
# value="LA": 텍스트 "LANDNG"
# value="LN": 텍스트 "LANE"
# value="LM": 텍스트 "LIMITS"
# value="LE": 텍스트 "LINE"
# value="LI": 텍스트 "LINK"
# value="LK": 텍스트 "LOOKOUT"
# value="LP": 텍스트 "LOOP"
# value="MA": 텍스트 "MALL"
# value="MR": 텍스트 "MANOR"
# value="MZ": 텍스트 "MAZE"
# value="MW": 텍스트 "MEADOW"
# value="MS": 텍스트 "MEWS"
# value="MN": 텍스트 "MONTEE"
# value="MO": 텍스트 "MOUNT"
# value="MT": 텍스트 "MOUNTAIN"
# value="PR": 텍스트 "PARADE"
# value="PC": 텍스트 "PARC"
# value="PK": 텍스트 "PARK"
# value="PY": 텍스트 "PARKWAY"
# value="PS": 텍스트 "PASSAGE"
# value="PA": 텍스트 "PATH"
# value="PW": 텍스트 "PATHWAY"
# value="PL": 텍스트 "PLACE"
# value="PP": 텍스트 "PLATEAU"
# value="PZ": 텍스트 "PLAZA"
# value="PQ": 텍스트 "POINT"
# value="PT": 텍스트 "POINTE"
# value="PV": 텍스트 "PRIVATE"
# value="PE": 텍스트 "PROMENADE"
# value="QU": 텍스트 "QUAI"
# value="QY": 텍스트 "QUAY"
# value="RM": 텍스트 "RAMP"
# value="RA": 텍스트 "RANG"
# value="RG": 텍스트 "RANGE"
# value="RE": 텍스트 "RIDGE"
# value="RI": 텍스트 "RISE"
# value="RD": 텍스트 "ROAD"
# value="RT": 텍스트 "ROUTE"
# value="RO": 텍스트 "ROW"
# value="RU": 텍스트 "RUE"
# value="RL": 텍스트 "RUELLE"
# value="RN": 텍스트 "RUN"
# value="SN": 텍스트 "SENTIER"
# value="SQ": 텍스트 "SQUARE"
# value="SU": 텍스트 "SUBDIVISION"
# value="TC": 텍스트 "TERRACE"
# value="TS": 텍스트 "TERRASSE"
# value="TL": 텍스트 "TOWNLINE"
# value="TR": 텍스트 "TRAIL"
# value="TT": 텍스트 "TURNABOUT"
# value="VL": 텍스트 "VALE"
# value="VW": 텍스트 "VIEW"
# value="VI": 텍스트 "VILLAGE"
# value="VA": 텍스트 "VILLAS"
# value="VS": 텍스트 "VISTA"
# value="VO": 텍스트 "VOIE"
# value="WK": 텍스트 "WALK"
# value="WY": 텍스트 "WAY"
# value="WH": 텍스트 "WHARF"
# value="WO": 텍스트 "WOOD"
# value="WN": 텍스트 "WYND"
select = Select(street_type_select)
select.select_by_value("AV")  # 예: "AVENUE"를 선택하려면 "AV" 값을 사용

# 선택된 옵션 확인
selected_option = select.first_selected_option
print(f"Selected Street Type: {selected_option.text}")  # 출력: Selected Street Type: AVENUE


# 'Direction' 드롭다운 요소 찾기
direction_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlDirectionCurEmp")

# Select 객체 생성
select = Select(direction_dropdown)

# 값 선택 (예: 'North')
# value="E": 텍스트 "East"
# value="N": 텍스트 "North"
# value="NE": 텍스트 "North East"
# value="NW": 텍스트 "North West"
# value="S": 텍스트 "South"
# value="SE": 텍스트 "South East"
# value="SW": 텍스트 "South West"
# value="W": 텍스트 "West"
direction_value = "N"
select.select_by_value(direction_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Direction: {selected_option.text}")  # 출력: Selected Direction: North

# 'City' 텍스트 입력 필드 찾기
city_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00__txtCityCurEmp")

# 값 입력 (예: 'Toronto')
city_input.send_keys("Toronto")

# 입력된 값 확인
print(f"Entered City: {city_input.get_attribute('value')}")  # 출력: Entered City: Toronto

# 'Province' 드롭다운 요소 찾기
province_dropdown = driver.find_element(By.ID, "ctl21_ctl24_ctl00__ddlProvinceCurEmp")

# Select 객체 생성
select = Select(province_dropdown)

# 값 선택 (예: 'Ontario')
# value=1 : Alberta
# value=2 : British Columbia
# value=3 : Manitoba
# value=4 : New Brunswick
# value=5 : Newfoundland
# value=6 : Northwest Territories
# value=7 : Nova Scotia
# value=8 : Nunavut
# value=9 : Ontario
# value=10 : Prince Edward Island
# value=11 : Quebec
# value=12 : Saskatchewan
# value=13 : Yukon

province_value = "9"
select.select_by_value(province_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Province: {selected_option.text}")  # 출력: Selected Province: Ontario

# 'Postal Code' 입력 필드 찾기

postal_code_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtPostalCodeCurEmp")
postal_code_input.click()
postal_code_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")

# 값 입력 (예: 'M1A 2B3')
postal_code_value = "M1A2B3"
postal_code_input.send_keys(postal_code_value)

# 입력된 값 확인
print(f"Entered Postal Code: {postal_code_input.get_attribute('value')}")  # 출력: Entered Postal Code: M1A 2B3

time.sleep(1)
# 'Telephone' 입력 필드 찾기
telephone_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtTelephoneCurEmp")
# telephone_input.click()
# telephone_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 값 입력 (예: '123-456-7890')
telephone_value = "4374536013"
telephone_input.send_keys(telephone_value)

# 입력된 값 확인
print(f"Entered Telephone: {telephone_input.get_attribute('value')}")  # 출력: Entered Telephone: 123-456-7890

time.sleep(1)
# 'Extension' 입력 필드 찾기
extension_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtExtensionCurEmp")
# extension_input.click()
# extension_input = driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
# 값 입력 (예: '12345')
extension_value = "12345"
extension_input.send_keys(extension_value)

# 입력된 값 확인
print(f"Entered Extension: {extension_input.get_attribute('value')}")  # 출력: Entered Extension: 12345

######################################################## Previous Employment ##############################################################
###########################################################################################################################################
# Duration < 2 면 작성

######################################################## Income Details ###################################################################
###########################################################################################################################################

# 'Gross Income' 입력 필드 찾기
gross_income_input = driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtGrossIncome")
# 값 입력 (예: '50000')
gross_income_value = "50000"
gross_income_input.clear()
gross_income_input.send_keys(gross_income_value)

# 입력된 값 확인
print(f"Entered Gross Income: {gross_income_input.get_attribute('value')}")  # 출력: Entered Gross Income: 50000

# 'Income Basis' 드롭다운 요소 찾기
income_basis_dropdown = driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlIncomeBasis")
income_basis_dropdown.click()
# Select 객체 생성
select = Select(income_basis_dropdown)

# 값 선택 (예: 'Month')
# value=1 : Year
# value=12 : Month
# value=52 : Week
income_basis_value = "12"
select.select_by_value(income_basis_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Income Basis: {selected_option.text}")  # 출력: Selected Income Basis: Month


# 'Other Income Type' 드롭다운 요소 찾기
other_income_type_dropdown = driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlOtherIncomeType")

# Select 객체 생성
select = Select(other_income_type_dropdown)

# 값 선택 (예: 'Disability Payments')
# value="Car Allowance" : Car Allowance
# value="Child Support/Alimony" : Child Support/Alimony
# value="Disability Payments" : Disability Payments
# value="Investment Income" : Investment Income
# value="Other" : Other
# value="Pensions" : Pensions
# value="Rental Income" : Rental Income
# value="Workers Compensation" : Workers Compensation
other_income_type_value = "Disability Payments"
select.select_by_visible_text(other_income_type_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Other Income Type: {selected_option.text}")  # 출력: Selected Other Income Type: Disability Payments

# 10초간 기다리기
# 'Other Income' 입력 필드 찾기
other_income_input = driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtOtherIncome")

# 값 입력 (예: '1000')
other_income_value = "1000"
other_income_input.clear()
other_income_input.send_keys(other_income_value)

# 입력된 값 확인
entered_value = other_income_input.get_attribute("value")

print(f"Entered Other Income: {entered_value}")  # 출력: Entered Other Income: 1000


# 'Other Income Basis' 드롭다운 요소 찾기
other_income_basis_dropdown = driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlOtherIncomeBasis")

# Select 객체 생성
select = Select(other_income_basis_dropdown)

# 값 선택 (예: 'Month')
# value=1 : Year
# value=12 : Month
# value=52 : Week
other_income_basis_value = "12"
select.select_by_value(other_income_basis_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Other Income Basis: {selected_option.text}")  # 출력: Selected Other Income Basis: Month

if other_income_type_value=="Other":
    # 'Other Description' 텍스트 필드 요소 찾기
    other_description_input = driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtOtherDescription")

    # 값 입력 (예: 'Additional Income')
    other_description_value = "Additional Income"
    other_description_input.send_keys(other_description_value)

    # 입력된 값 확인
    entered_value = other_description_input.get_attribute("value")
    print(f"Entered Other Description: {entered_value}")  # 출력: Entered Other Description: Additional Income


######################################################## Financial Summary ################################################################
###########################################################################################################################################

##################################################### Assets and Liabilities ##############################################################
###########################################################################################################################################


###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################

################################################################ Worksheet ################################################################
###########################################################################################################################################
###########################################################################################################################################
# 'Worksheet' 링크 요소 찾기
worksheet_link = driver.find_element(By.ID, "ctl21_btnWORKSHEET")

# 링크 클릭
worksheet_link.click()

########################################################### Vehicle Selection #############################################################
###########################################################################################################################################

# 'VIN' 입력 필드 찾기
# 'VIN' 입력 필드 로드될 때까지 기다리기 (최대 20초)
try:
    vin_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ctl21_ctl19_ctl00_txtVIN"))
    )
    print("VIN input field is loaded.")
except:
    print("Timeout: VIN input field was not found.")

# 값 입력 (예: '1HGCM82633A123456')
vin_value = "1HGCM82633A123456"
vin_input.send_keys(vin_value)

# 입력된 값 확인
entered_value = vin_input.get_attribute("value")
print(f"Entered VIN: {entered_value}")  # 출력: Entered VIN: 1HGCM82633A123456

# 'Stock Number' 입력 필드 찾기
stock_number_input = driver.find_element(By.ID, "ctl21_ctl19_ctl00_txtStockNumber")

# 값 입력 (예: 'STK12345')
stock_number_value = "STK12345"
stock_number_input.send_keys(stock_number_value)

# 입력된 값 확인
entered_value = stock_number_input.get_attribute("value")
print(f"Entered Stock Number: {entered_value}")  # 출력: Entered Stock Number: STK12345

# 'Residual Month' 드롭다운 요소 찾기
residual_month_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlResidualMonth")

# Select 객체 생성
select = Select(residual_month_dropdown)

# 값 선택 (예: '202411')
# value="202412"
# value="202411"
residual_month_value = "202411"
select.select_by_value(residual_month_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Residual Month: {selected_option.text}")  # 출력: Selected Residual Month: November, 2024


# 'Vehicle Condition' 드롭다운 요소 찾기
vehicle_condition_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleCondition")
time.sleep(1)


# Select 객체 생성
select = Select(vehicle_condition_dropdown)

# 값 선택 (예: 'U' for Used)
# value="N" : New
# value="U" : Used
vehicle_condition_value = "U"
select.select_by_value(vehicle_condition_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Vehicle Condition: {selected_option.text}")  # 출력: Selected Vehicle Condition: Used

# 'Vehicle Year' 드롭다운 요소 찾기
vehicle_year_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleYear")
time.sleep(1)

# Select 객체 생성
select = Select(vehicle_year_dropdown)

# 값 선택 (예: '2024')
vehicle_year_value = "2024"
select.select_by_value(vehicle_year_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Vehicle Year: {selected_option.text}")  # 출력: Selected Vehicle Year: 2024

# 'Vehicle Make' 드롭다운 요소 찾기
vehicle_make_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleMake")
time.sleep(1)

# Select 객체 생성
select = Select(vehicle_make_dropdown)

# 값 선택 (예: 'Honda')
# <option value="">Select an option</option>
# <option value="AC">Acura</option>
# <option value="AR">Alfa Romeo</option>
# <option value="AU">Audi</option>
# <option value="BM">BMW</option>
# <option value="BU">Buick</option>
# <option value="CA">Cadillac</option>
# <option value="CV">Chevrolet</option>
# <option value="CH">Chrysler</option>
# <option value="DW">Daewoo</option>
# <option value="DO">Dodge</option>
# <option value="FI">Fiat</option>
# <option value="FK">Fisker</option>
# <option value="FO">Ford</option>
# <option value="GN">Genesis</option>
# <option value="GM">GMC</option>
# <option value="HO">Honda</option>
# <option value="HU">Hummer</option>
# <option value="HY">Hyundai</option>
# <option value="IE">Ineos</option>
# <option value="IN">Infiniti</option>
# <option value="IS">Isuzu</option>
# <option value="JG">Jaguar</option>
# <option value="JE">Jeep</option>
# <option value="KI">Kia</option>
# <option value="LR">Land Rover</option>
# <option value="LE">Lexus</option>
# <option value="LI">Lincoln</option>
# <option value="LU">Lucid</option>
# <option value="MS">Maserati</option>
# <option value="MA">Mazda</option>
# <option value="ME">Mercedes-Benz</option>
# <option value="MY">Mercury</option>
# <option value="MN">Mini</option>
# <option value="MI">Mitsubishi</option>
# <option value="NI">Nissan</option>
# <option value="OL">Oldsmobile</option>
# <option value="PL">Plymouth</option>
# <option value="PS">Polestar</option>
# <option value="PO">Pontiac</option>
# <option value="PR">Porsche</option>
# <option value="RA">Ram</option>
# <option value="RI">Rivian</option>
# <option value="SB">Saab</option>
# <option value="SA">Saturn</option>
# <option value="SC">Scion</option>
# <option value="SM">Smart</option>
# <option value="SU">Subaru</option>
# <option value="SZ">Suzuki</option>
# <option value="TE">Tesla</option>
# <option value="TO">Toyota</option>
# <option value="VF">Vinfast</option>
# <option value="VW">Volkswagen</option>
# <option value="VO">Volvo</option>

vehicle_make_value = "VO"
select.select_by_value(vehicle_make_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Vehicle Make: {selected_option.text}")  # 출력: Selected Vehicle Make: Honda


# "Vehicle Model"
# 'Vehicle Model' 드롭다운 요소 찾기
vehicle_model_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleModel")
time.sleep(1)

# Select 객체 생성
select = Select(vehicle_model_dropdown)

# 값 선택 (예: 'MDX')
vehicle_model_value = "C40"
select.select_by_value(vehicle_model_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Vehicle Model: {selected_option.text}")  # 출력: Selected Vehicle Model: MDX

# 'Vehicle Series' 드롭다운 요소 찾기
vehicle_series_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleSeries")
time.sleep(1)

# Select 객체 생성
select = Select(vehicle_series_dropdown)

# 값 선택 (예: 'Recharge Plus')
vehicle_series_value = "Recharge Plus"
select.select_by_value(vehicle_series_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Vehicle Series: {selected_option.text}")  # 출력: Selected Vehicle Series: Recharge Plus

# 'Vehicle Body Style' 드롭다운 요소 찾기
vehicle_body_style_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleBodyStyle")
time.sleep(1)

# Select 객체 생성
select = Select(vehicle_body_style_dropdown)

# 값 선택 (예: '4D Utility')
vehicle_body_style_value = "4D Utility"
select.select_by_value(vehicle_body_style_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Vehicle Body Style: {selected_option.text}")  # 출력: Selected Vehicle Body Style: 4D Utility

# 'Vehicle Includes' 드롭다운 요소 찾기
vehicle_includes_dropdown = driver.find_element(By.ID, "ctl21_ctl19_ctl00_ddlVehicleIncludes")
time.sleep(1)

# Select 객체 생성
select = Select(vehicle_includes_dropdown)

# 값 선택 (예: 'AC AT CC ES')
vehicle_includes_value = "AC AT CC ES"
select.select_by_value(vehicle_includes_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Vehicle Includes: {selected_option.text}")  # 출력: Selected Vehicle Includes: AC AT CC ES
############################################### Additional Lender Information #############################################################
###########################################################################################################################################

# 'Sales Code' 입력 필드 찾기
sales_code_input = driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtSalesCode")

# 값 입력 (예: 'ABC123')
sales_code_value = "ABC123"
sales_code_input.clear()  # 기존 값 지우기
sales_code_input.send_keys(sales_code_value)

# 입력된 값 확인
entered_value = sales_code_input.get_attribute("value")
print(f"Entered Sales Code: {entered_value}")  # 출력: Entered Sales Code: ABC123

########################################################### Program Selection #############################################################
###########################################################################################################################################
# 'program_selection' 드롭다운 요소 찾기
program_selection_dropdown = driver.find_element(By.ID, "ctl21_ctl21_ctl00_ddlProgram")
time.sleep(1)

# Select 객체 생성
select = Select(program_selection_dropdown)

# 값 선택 (예: 'AC AT CC ES')
program_selection_value = "1966416"
select.select_by_value(program_selection_value)

# 선택된 값 확인
selected_option = select.first_selected_option
print(f"Selected Program: {selected_option.text}")  

#################################################### Special Discount Program #############################################################
###########################################################################################################################################

############################################################ Purchase Details #############################################################
###########################################################################################################################################
# 'Cash Price' 입력 필드 찾기
cash_price_input = driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtCashPrice")
time.sleep(1)

# 값 입력 (예: '25000')
cash_price_value = "25000"
cash_price_input.clear()  # 기존 값 지우기
cash_price_input.send_keys(cash_price_value)

# 입력된 값 확인
entered_value = cash_price_input.get_attribute("value")
print(f"Entered Cash Price: {entered_value}")  # 출력: Entered Cash Price: 25000
#################################################################### Trade In #############################################################
###########################################################################################################################################
# 'Year' 입력 필드 찾기
year_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtYear")

# 값 입력 (예: '2024')
year_value = "2024"
year_input.clear()  # 기존 값 지우기
year_input.send_keys(year_value)

# 입력된 값 확인
entered_value = year_input.get_attribute("value")
print(f"Entered Year: {entered_value}")  # 출력: Entered Year: 2024

# 'Make' 입력 필드 찾기
make_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtMake")

# 값 입력 (예: 'Toyota')
make_value = "Toyota"
make_input.clear()  # 기존 값 지우기
make_input.send_keys(make_value)

# 입력된 값 확인
entered_value = make_input.get_attribute("value")
print(f"Entered Make: {entered_value}")  # 출력: Entered Make: Toyota

# 'Model' 입력 필드 찾기
model_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtModel")

# 값 입력 (예: 'Corolla')
model_value = "Corolla"
model_input.clear()  # 기존 값 지우기
model_input.send_keys(model_value)

# 입력된 값 확인
entered_value = model_input.get_attribute("value")
print(f"Entered Model: {entered_value}")  # 출력: Entered Model: Corolla

# 'Body Style' 입력 필드 찾기
body_style_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtBodyStyle")

# 값 입력 (예: 'Sedan')
body_style_value = "Sedan"
body_style_input.clear()  # 기존 값 지우기
body_style_input.send_keys(body_style_value)

# 입력된 값 확인
entered_value = body_style_input.get_attribute("value")
print(f"Entered Body Style: {entered_value}")  # 출력: Entered Body Style: Sedan

# 'VIN' 입력 필드 찾기
vin_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtVIN")

# 값 입력 (예: '1HGCM82633A123456')
vin_value = "1HGCM82633A123456"
vin_input.clear()  # 기존 값 지우기
vin_input.send_keys(vin_value)

# 입력된 값 확인
entered_value = vin_input.get_attribute("value")
print(f"Entered VIN: {entered_value}")  # 출력: Entered VIN: 1HGCM82633A123456


# 'Mileage' 입력 필드 찾기
mileage_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtMileage")

# 값 입력 (예: '10000')
mileage_value = "10000"
mileage_input.clear()  # 기존 값 지우기
mileage_input.send_keys(mileage_value)

# 입력된 값 확인
entered_value = mileage_input.get_attribute("value")
print(f"Entered Mileage: {entered_value}")  # 출력: Entered Mileage: 10000


# 'Allowance' 입력 필드 찾기
allowance_input = driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtAllowance")

# 값 입력 (예: '500')
allowance_value = "500"
allowance_input.clear()  # 기존 값 지우기
allowance_input.send_keys(allowance_value)

# 입력된 값 확인
entered_value = allowance_input.get_attribute("value")
print(f"Entered Allowance: {entered_value}")  # 출력: Entered Allowance: 500

#################################################################### Lien #################################################################
###########################################################################################################################################
# 'Lien Amount' 입력 필드 찾기
lien_amount_input = driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtLienAmount")

# 값 입력 (예: '2000')
lien_amount_value = "2000"
lien_amount_input.clear()  # 기존 값 지우기
lien_amount_input.send_keys(lien_amount_value)

# 입력된 값 확인
entered_value = lien_amount_input.get_attribute("value")
print(f"Entered Lien Amount: {entered_value}")  # 출력: Entered Lien Amount: 2000


################################################################### Taxes #################################################################
###########################################################################################################################################
# 'Province' 드롭다운 필드 찾기
province_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlProvince")

# 값 선택 (예: '9' -> Ontario)
province_value = "9"
select = Select(province_dropdown)  # Selenium의 Select 클래스 사용
select.select_by_value(province_value)  # 값으로 선택

# 선택된 값 확인
selected_value = select.first_selected_option.get_attribute("value")
print(f"Selected Province Value: {selected_value}")  # 출력: Selected Province Value: 9

# 선택된 텍스트 확인 (예: Ontario)
selected_text = select.first_selected_option.text
print(f"Selected Province Text: {selected_text}")  # 출력: Selected Province Text: Ontario

# 'PST' 드롭다운 필드 찾기
pst_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlPST")

# 값 선택 (예: '8' -> 8.000)
pst_value = "8"
select = Select(pst_dropdown)  # Selenium의 Select 클래스 사용
select.select_by_value(pst_value)  # 값으로 선택

# 선택된 값 확인
selected_value = select.first_selected_option.get_attribute("value")
print(f"Selected PST Value: {selected_value}")  # 출력: Selected PST Value: 8

# 선택된 텍스트 확인 (예: 8.000)
selected_text = select.first_selected_option.text
print(f"Selected PST Text: {selected_text}")  # 출력: Selected PST Text: 8.000

# 'GSTHST' 드롭다운 필드 찾기
gst_hst_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlGSTHST")

# 값 선택 (예: '5' -> 5.00)
gst_hst_value = "5"
select = Select(gst_hst_dropdown)  # Selenium의 Select 클래스 사용
select.select_by_value(gst_hst_value)  # 값으로 선택

# 선택된 값 확인
selected_value = select.first_selected_option.get_attribute("value")
print(f"Selected GSTHST Value: {selected_value}")  # 출력: Selected GSTHST Value: 5

# 선택된 텍스트 확인 (예: 5.00)
selected_text = select.first_selected_option.text
print(f"Selected GSTHST Text: {selected_text}")  # 출력: Selected GSTHST Text: 5.00

if pst_value=="0":
    # 'PSTExemption' 드롭다운 필드 찾기
    pst_exemption_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlPSTExemption")

    # 값 선택 (예: '1' -> Charitable Organization)
    pst_exemption_value = "1"
    select = Select(pst_exemption_dropdown)  # Selenium의 Select 클래스 사용
    select.select_by_value(pst_exemption_value)  # 값으로 선택

    # 선택된 값 확인
    selected_value = select.first_selected_option.get_attribute("value")
    print(f"Selected PSTExemption Value: {selected_value}")  # 출력: Selected PSTExemption Value: 1

    # 선택된 텍스트 확인 (예: Charitable Organization)
    selected_text = select.first_selected_option.text
    print(f"Selected PSTExemption Text: {selected_text}")  # 출력: Selected PSTExemption Text: Charitable Organization

if gst_hst_value=="0":
    # 'GSTExemption' 드롭다운 필드 찾기
    gst_exemption_dropdown = driver.find_element(By.ID, "ctl21_ctl27_ctl00_ddlGSTExemption")

    # 값 선택 (예: '2' -> Diplomatic)
    gst_exemption_value = "2"
    select = Select(gst_exemption_dropdown)  # Selenium의 Select 클래스 사용
    select.select_by_value(gst_exemption_value)  # 값으로 선택

    # 선택된 값 확인
    selected_value = select.first_selected_option.get_attribute("value")
    print(f"Selected GSTExemption Value: {selected_value}")  # 출력: Selected GSTExemption Value: 2

    # 선택된 텍스트 확인 (예: Diplomatic)
    selected_text = select.first_selected_option.text
    print(f"Selected GSTExemption Text: {selected_text}")  # 출력: Selected GSTExemption Text: Diplomatic
#################################################################### Fees #################################################################
###########################################################################################################################################
# 'CashDownPayment' 입력 필드 찾기
cash_down_payment_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtCashDownPayment")

# 값 입력 (예: '5000')
cash_down_payment_value = "5000"
cash_down_payment_input.clear()  # 기존 값 지우기
cash_down_payment_input.send_keys(cash_down_payment_value)  # 새로운 값 입력

# 입력된 값 확인
entered_value = cash_down_payment_input.get_attribute("value")
print(f"Entered Cash Down Payment: {entered_value}")  # 출력: Entered Cash Down Payment: 5000

# 'Rebate' 입력 필드 찾기
rebate_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtRebate")

# 값 입력 (예: '1000')
rebate_value = "1000"
rebate_input.clear()  # 기존 값 지우기
rebate_input.send_keys(rebate_value)  # 새로운 값 입력

# 입력된 값 확인
entered_value = rebate_input.get_attribute("value")
print(f"Entered Rebate: {entered_value}")  # 출력: Entered Rebate: 1000


# 'Other Taxable' 입력 필드 찾기
other_taxable_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherTaxable")

# 값 입력 (예: '500')
other_taxable_value = "500"
other_taxable_input.clear()  # 기존 값 지우기
other_taxable_input.send_keys(other_taxable_value)  # 새로운 값 입력

# 입력된 값 확인
entered_value = other_taxable_input.get_attribute("value")
print(f"Entered Other Taxable: {entered_value}")  # 출력: Entered Other Taxable: 500


# 'Other Taxable Description' 입력 필드 찾기
other_taxable_desc_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherTaxableDesc")

# 값 입력 (예: 'Example Description')
other_taxable_desc_value = "Example Description"
other_taxable_desc_input.clear()  # 기존 값 지우기
other_taxable_desc_input.send_keys(other_taxable_desc_value)  # 새로운 값 입력

# 입력된 값 확인
entered_value = other_taxable_desc_input.get_attribute("value")
print(f"Entered Other Taxable Description: {entered_value}")  # 출력: Entered Other Taxable Description: Example Description

# 'Other Non-Taxable' 입력 필드 찾기
other_non_taxable_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherNonTaxable")

# 값 입력 (예: '1000')
other_non_taxable_value = "1000"
other_non_taxable_input.clear()  # 기존 값 지우기
other_non_taxable_input.send_keys(other_non_taxable_value)  # 새로운 값 입력

# 입력된 값 확인
entered_value = other_non_taxable_input.get_attribute("value")
print(f"Entered Other Non-Taxable: {entered_value}")  # 출력: Entered Other Non-Taxable: 1000


# 'Other Non-Taxable Description' 입력 필드 찾기
other_non_taxable_desc_input = driver.find_element(By.ID, "ctl21_ctl28_ctl00_txtOtherNonTaxableDesc")

# 값 입력 (예: 'Additional Fee')
other_non_taxable_desc_value = "Additional Fee"
other_non_taxable_desc_input.clear()  # 기존 값 지우기
other_non_taxable_desc_input.send_keys(other_non_taxable_desc_value)  # 새로운 값 입력

# 입력된 값 확인
entered_value = other_non_taxable_desc_input.get_attribute("value")
print(f"Entered Other Non-Taxable Description: {entered_value}")  # 출력: Entered Other Non-Taxable Description: Additional Fee

##################################################### Aftermarket Service #################################################################
###########################################################################################################################################
# 'Extended Warranty' 입력 필드 찾기
extended_warranty_input = driver.find_element(By.ID, "ctl21_ctl30_ctl00_txtExtendedWarranty")

# 값 입력 (예: '100')
extended_warranty_value = "100"
extended_warranty_input.clear()  # 기존 값 지우기
extended_warranty_input.send_keys(extended_warranty_value)  # 새로운 값 입력

# 입력된 값 확인
entered_value = extended_warranty_input.get_attribute("value")
print(f"Entered Extended Warranty: {entered_value}")  # 출력: Entered Extended Warranty: 100

# 'Extended Warranty Term' 선택 필드 찾기
ex_warranty_term_select = Select(driver.find_element(By.ID, "ctl21_ctl30_ctl00_ddlExWarrantyTerm"))

# 값 선택 (예: 'Manufacturer' 선택)
ex_warranty_term_value = "2"  # "Manufacturer" 선택
ex_warranty_term_select.select_by_value(ex_warranty_term_value)

# 선택된 값 확인
selected_value = ex_warranty_term_select.first_selected_option.text
print(f"Selected Extended Warranty Term: {selected_value}")  # 출력: Selected Extended Warranty Term: Manufacturer

# 'Replacement Warranty' 입력 필드 찾기
replacement_input = driver.find_element(By.ID, "ctl21_ctl30_ctl00_txtReplacement")

# 값 입력 (예: '500')
replacement_value = "50"
replacement_input.clear()  # 기존 값 지우기
replacement_input.send_keys(replacement_value)

# 입력된 값 확인
entered_value = replacement_input.get_attribute("value")
print(f"Entered Replacement Warranty: {entered_value}")  # 출력: Entered Replacement Warranty: 500


# 'Life Insurance' 입력 필드 찾기
life_insurance_input = driver.find_element(By.ID, "ctl21_ctl30_ctl00_txtLifeInsurance")

# 값 입력 (예: '1000')
life_insurance_value = "10"
life_insurance_input.clear()  # 기존 값 지우기
life_insurance_input.send_keys(life_insurance_value)

# 입력된 값 확인
entered_value = life_insurance_input.get_attribute("value")
print(f"Entered Life Insurance: {entered_value}")  # 출력: Entered Life Insurance: 1000


# 'AH Insurance' 입력 필드 찾기
ah_insurance_input = driver.find_element(By.ID, "ctl21_ctl30_ctl00_txtAHInsurance")

# 값 입력 (예: '500')
ah_insurance_value = "10"
ah_insurance_input.clear()  # 기존 값 지우기
ah_insurance_input.send_keys(ah_insurance_value)

# 입력된 값 확인
entered_value = ah_insurance_input.get_attribute("value")
print(f"Entered AH Insurance: {entered_value}")  # 출력: Entered AH Insurance: 500

################################################## Defereal and Payment Date Options ######################################################
###########################################################################################################################################


######################################################### Financing Terms #################################################################
###########################################################################################################################################

# 'Term' 드롭다운 필드 찾기
term_dropdown = driver.find_element(By.ID, "ctl21_ctl32_ctl00_ddlTerm")

# 드롭다운 선택을 위한 Select 객체 생성
select_term = Select(term_dropdown)

# 값을 선택 (예: '24')
term_value = "24"
select_term.select_by_value(term_value)

# 선택된 값 확인
selected_option = select_term.first_selected_option
print(f"Selected Term: {selected_option.text}")  # 출력: Selected Term: 24


# 'Amortization' 드롭다운 필드 찾기
amortization_dropdown = driver.find_element(By.ID, "ctl21_ctl32_ctl00_ddlAmortization")

# 드롭다운 선택을 위한 Select 객체 생성
select_amortization = Select(amortization_dropdown)

# 값을 선택 (예: '36')
amortization_value = "36"
select_amortization.select_by_value(amortization_value)

# 선택된 값 확인
selected_option = select_amortization.first_selected_option
time.sleep(1)
print(f"Selected Amortization: {selected_option.text}")  # 출력: Selected Amortization: 36

# 'Payment Frequency' 드롭다운 필드 찾기
payment_frequency_dropdown = driver.find_element(By.ID, "ctl21_ctl32_ctl00_ddlPaymentFrequency")

# 드롭다운 선택을 위한 Select 객체 생성
select_payment_frequency = Select(payment_frequency_dropdown)

# 값을 선택 (예: 'Bi-Weekly' = value="26")
payment_frequency_value = "26"
select_payment_frequency.select_by_value(payment_frequency_value)

# 선택된 값 확인
selected_option = select_payment_frequency.first_selected_option
print(f"Selected Payment Frequency: {selected_option.text}")  # 출력: Selected Payment Frequency: Bi-Weekly

time.sleep(1)
# 'Dealer Interest Rate' 입력 필드 찾기
dealer_interest_rate_input = driver.find_element(By.ID, "ctl21_ctl32_ctl00_txtDealerInterestRate")

# 값 입력 (예: '5.5')
dealer_interest_rate_value = "5.5"
dealer_interest_rate_input.clear()  # 기존 값 지우기
dealer_interest_rate_input.send_keys(dealer_interest_rate_value)

# 입력된 값 확인
entered_value = dealer_interest_rate_input.get_attribute("value")
print(f"Entered Dealer Interest Rate: {entered_value}")  # 출력: Entered Dealer Interest Rate: 5.5
############################################################ Dealer Tools #################################################################
###########################################################################################################################################


###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################



###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################

#드라이버 종료
# time.sleep(1)
# time.sleep(1)
# time.sleep(1)
# driver.quit()