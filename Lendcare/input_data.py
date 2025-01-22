import os
import re
import time
import requests
import traceback
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import json

class DealerTrackAutomation:
    def __init__(self):
        self.session = requests.session()
        self.driver = None
        self.load_env_variables()
        self.setup_file_path()

    def load_env_variables(self):
        load_dotenv(find_dotenv())
        print("SHERWAYNISSAN = 1, MERCURY = 2, BAYSIDE = 3, BOSAUTO = 4")
        d_s_n = input("Chosse DealerShip name : ")
        if d_s_n == "1":
            self.username = os.getenv("SHERWAYNISSAN_ID")
            self.password = os.getenv("SHERWAYNISSAN_PASS")
        elif d_s_n == "2":    
            self.username = os.getenv("MERCURY_ID")
            self.password = os.getenv("MERCURY_PASS")
        elif d_s_n == "3":
            self.username = os.getenv("BAYSIDE_ID")
            self.password = os.getenv("BAYSIDE_PASS")
        elif d_s_n == "4":
            self.username = os.getenv("BOSAUTO_ID")
            self.password = os.getenv("BOSAUTO_PASS")

    def setup_file_path(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        # self.file_name = os.path.join(".", "airtable_data", f"table_list_{current_date}.json")
        # self.file_name = os.path.join(".", "airtable_data", f"table_list_2024-12-18.json")
        self.file_name = os.path.join(".", "airtable_data", f"table_list_{current_date}.json")

    def read_json_data(self, client_data_id):
        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)

                # Search for the record matching client_data_id
                matching_record = next((record for record in data if record.get("id") == client_data_id), None)
                if matching_record:
                    print(f"Found matching record for client_data_id '{client_data_id}'")
                    # print(f"Found matching record for client_data_id '{client_data_id}': {matching_record}")
                else:
                    print(f"No matching record found for client_data_id '{client_data_id}'.")

                self.data = matching_record

        except FileNotFoundError:
            print(f"File not found: {self.file_name}")
            return None

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

    def login(self):
        login_url = "https://auth.dealertrack.ca/idp/startSSO.ping?PartnerSpId=prod_dtc_sp_pingfed"
        login_data = {
            "pf.username": self.username,
            "pf.pass": self.password,
            "pf.ok": "",
            "pf.cancel": "",
            "pf.adapterId": "ARTHTMLLOGINPAGE",
        }

        response = self.session.post(login_url, data=login_data)
        response.raise_for_status()
        print("Login successful.")

    def setup_selenium_driver(self):
        options = Options()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def navigate_to_url(self, url):
        self.driver.get(url)

    def transfer_cookies_to_selenium(self):
        cookies = self.session.cookies.get_dict()
        for name, value in cookies.items():
            self.driver.add_cookie({'name': name, 'value': value})
        self.driver.refresh()

    def fill_dropdown(self, dropdown_id, value):
        wait = WebDriverWait(self.driver, 20)
        dropdown_element = wait.until(EC.element_to_be_clickable((By.ID, dropdown_id)))
        time.sleep(0.5)
        dropdown = Select(dropdown_element)
        time.sleep(0.5)
        dropdown.select_by_visible_text(value)
        # print(f"Dropdown '{dropdown_id}' selected value: {value}")

    def fill_text_field(self, field_id, text):
        field = self.driver.find_element(By.ID, field_id)
        field.send_keys(text)
        entered_value = field.get_attribute("value")
        print(f"Field '{field_id}' entered value: {entered_value}")

    def fill_sin_field(self):
        if "SIN" in self.data["fields"]:
            sin_input = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtSIN")
            sin_input.click()
            sin_input = self.driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
            sin_data = self.data["fields"].get("SIN", "")

            if len(sin_data) == 9:
                sin_input.send_keys(sin_data)
                print(f"SIN Entered: {sin_input.get_attribute('value')}")

    def fill_phone_fields(self):
        def remove_country_code_and_non_digits(phone):
            return re.sub(r'\D', '', str(phone)[-10:])  # Extract last 10 digits

        if "Phone" in self.data["fields"]:
            phone_number = remove_country_code_and_non_digits(self.data["fields"]["Phone"])

            # Fill phone field
            phone_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "ctl21_ctl20_ctl00_txtPhone"))
            )
            phone_field.click()
            phone_input = self.driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
            phone_input.send_keys(phone_number)
            print(f"Phone Number Entered: {phone_input.get_attribute('value')}")

            # Fill mobile phone field
            mobile_phone_input = self.driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
            mobile_phone_input.send_keys(phone_number)
            print(f"Mobile Phone Number Entered: {mobile_phone_input.get_attribute('value')}")

    def fill_dob_field(self):
        date_of_birth = self.data["fields"].get("Date of Birth", "")

        if date_of_birth:
            year, month, day = date_of_birth.split("-")

            # Fill month field
            month_input = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_MM")
            month_input.send_keys(month)
            print(f"Month Entered: {month_input.get_attribute('value')}")

            # Fill day field
            day_input = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_DD")
            day_input.send_keys(day)
            print(f"Day Entered: {day_input.get_attribute('value')}")

            # Fill year field
            year_input = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtDateofBirth_YYYY")
            year_input.send_keys(year)
            print(f"Year Entered: {year_input.get_attribute('value')}")

    def fill_and_submit_form(self):
        # Switch to iframe
        iframe = self.driver.find_element(By.ID, "iFrm")
        self.driver.switch_to.frame(iframe)
        self.driver.switch_to.frame("main")
        try:
            non_oem_button = self.driver.find_element(By.ID, "OEMProgramCategory1_ctl00_lblStandard")
            non_oem_button.click()
        except:
            pass
        time.sleep(0.5)
        # Select "Automotive" from ddAsset
        self.fill_dropdown("ddAsset", "Automotive")

        # Select "Scotiabank" from ddLenders
        self.fill_dropdown("ddLenders", "Lendcare Capital Inc.")
        time.sleep(0.5)
        # Select "Lease" from ddProduct
        self.fill_dropdown("ddProduct", "Loan")
        time.sleep(0.5)
        # Click the "Continue" button
        continue_button = self.driver.find_element(By.ID, "btnSave")
        continue_button.click()
        print("Form submitted successfully!")

    def fill_salutation_and_name_fields(self):
        wait = WebDriverWait(self.driver, 20)

        # Fill Salutation Dropdown
        salutation_field_id = "ctl21_ctl20_ctl00_ddlSalutation"
        try:
            salutation_dropdown = wait.until(EC.presence_of_element_located((By.ID, salutation_field_id)))
            print("Salutation dropdown loaded.")
            select = Select(salutation_dropdown)

            salutation = self.data["fields"].get("Salutation", "")
            if salutation=="Mr":
                salutation = "Mr."
            elif salutation=="Ms":
                salutation = "Ms."
            elif salutation=="Mrs":
                salutation = "Mrs."
            elif salutation=="Dr":
                salutation = "Dr."
            
            if salutation in ["Dr.", "Mr.", "Ms.", "Miss", "Mrs."]:
                select.select_by_visible_text(salutation)
            else:
                print("Salutation not recognized.")

            selected_option = select.first_selected_option
            print(f"Selected salutation: {selected_option.text}")
        except Exception as e:
            print(f"Error with salutation field: {e}")

        # Fill Name Fields
        self.fill_text_field("ctl21_ctl20_ctl00_txtFirstName", self.data["fields"].get("First Name", ""))
        self.fill_text_field("ctl21_ctl20_ctl00_txtMiddleName", self.data["fields"].get("Middle Name", ""))
        self.fill_text_field("ctl21_ctl20_ctl00_txtLastName", self.data["fields"].get("Last Name", ""))

    def select_gender(self):
        gender_select = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlGender")
        select = Select(gender_select)

        if "Gender" in self.data["fields"] and self.data["fields"]["Gender"]:
            if self.data["fields"]["Gender"] == "Male":
                select.select_by_value("MALE")
            elif self.data["fields"]["Gender"] == "Female":
                select.select_by_value("FEMALE")

        selected_option = select.first_selected_option
        print(f"Selected Gender: {selected_option.text}")

    def select_marital_status(self):
        marital_status_select = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlMaritalStatus")
        select = Select(marital_status_select)

        if "Marital Status" in self.data["fields"] and self.data["fields"]["Marital Status"]:
            marital_status_map = {
                "Married": "MR",
                "Widow / Widower": "WD",
                "Single": "SG",
                "Common Law": "CL",
                "Separated": "SP",
            }
            select.select_by_value(marital_status_map.get(self.data["fields"]["Marital Status"], ""))

        selected_option = select.first_selected_option
        print(f"Selected Marital Status: {selected_option.text}")

    def enter_email(self):
        email_input = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_txtEmail")
        email_input.send_keys(self.data["fields"].get("Email", ""))
        entered_email = email_input.get_attribute("value")
        print(f"Entered Email: {entered_email}")

    def select_language(self):
        language_dropdown = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlLanguage")
        select = Select(language_dropdown)
        select.select_by_value("en-CA")  # Select English by default

    def enter_postal_code(self, airtable_client, client_data_id):
        address = self.data["fields"].get("Address", "")
        wait = WebDriverWait(self.driver, 10)
        try:
            postal_code_input = wait.until(
                EC.presence_of_element_located((By.ID, "ctl21_ctl21_ctl00_txtPostalCode"))
            )
            print("postal_code_input field is loaded.")
        except:
            print("Timeout: postal_code_input field was not found.")

        postal_code_input.click()
        postal_code_input = self.driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
        postal_code_input.send_keys(self.data["fields"].get("Postal Code", ""))
        entered_value = postal_code_input.get_attribute("value")
        print(f"Entered Postal Code: {entered_value}")

        address_lookup_button = self.driver.find_element(By.ID, "ctl21_ctl21_ctl00_btnPostalCodeLookup")
        address_lookup_button.click()
        time.sleep(3)
        try:
            # Switch to iframe containing lookup details
            iframe = wait.until(EC.element_to_be_clickable((By.ID, "DTC$ModalPopup$Frame")))
            self.driver.switch_to.frame(iframe)

            # 테이블 로드 대기
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "gvPostalCode")))

            # 테이블 행 가져오기
            rows = self.driver.find_elements(By.XPATH, "//table[@id='gvPostalCode']/tbody/tr")

            # 첫 번째 행은 헤더이므로 제외하고 반복문 실행
            for row in rows[1:]:
                # 'Street Name' 값 가져오기
                street_name = row.find_element(By.XPATH, "./td[2]").text.strip()
                
                # 비교 값과 일치 여부 확인
                if street_name in address:
                    # 라디오 버튼 클릭
                    radio_button = row.find_element(By.XPATH, "./td[1]/input[@type='radio']")
                    radio_button.click()
                    print(f"Radio button for '{street_name}' clicked.")
                    break
                # 그냥 첫번째 것 클릭하도록 되어있다.
                else:
                    radio_button = row.find_element(By.XPATH, "./td[1]/input[@type='radio']")
                    radio_button.click()
                    print(f"Radio button for '{street_name}' clicked.")
            else:
                print(f"No matching 'Street Name' found for '{street_name}'.")
            btnOK = wait.until(EC.element_to_be_clickable((By.ID, "btnOK")))
            # 버튼 클릭
            btnOK.click()

            self.driver.switch_to.parent_frame()

            airtable_client.update_record(client_data_id, {"Notes": "Need check Address"})
        except:
            pass

        print("Address Lookup button clicked successfully!")
    
    def enter_previous_postal_code(self, airtable_client, client_data_id):

        if "OLD Duration at Current Address (Years)" in self.data["fields"]:

            old_address_year = self.data["fields"].get("OLD Duration at Current Address (Years)", "")



        if "Duration at Current Address (Years)" in self.data["fields"]:

            address_year = self.data["fields"].get("Duration at Current Address (Years)", "")



        if address_year >= 2 or old_address_year >= 2:

            return



        address = self.data["fields"].get("Previous Address", "")

        wait = WebDriverWait(self.driver, 10)

        try:

            postal_code_input = wait.until(

                EC.presence_of_element_located((By.ID, "ctl21_ctl22_ctl00_txtPostalCode"))

            )

            print("postal_code_input field is loaded.")

        except:

            print("Timeout: postal_code_input field was not found.")



        postal_code_input.click()

        postal_code_input = self.driver.find_element(By.CLASS_NAME, "MaskedEditFocus")

        postal_code_input.send_keys(self.data["fields"].get("Previous Postal Code", ""))

        entered_value = postal_code_input.get_attribute("value")

        print(f"Entered Postal Code: {entered_value}")



        address_lookup_button = self.driver.find_element(By.ID, "ctl21_ctl22_ctl00_btnPostalCodeLookup")

        address_lookup_button.click()

        time.sleep(3)

        try:

            # Switch to iframe containing lookup details

            iframe = wait.until(EC.element_to_be_clickable((By.ID, "DTC$ModalPopup$Frame")))

            self.driver.switch_to.frame(iframe)



            # 테이블 로드 대기

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "gvPostalCode")))



            # 테이블 행 가져오기

            rows = self.driver.find_elements(By.XPATH, "//table[@id='gvPostalCode']/tbody/tr")



            # 첫 번째 행은 헤더이므로 제외하고 반복문 실행

            for row in rows[1:]:

                # 'Street Name' 값 가져오기

                street_name = row.find_element(By.XPATH, "./td[2]").text.strip()

                

                # 비교 값과 일치 여부 확인

                if street_name in address:

                    # 라디오 버튼 클릭

                    radio_button = row.find_element(By.XPATH, "./td[1]/input[@type='radio']")

                    radio_button.click()

                    print(f"Radio button for '{street_name}' clicked.")

                    break

                # 그냥 첫번째 것 클릭하도록 되어있다.

                else:

                    radio_button = row.find_element(By.XPATH, "./td[1]/input[@type='radio']")

                    radio_button.click()

                    print(f"Radio button for '{street_name}' clicked.")

            else:

                print(f"No matching 'Street Name' found for '{street_name}'.")

            btnOK = wait.until(EC.element_to_be_clickable((By.ID, "btnOK")))

            # 버튼 클릭

            btnOK.click()



            self.driver.switch_to.parent_frame()



            airtable_client.update_record(client_data_id, {"Notes": "Need check Address"})

        except:

            pass



        print("Address Lookup button clicked successfully!")
        
    def select_address_type(self):
        address_type_map = {

                "Street": "ST",

                "Rural Route": "RR",

                "Postal Box": "PB",

            }

        

        address_type_dropdown = self.driver.find_element(By.ID, "ctl21_ctl21_ctl00_ddlAddressType")

        address_type_dropdown = Select(address_type_dropdown)



        # Address Type 필드가 존재할 때만 실행

        if "Address Type" in self.data["fields"] and self.data["fields"]["Address Type"]:

            address_type = self.data["fields"]["Address Type"]

            address_type_dropdown.select_by_value(address_type_map.get(address_type, ""))

        # 변경 전, OLD Address를 사용하는 경우

        else:

            address_type_dropdown.select_by_value("ST")

    

        selected_option = address_type_dropdown.first_selected_option

        print(f"Selected Address Type Current Employer: {selected_option.text}")

    def select_previous_address_type(self):
        if "OLD Duration at Current Address (Years)" in self.data["fields"]:
            old_address_year = self.data["fields"].get("OLD Duration at Current Address (Years)", "")

        if "Duration at Current Address (Years)" in self.data["fields"]:
            address_year = self.data["fields"].get("Duration at Current Address (Years)", "")

        if address_year >= 2 or old_address_year >= 2:
            return
        
        address_type_map = {
                "Street": "ST",
                "Rural Route": "RR",
                "Postal Box": "PB",
            }
        
        address_type_dropdown = self.driver.find_element(By.ID, "ctl21_ctl22_ctl00_ddlAddressType")
        address_type_dropdown = Select(address_type_dropdown)

        # Address Type 필드가 존재할 때만 실행
        if "Address Type" in self.data["fields"] and self.data["fields"]["Previous Address Type"]:
            address_type = self.data["fields"]["Previous Address Type"]
            address_type_dropdown.select_by_value(address_type_map.get(address_type, ""))
        # 변경 전, OLD Address를 사용하는 경우
        else:
            address_type_dropdown.select_by_value("ST")
    
        selected_option = address_type_dropdown.first_selected_option
        print(f"Selected Previous Address Type : {selected_option.text}")

    def enter_suit_number(self):

        suit_number_input = self.driver.find_element(By.ID, "ctl21_ctl21_ctl00_txtSuiteNumber")

        if "Suite Number" in self.data["fields"]:

            suit_number = self.data["fields"].get("Suite Number", "")

            suit_number_input.send_keys(suit_number)

        entered_value = suit_number_input.get_attribute("value")

        print(f"Entered Suite Number : {entered_value}")

    def enter_previous_suit_number(self):
        if "OLD Duration at Current Address (Years)" in self.data["fields"]:
            old_address_year = self.data["fields"].get("OLD Duration at Current Address (Years)", "")

        if "Duration at Current Address (Years)" in self.data["fields"]:
            address_year = self.data["fields"].get("Duration at Current Address (Years)", "")

        if address_year >= 2 or old_address_year >= 2:
            return
        
        suit_number_input = self.driver.find_element(By.ID, "ctl21_ctl22_ctl00_txtSuiteNumber")

        if "Previous Suite Number" in self.data["fields"]:
            p_suit_number = self.data["fields"].get("Previous Suite Number", "")
            suit_number_input.send_keys(p_suit_number)
        
        entered_value = suit_number_input.get_attribute("value")
        print(f"Entered Previous Suite Number : {entered_value}")
        
    def enter_address_number(self):

        suit_address_number_input = self.driver.find_element(By.ID, "ctl21_ctl21_ctl00_txtStreetNumber")

        if "Street Number" in self.data["fields"]:

            street_number = self.data["fields"].get("Street Number", "")
            suit_address_number_input.send_keys(street_number)

        entered_value = suit_address_number_input.get_attribute("value")

        print(f"Entered Address Number : {entered_value}")

    def enter_previous_address_number(self):
        if "OLD Duration at Current Address (Years)" in self.data["fields"]:
            old_address_year = self.data["fields"].get("OLD Duration at Current Address (Years)", "")

        if "Duration at Current Address (Years)" in self.data["fields"]:
            address_year = self.data["fields"].get("Duration at Current Address (Years)", "")

        if address_year >= 2 or old_address_year >= 2:
            return
        
        suit_address_number_input = self.driver.find_element(By.ID, "ctl21_ctl22_ctl00_txtStreetNumber")

        if "Previous Street Number" in self.data["fields"]:
            p_street_number = self.data["fields"].get("Previous Street Number", "")    
            suit_address_number_input.send_keys(p_street_number)

        entered_value = suit_address_number_input.get_attribute("value")
        print(f"Entered Previous Address Number : {entered_value}")

    def enter_street_name(self):

        street_name_input = self.driver.find_element(By.ID, "ctl21_ctl21_ctl00_txtStreetName")

        if "Street Name" in self.data["fields"]:

            street_name = self.data["fields"].get("Street Name", "")

            street_name_input.send_keys(street_name)

        else: 
            street_name_input.send_keys("Street Name")

        entered_value = street_name_input.get_attribute("value")

        print(f"Entered Street Name : {entered_value}")

    def enter_previous_street_name(self):
        if "OLD Duration at Current Address (Years)" in self.data["fields"]:
            old_address_year = self.data["fields"].get("OLD Duration at Current Address (Years)", "")

        if "Duration at Current Address (Years)" in self.data["fields"]:
            address_year = self.data["fields"].get("Duration at Current Address (Years)", "")

        if address_year >= 2 or old_address_year >= 2:
            return
        
        street_name_input = self.driver.find_element(By.ID, "ctl21_ctl22_ctl00_txtStreetName")

        if "Previous Street Name" in self.data["fields"]:
            p_street_name = self.data["fields"].get("Previous Street Name", "")
            street_name_input.send_keys(p_street_name)
        else: 
            street_name_input.send_keys("Street Name")
        entered_value = street_name_input.get_attribute("value")
        print(f"Entered Previous Street Name : {entered_value}")

    def enter_street_type(self):
        street_type_dropdown = self.driver.find_element(By.ID, "ctl21_ctl21_ctl00_ddlStreetType")
        street_type_dropdown = Select(street_type_dropdown)

        # Street Type 필드가 존재할 때만 실행
        if "Street Type" in self.data["fields"] and self.data["fields"]["Street Type"]:
            street_type = self.data["fields"]["Street Type"]
            street_type_dropdown.select_by_visible_text(street_type)
        # 변경 전, OLD Address를 사용하는 경우
        else:
            return
    
        selected_option = street_type_dropdown.first_selected_option
        print(f"Selected Street Type Current Employer: {selected_option.text}")

    def enter_previous_street_type(self):
        if "OLD Duration at Current Address (Years)" in self.data["fields"]:
            old_address_year = self.data["fields"].get("OLD Duration at Current Address (Years)", "")

        if "Duration at Current Address (Years)" in self.data["fields"]:
            address_year = self.data["fields"].get("Duration at Current Address (Years)", "")

        if address_year >= 2 or old_address_year >= 2:
            return
        
        street_type_dropdown = self.driver.find_element(By.ID, "ctl21_ctl22_ctl00_ddlStreetType")
        street_type_dropdown = Select(street_type_dropdown)

        # Street Type 필드가 존재할 때만 실행
        if "Previous Street Type" in self.data["fields"] and self.data["fields"]["Previous Street Type"]:
            street_type = self.data["fields"]["Previous Street Type"]
            street_type_dropdown.select_by_visible_text(street_type)
        # 변경 전, OLD Address를 사용하는 경우
        else:
            return
    
        selected_option = street_type_dropdown.first_selected_option
        print(f"Selected Street Type Current Employer: {selected_option.text}")

    def enter_direction(self):
        direction_dropdown = self.driver.find_element(By.ID, "ctl21_ctl21_ctl00_ddlStreetType")
        direction_dropdown = Select(direction_dropdown)

        # Street Type 필드가 존재할 때만 실행
        if "Direction" in self.data["fields"] and self.data["fields"]["Direction"]:
            direction_status_map = {
                "NORTH": "N",
                "NORTH EAST": "NE",
                "NORTH WEST": "NW",
                "SOUTH": "S",
                "SOUTH EAST": "SE",
                "SOUTH WEST": "SW",
                "WEST": "W",
            }
            status = self.data["fields"]["Direction"]
            direction_dropdown.select_by_value(direction_status_map.get(status, ""))
        # 변경 전, OLD Address를 사용하는 경우
        else:
            return
    
        selected_option = direction_dropdown.first_selected_option
        print(f"Selected Direction: {selected_option.text}")

    def enter_duration_at_current_address(self):
        wait = WebDriverWait(self.driver, 20)
        try:
            duration_years_input = wait.until(
                EC.presence_of_element_located((By.ID, "ctl21_ctl21_ctl00_CDurationCurrentAddress_Y"))
            )
            print("Duration field is loaded.")
        except:
            print("Timeout: Duration input field was not found.")

        # 변경 전 OLD Duration을 사용하는 경우

        if "OLD Duration at Current Address (Years)" in self.data["fields"]:

            duration_years_input.send_keys(self.data["fields"].get("OLD Duration at Current Address (Years)", ""))

            entered_value = duration_years_input.get_attribute("value")

            print(f"Entered Duration in Years: {entered_value}")



        if "Duration at Current Address (Years)" in self.data["fields"]:

            duration_years_input.send_keys(self.data["fields"].get("Duration at Current Address (Years)", ""))

            entered_value = duration_years_input.get_attribute("value")

            print(f"Entered Duration in Years: {entered_value}")


        if "Duration at Current Address (Month)" in self.data["fields"]:

            duration_months_input = self.driver.find_element(By.ID, "ctl21_ctl21_ctl00_CDurationCurrentAddress_M")

            duration_months_value = self.data["fields"].get("Duration at Current Address (Month)", "")  # Assuming default value for demonstration

            duration_months_input.send_keys(duration_months_value)

            entered_value = duration_months_input.get_attribute("value")

            print(f"Entered Duration in Months: {entered_value}")

    def enter_previous_direction(self):
        if "OLD Duration at Current Address (Years)" in self.data["fields"]:
            old_address_year = self.data["fields"].get("OLD Duration at Current Address (Years)", "")

        if "Duration at Current Address (Years)" in self.data["fields"]:
            address_year = self.data["fields"].get("Duration at Current Address (Years)", "")

        if address_year >= 2 or old_address_year >= 2:
            return
        
        direction_dropdown = self.driver.find_element(By.ID, "ctl21_ctl22_ctl00_ddlDirection")
        direction_dropdown = Select(direction_dropdown)

        # Street Type 필드가 존재할 때만 실행
        if "Previous Direction" in self.data["fields"] and self.data["fields"]["Previous Direction"]:
            direction_status_map = {
                "NORTH": "N",
                "NORTH EAST": "NE",
                "NORTH WEST": "NW",
                "SOUTH": "S",
                "SOUTH EAST": "SE",
                "SOUTH WEST": "SW",
                "WEST": "W",
            }
            status = self.data["fields"]["Previous Direction"]
            direction_dropdown.select_by_value(direction_status_map.get(status, ""))
        # 변경 전, OLD Address를 사용하는 경우
        else:
            return
    
        selected_option = direction_dropdown.first_selected_option
        print(f"Selected Direction: {selected_option.text}")

    def enter_duration_at_previous_address(self):
        if "OLD Duration at Current Address (Years)" in self.data["fields"]:
            address_year = self.data["fields"].get("OLD Duration at Current Address (Years)", "")
            

        if "Duration at Current Address (Years)" in self.data["fields"]:
            address_year = self.data["fields"].get("Duration at Current Address (Years)", "")
            
        if int(address_year) > 2:
            return
        
        wait = WebDriverWait(self.driver, 20)
        try:
            duration_years_input = wait.until(
                EC.presence_of_element_located((By.ID, "ctl21_ctl22_ctl00_CDurationPreviousAddress_Y"))
            )
            print("Duration field is loaded.")
        except:
            print("Timeout: Duration input field was not found.")

        if "Duration at Previous Address (Years)" in self.data["fields"]:
            duration_years_input.send_keys(self.data["fields"].get("Duration at Previous Address (Years)", ""))
            entered_value = duration_years_input.get_attribute("value")
            print(f"Entered Duration in Years: {entered_value}")
        
        if "Duration at Previous Address (Month)" in self.data["fields"]:
            duration_months_input = self.driver.find_element(By.ID, "ctl21_ctl22_ctl00_CDurationPreviousAddress_M")
            duration_months_value = self.data["fields"].get("Duration at Previous Address (Month)", "")  # Assuming default value for demonstration
            duration_months_input.send_keys(duration_months_value)
            entered_value = duration_months_input.get_attribute("value")
            print(f"Entered Duration in Months: {entered_value}")

    
    def select_housing_status(self):
        home_dropdown = self.driver.find_element(By.ID, "ctl21_ctl23_ctl00_ddlHome")
        select = Select(home_dropdown)

        if "Housing Status" in self.data["fields"] and self.data["fields"]["Housing Status"]:
            housing_status_map = {
                "Own with Mortgage": "OW",
                "Own Free & Clear": "OF",
                "Rent": "RE",
                "Living with Parents": "PA",
            }
            status = self.data["fields"]["Housing Status"]
            select.select_by_value(housing_status_map.get(status, ""))

            if status == "Own with Mortgage":
                mortgage_holder_input = self.driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMortgageHolder")
                mortgage_holder_input.clear()
                mortgage_holder_input.send_keys(self.data["fields"].get("Lender", ""))
                entered_value = mortgage_holder_input.get_attribute("value")
                print(f"Entered Mortgage Holder: {entered_value}")

        selected_option = select.first_selected_option
        print(f"Selected Home Option: {selected_option.text}")

    def enter_market_value_and_payments(self):
        market_value_input = self.driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtmarketValue")
        market_value_input.clear()
        # print("Market Value : ",self.data["fields"]["Market Value"])
        # print(self.data["fields"].get("Market Value", ""))
        market_value_input.send_keys(self.data["fields"].get("Market Value", ""))
        market_value_input.send_keys(Keys.TAB)
        entered_value = market_value_input.get_attribute("value")
        print(f"Entered Market Value: {entered_value}")

        mortgage_amount_input = self.driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMortgageAmount")
        mortgage_amount_input.clear()
        mortgage_amount_input.send_keys(self.data["fields"].get("Mortgage Amount", ""))
        mortgage_amount_input.send_keys(Keys.TAB)
        entered_value = mortgage_amount_input.get_attribute("value")
        print(f"Entered Mortgage Amount: {entered_value}")

        monthly_payment_input = self.driver.find_element(By.ID, "ctl21_ctl23_ctl00_txtMonthlyPayment")
        monthly_payment_input.clear()
        monthly_payment_input.send_keys(self.data["fields"].get("Monthly Payment", ""))
        monthly_payment_input.send_keys(Keys.TAB)
        entered_value = monthly_payment_input.get_attribute("value")
        print(f"Entered Monthly Payment: {entered_value}")

    def select_employment_type(self):
        employment_type_dropdown = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlTypeCurEmp")
        select_employment_type = Select(employment_type_dropdown)

        if "Employment Status" in self.data["fields"] and self.data["fields"]["Employment Status"]:
            employment_type_map = {
                "At Home": "At home",
                "Executive": "Executive",
                "Labourer": "Labourer",
                "Office Staff": "Office Staff",
                "Other": "Other",
                "Production": "Production",
                "Progessional": "Professional",
                "Retired": "Retired",
                "Sales": "Sales",
                "Self-Employed": "Self-Employed",
                "Service": "Service",
                "Trades": "Trades",
                "Student": "Student",
                "Unemployed": "Unemployed",
            }
            status = self.data["fields"]["Employment Type"]
            select_employment_type.select_by_value(employment_type_map.get(status, ""))

        selected_option = select_employment_type.first_selected_option
        print(f"Selected Employment Type: {selected_option.text}")

    def select_previous_employment_type(self):
        employment_type_dropdown = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_ddlType")
        select_employment_type = Select(employment_type_dropdown)

        if "Previous Employment Status" in self.data["fields"] and self.data["fields"]["Previous Employment Status"]:
            employment_type_map = {
                "At Home": "At home",
                "Executive": "Executive",
                "Labourer": "Labourer",
                "Office Staff": "Office Staff",
                "Other": "Other",
                "Production": "Production",
                "Progessional": "Professional", # airtable typo
                "Retired": "Retired",
                "Sales": "Sales",
                "Self-Employed": "Self-Employed",
                "Service": "Service",
                "Trades": "Trades",
                "Student": "Student",
                "Unemployed": "Unemployed",
            }
            status = self.data["fields"]["Previous Employment Type"]
            select_employment_type.select_by_value(employment_type_map.get(status, ""))

        selected_option = select_employment_type.first_selected_option
        print(f"Selected Previous Employment Type: {selected_option.text}")

    def enter_employer_name(self):
        current_employer_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtEmployerCurEmp")
        current_employer_input.send_keys(self.data["fields"].get("Employer Name", ""))
        entered_value = current_employer_input.get_attribute("value")
        print(f"Entered Current Employer: {entered_value}")

    def enter_previous_employer_name(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        current_employer_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtEmployer")
        current_employer_input.send_keys(self.data["fields"].get("Previous Employer Name", ""))
        entered_value = current_employer_input.get_attribute("value")
        print(f"Entered Previous Employer: {entered_value}")

    def select_employment_status_dropdown(self):
        employment_status_dropdown = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlStatusCurEmp")
        select = Select(employment_status_dropdown)

        if "Employment Status" in self.data["fields"] and self.data["fields"]["Employment Status"]:
            employment_status_map = {
                "Full-time": "FT",
                "Full Time (Probation)": "FTP",
                "Part Time (Casual)": "PTC",
                "Part Time (Regular)": "PTR",
                "Retired": "RET",
                "Seasonal Summer": "SEAS",
                "Seasonal Winter": "SEAW",
                "Self Employed": "SE",
            }
        
            status = self.data["fields"]["Employment Status"]
            select.select_by_value(employment_status_map.get(status, ""))

        selected_option = select.first_selected_option
        print(f"Selected Employment Status: {selected_option.text}")

    def enter_occupation(self):
        occupation_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtOccupationCurEmp")
        occupation_input.send_keys(self.data["fields"].get("Occupation", ""))
        entered_value = occupation_input.get_attribute("value")
        print(f"Entered Occupation: {entered_value}")

    def enter_previous_occupation(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        occupation_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtOccupation")
        occupation_input.send_keys(self.data["fields"].get("Previous Occupation", ""))
        entered_value = occupation_input.get_attribute("value")
        print(f"Entered Previous Occupation: {entered_value}") 

    def enter_duration_of_employment(self):
        wait = WebDriverWait(self.driver, 20)
        try:
            duration_years_input = wait.until(
                EC.presence_of_element_located((By.ID, "ctl21_ctl24_ctl00_CDurationCurrentEmployerAddress_Y"))
            )
            print("Duration field is loaded.")
        except:
            print("Timeout: Duration input field was not found.")

        if "OLD Duration of Employment" in self.data["fields"]:

            duration_years_input.send_keys(self.data["fields"].get("OLD Duration of Employment", ""))

            entered_value = duration_years_input.get_attribute("value")

            print(f"Entered Duration of Employment in Years: {entered_value}")



        if "Duration of Employment (Years)" in self.data["fields"]:

            duration_years_input.send_keys(self.data["fields"].get("Duration of Employment (Years)", ""))

            entered_value = duration_years_input.get_attribute("value")

            print(f"Entered Duration of Employment in Years: {entered_value}")

        if "Duration of Employment (Month)" in self.data["fields"]:

            duration_months_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_CDurationCurrentEmployerAddress_M")

            duration_months_value = self.data["fields"].get("Duration of Employment (Month)", "")

        

            duration_months_input.send_keys(duration_months_value)

            entered_value = duration_months_input.get_attribute("value")

            print(f"Entered Duration of Employment in Months: {entered_value}")

    def enter_previous_duration_of_employment(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        wait = WebDriverWait(self.driver, 20)
        try:
            duration_years_input = wait.until(
                EC.presence_of_element_located((By.ID, "ctl21_ctl25_ctl00_CDurationPreviousEmployerAddress_Y"))
            )
            print("Duration field is loaded.")
        except:
            print("Timeout: Duration input field was not found.")

        if "Previous Duration of Employment" in self.data["fields"]:
            duration_years_input.send_keys(self.data["fields"].get("Previous Duration of Employment", ""))
            entered_value = duration_years_input.get_attribute("value")
            print(f"Entered Duration of Employment in Years: {entered_value}")

        # if "Duration of Employment (Month)" in self.data["fields"]:
        #     duration_months_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_CDurationCurrentEmployerAddress_M")
        #     duration_months_value = self.data["fields"].get("Duration of Employment (Month)", "")        
        #     duration_months_input.send_keys(duration_months_value)
        #     entered_value = duration_months_input.get_attribute("value")
        #     print(f"Entered Duration of Employment in Months: {entered_value}")

    def select_address_type_cur_employment(self):
        address_type_cur_employment_dropdown = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlAddressTypeCurEmp")
        address_type_cur_employment_dropdown = Select(address_type_cur_employment_dropdown)

        if "Address Type Current Employer" in self.data["fields"] and self.data["fields"]["Address Type Current Employer"]:
            address_type_map = {
                "Street": "ST",
                "Rural Route": "RR",
                "Postal Box": "PB",
            }
            status = self.data["fields"]["Address Type Current Employer"]
            address_type_cur_employment_dropdown.select_by_value(address_type_map.get(status, ""))
        else:
            address_type_cur_employment_dropdown.select_by_value("ST")
    
        selected_option = address_type_cur_employment_dropdown.first_selected_option
        print(f"Selected Address Type Current Employer: {selected_option.text}")

    def select_address_type_prev_employment(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        address_type_cur_employment_dropdown = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_ddlAddressType")
        address_type_cur_employment_dropdown = Select(address_type_cur_employment_dropdown)

        if "Address Type Current Employer" in self.data["fields"] and self.data["fields"]["Address Type Current Employer"]:
            address_type_map = {
                "Street": "ST",
                "Rural Route": "RR",
                "Postal Box": "PB",
            }
            status = self.data["fields"]["Address Type Current Employer"]
            address_type_cur_employment_dropdown.select_by_value(address_type_map.get(status, ""))
        else:
            address_type_cur_employment_dropdown.select_by_value("ST")
    
        selected_option = address_type_cur_employment_dropdown.first_selected_option
        print(f"Selected Address Type Current Employer: {selected_option.text}")

    def select_previous_employment_status_dropdown(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        employment_status_dropdown = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_ddlStatus")
        select = Select(employment_status_dropdown)

        if "Previous Employment Status" in self.data["fields"] and self.data["fields"]["Previous Employment Status"]:
            employment_status_map = {
                "Full-time": "FT",
                "Full Time (Probation)": "FTP",
                "Part Time (Casual)": "PTC",
                "Part Time (Regular)": "PTR",
                "Retired": "RET",
                "Seasonal Summer": "SEAS",
                "Seasonal Winter": "SEAW",
                "Self Employed": "SE",
            }
        
            status = self.data["fields"]["Previous Employment Status"]
            select.select_by_value(employment_status_map.get(status, ""))

        selected_option = select.first_selected_option
        print(f"Selected Previous Employment Status: {selected_option.text}")

    def enter_suit_number_cur_employer(self):
        suit_number_cur_employer_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtSuiteNumberCurEmp")
        if "Employer Address" in self.data["fields"]:

            employer_address = self.data["fields"].get("Employer Address", "")

            pattern = r"(\d+), (\d+)\s+([\w\s]+)\s(\w+),\s([\w\s]+)"

            match = re.match(pattern, employer_address)

            if match:

                unit_number = match.group(1)

                suit_number_cur_employer_input.send_keys(unit_number)
        entered_value = suit_number_cur_employer_input.get_attribute("value")
        print(f"Entered Suite Number Current Employer: {entered_value}")

    def enter_suit_number_prev_employer(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        suit_number_prev_employer_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtSuiteNumber")

        if "Previous Employer Suite Number" in self.data["fields"]:
            prev_employer_suit_number = self.data["fields"].get("Previous Employer Suite Number", "")
            suit_number_prev_employer_input.send_keys(prev_employer_suit_number)
            entered_value = suit_number_prev_employer_input.get_attribute(prev_employer_suit_number)
            print(f"Entered Suite Number Current Employer: {entered_value}")

    def enter_street_number_cur_employer(self):
        street_number_cur_employer_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtStreetNumberCurEmp")
        if "Employer Address" in self.data["fields"]:

            employer_address = self.data["fields"].get("Employer Address", "")

            pattern = r"(\d+), (\d+)\s+([\w\s]+)\s(\w+),\s([\w\s]+)"

            match = re.match(pattern, employer_address)

            if match:

                street_number = match.group(2)

                street_number_cur_employer_input.send_keys(street_number)

        else:

            street_number_cur_employer_input.send_keys(490) # for test
        entered_value = street_number_cur_employer_input.get_attribute("value")
        print(f"Entered Street Number Current Employer: {entered_value}")

    def enter_street_number_prev_employer(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        street_number_prev_employer_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtStreetNumber")

        if "Previous Employer Street Number" in self.data["fields"]:
            prev_street_number = self.data["fields"].get("Previous Employer Street Number", "")
            entered_value = street_number_prev_employer_input.get_attribute(prev_street_number)
            print(f"Entered Street Number Current Employer: {entered_value}")

    def enter_street_name_cur_employer(self):
        street_name_cur_employer_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtStreetNameCurEmp")
        if "Employer Address" in self.data["fields"]:

            employer_address = self.data["fields"].get("Employer Address", "")

            pattern = r"(\d+), (\d+)\s+([\w\s]+)\s(\w+),\s([\w\s]+)"

            match = re.match(pattern, employer_address)

            if match:

                street_name = match.group(3).strip()

                street_name_cur_employer_input.send_keys(street_name)

        else:

            street_name_cur_employer_input.send_keys("YORK") # for test
        entered_value = street_name_cur_employer_input.get_attribute("value")
        print(f"Entered Street Name Current Employe: {entered_value}")

    def enter_street_name_prev_employer(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        street_name_prev_employer_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtStreetName")
        if "Previous Employer Street Name" in self.data["fields"]:
            employer_address = self.data["fields"].get("Previous Employer Street Name", "")
            street_name_prev_employer_input.send_keys(employer_address)
            entered_value = street_name_prev_employer_input.get_attribute(employer_address)
            print(f"Entered Street Name Previous Employe: {entered_value}")
    
    def enter_street_number_prev_employer(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        street_number_prev_employer_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtStreetNumber")

        if "Previous Employer Street Number" in self.data["fields"]:
            prev_street_number = self.data["fields"].get("Previous Employer Street Number", "")
            entered_value = street_number_prev_employer_input.get_attribute(prev_street_number)
            print(f"Entered Street Number Current Employer: {entered_value}")

    def select_street_type_cur_employment(self):
        street_type_cur_employment_dropdown = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlStreetTypeCurEmp")

        street_type_cur_employment_dropdown = Select(street_type_cur_employment_dropdown)

        if "Employer Street Type" in self.data["fields"]:
            street_type = self.data["fields"]["Employer Street Type"]
            street_type_cur_employment_dropdown.select_by_visible_text(street_type)
        # 변경 전, OLD Address를 사용하는 경우
        else:
            return
        
        selected_option = street_type_cur_employment_dropdown.first_selected_option

        print(f"Selected Address Type Current Employer: {selected_option.text}")

    def select_street_type_prev_employment(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        street_type_cur_employment_dropdown = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_ddlStreetType")
        street_type_cur_employment_dropdown = Select(street_type_cur_employment_dropdown)

        # Street Type 필드가 존재할 때만 실행
        if "Previous Employer Street Type" in self.data["fields"] and self.data["fields"]["Previous Employer Street Type"]:
            street_type = self.data["fields"]["Previous Employer Street Type"]
            street_type_cur_employment_dropdown.select_by_visible_text(street_type)
        # 변경 전, OLD Address를 사용하는 경우
        else:
            return
    
        selected_option = street_type_cur_employment_dropdown.first_selected_option
        print(f"Selected Street Type Previous Employer: {selected_option.text}")

    def select_direction_cur_employment(self):
        direction_dropdown = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_ddlDirectionCurEmp")
        direction_dropdown = Select(direction_dropdown)

        # Street Type 필드가 존재할 때만 실행
        if "Employer Direction" in self.data["fields"] and self.data["fields"]["Employer Direction"]:
            direction_status_map = {
                "NORTH": "N",
                "NORTH EAST": "NE",
                "NORTH WEST": "NW",
                "SOUTH": "S",
                "SOUTH EAST": "SE",
                "SOUTH WEST": "SW",
                "WEST": "W",
            }
            status = self.data["fields"]["Employer Direction"]
            direction_dropdown.select_by_value(direction_status_map.get(status, ""))
        # 변경 전, OLD Address를 사용하는 경우
        else:
            return
    
        selected_option = direction_dropdown.first_selected_option
        print(f"Selected Employer Direction: {selected_option.text}")
    
    def select_direction_prev_employment(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        direction_dropdown = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_ddlDirection")
        direction_dropdown = Select(direction_dropdown)

        # Street Type 필드가 존재할 때만 실행
        if "Previous Employer Direction" in self.data["fields"] and self.data["fields"]["Previous Employer Direction"]:
            direction_status_map = {
                "NORTH": "N",
                "NORTH EAST": "NE",
                "NORTH WEST": "NW",
                "SOUTH": "S",
                "SOUTH EAST": "SE",
                "SOUTH WEST": "SW",
                "WEST": "W",
            }
            status = self.data["fields"]["Previous Employer Direction"]
            direction_dropdown.select_by_value(direction_status_map.get(status, ""))
        # 변경 전, OLD Address를 사용하는 경우
        else:
            return
    
        selected_option = direction_dropdown.first_selected_option
        print(f"Selected Previous Employer Direction: {selected_option.text}")

    def enter_employer_city(self):
        employer_city_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00__txtCityCurEmp")
        employer_city_input.clear()
        employer_city_input.send_keys(self.data["fields"].get("Employer City", ""))
        entered_value = employer_city_input.get_attribute("value")
        print(f"Entered Employer City: {entered_value}")

    def enter_previous_employer_city(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        employer_city_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtCity")
        employer_city_input.clear()
        employer_city_input.send_keys(self.data["fields"].get("Previous Employer City", ""))
        entered_value = employer_city_input.get_attribute("value")
        print(f"Entered Previous Employer City: {entered_value}")

    def select_employer_province_dropdown(self):
        employer_province_dropdown = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00__ddlProvinceCurEmp")
        select = Select(employer_province_dropdown)

        employer_province_map = {
                "Ontario": "9",
                "Quebec": "11",
            }
        status = self.data["fields"]["Employer Province"]
        select.select_by_visible_text(status)
        selected_option = select.first_selected_option
        print(f"Selected Employer Province: {selected_option.text}")

    def select_previous_employer_province_dropdown(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        employer_province_dropdown = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_ddlProvince")
        select = Select(employer_province_dropdown)

        employer_province_map = {
                "Ontario": "9",
                "Quebec": "11",
            }
        status = self.data["fields"]["Previous Employer Province"]
        select.select_by_visible_text(status)
        selected_option = select.first_selected_option
        print(f"Selected Previous Employer Province: {selected_option.text}")

    def enter_employer_postal_code(self):
        employer_postal_code_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtPostalCodeCurEmp")
        employer_postal_code_input.click()
        employer_postal_code_input = self.driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
        employer_postal_code_input.send_keys(self.data["fields"].get("Employer Postal Code", ""))
        entered_value = employer_postal_code_input.get_attribute("value")
        print(f"Entered Employer Postal Code: {entered_value}")

    def enter_previous_employer_postal_code(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        employer_postal_code_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtPostalCode")
        employer_postal_code_input.click()
        employer_postal_code_input = self.driver.find_element(By.CLASS_NAME, "MaskedEditFocus")
        employer_postal_code_input.send_keys(self.data["fields"].get("Previous Employer Postal Code", ""))
        entered_value = employer_postal_code_input.get_attribute("value")
        print(f"Entered Previous Employer Postal Code: {entered_value}")

    def enter_employer_phone(self):
        def remove_country_code_and_non_digits(phone):
            return re.sub(r'\D', '', str(phone)[-10:])  # Extract last 10 digits
        
        if "Employer Phone" in self.data["fields"]:
            employer_phone_number = remove_country_code_and_non_digits(self.data["fields"]["Employer Phone"])
            employer_phone_input = self.driver.find_element(By.ID, "ctl21_ctl24_ctl00_txtTelephoneCurEmp")
            employer_phone_input.send_keys(employer_phone_number)
            entered_value = employer_phone_input.get_attribute("value")
            print(f"Entered Employer Phone: {entered_value}")

    def enter_previous_employer_phone(self):
        if "Duration of Employment (Years)" in self.data["fields"]:
            emlpoyment_duration_year = self.data["fields"].get("Duration of Employment (Years)", "")
        
        if "OLD Duration of Employment" in self.data["fields"]:
            old_emlpoyment_duration_year = self.data["fields"].get("OLD Duration of Employment", "")

        if emlpoyment_duration_year >= 2 or old_emlpoyment_duration_year >= 2:
            return
        
        def remove_country_code_and_non_digits(phone):
            return re.sub(r'\D', '', str(phone)[-10:])  # Extract last 10 digits
        
        if "Previous Employer Phone" in self.data["fields"]:
            employer_phone_number = remove_country_code_and_non_digits(self.data["fields"]["Previous Employer Phone"])
            employer_phone_input = self.driver.find_element(By.ID, "ctl21_ctl25_ctl00_txtTelephone")
            employer_phone_input.send_keys(employer_phone_number)
            entered_value = employer_phone_input.get_attribute("value")
            print(f"Entered Employer Phone: {entered_value}")

    def enter_gross_income(self):
        gross_income_input = self.driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtGrossIncome")
        gross_income_input.clear()
        if "Gross Income" in self.data["fields"]:
            gross_income_input.send_keys(self.data["fields"].get("Gross Income", ""))
        entered_value = gross_income_input.get_attribute("value")
        print(f"Entered Gross Income (Monthly or Annually): {entered_value}")

    def select_gross_income_per_dropdown(self):
        gross_income_per_dropdown = self.driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlIncomeBasis")
        select = Select(gross_income_per_dropdown)

        gross_income_per_map = {
                "Year": "1",
                "Month": "12",
                "Week": "52",
            }
        status = self.data["fields"]["Gross Income Time Period"]
        select.select_by_value(gross_income_per_map.get(status, ""))
        selected_option = select.first_selected_option
        print(f"Selected Gross Income Per: {selected_option.text}")

    def select_other_income_type_dropdown(self):
        other_income_type_dropdown = self.driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlOtherIncomeType")
        select = Select(other_income_type_dropdown)

        select.select_by_visible_text(self.data["fields"].get("Other Income Type", ""))
        selected_option = select.first_selected_option
        print(f"Selected Other Income Type: {selected_option.text}")

        if self.data["fields"].get("Other Income Type", "") == "Other":
            self.enter_other_description()

    def enter_other_income(self):
        other_income_input = self.driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtOtherIncome")
        other_income_input.clear()
        other_income_input.send_keys(self.data["fields"].get("Other Income", ""))
        entered_value = other_income_input.get_attribute("value")
        print(f"Entered Other Income : {entered_value}")

    def select_other_income_per_dropdown(self):
        other_income_per_dropdown = self.driver.find_element(By.ID, "ctl21_ctl26_ctl00_ddlOtherIncomeType")
        select = Select(other_income_per_dropdown)

        other_income_per_map = {
                "Year": "1",
                "Month": "12",
                "Week": "52",
            }
        status = self.data["fields"]["Other Income Time Period"]
        select.select_by_value(other_income_per_map.get(status, ""))
        selected_option = select.first_selected_option
        print(f"Selected Other Income Per: {selected_option.text}")

    def enter_other_description(self):
        # Find the 'Other Description' input field
        other_description_input = self.driver.find_element(By.ID, "ctl21_ctl26_ctl00_txtOtherDescription")

        # Set the description value
        other_description_value =  self.data["fields"]["Other Income Description"] # Replace with your value as needed
        other_description_input.send_keys(other_description_value)

        # Verify the entered value
        entered_value = other_description_input.get_attribute("value")
        print(f"Entered Other Description: {entered_value}")

    def click_worksheet_link(self):
        # 'Worksheet' link element
        worksheet_link = self.driver.find_element(By.ID, "ctl21_btnWORKSHEET")
        worksheet_link.click()

    def enter_vin(self):
        # Wait for VIN input field
        try:
            vin_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "ctl21_ctl19_ctl00_txtVIN"))
            )
            print("VIN input field is loaded.")
        except:
            print("Timeout: VIN input field was not found.")
        
        vin_input.send_keys(self.data["fields"].get("VIN", ""))
        entered_value = vin_input.get_attribute("value")
        print(f"Entered VIN: {entered_value}")

    def click_vin_lookup_button(self):
        # 'VIN Lookup' button
        vin_lookup_button = self.driver.find_element(By.ID, "ctl21_ctl19_ctl00_btnVINLookup")
        vin_lookup_button.click()

    def wait_for_vin_lookup_popup(self):
        # Wait for the VIN Lookup modal to appear
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "DTC$ModalPopup$TitleID3"))
        )

    def switch_to_vin_lookup_iframe(self):
        # Switch to iframe containing VIN lookup details
        iframe = self.driver.find_element(By.ID, "DTC$ModalPopup$Frame")
        self.driver.switch_to.frame(iframe)

    def select_vehicle_trim_from_table(self):
        # Find the table and rows within the iframe
        try:
            table = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "gvVehicles"))
            )
            print("Table field is loaded.")
        except:
            print("Timeout: Table field was not found.")
        
        rows = table.find_elements(By.TAG_NAME, "tr")

        # Get the vehicle trim from data and match it
        if "Vehicle Trim" in self.data["fields"]:
            target_series = str(self.data["fields"].get("Vehicle Trim", ""))

            # Start iterating from the second row, as the first row is the header
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 5:
                    series_value = cells[5].text.strip()

                    if series_value == target_series.capitalize() or \
                       series_value == target_series.upper() or \
                       series_value == target_series.lower():
                        # Click the radio button in the second column
                        radio_button = cells[1].find_element(By.TAG_NAME, "input")
                        radio_button.click()
                        break
            else:
                # If no match is found, click the first radio button
                first_row = rows[1]
                first_radio_button = first_row.find_elements(By.TAG_NAME, "td")[1].find_element(By.TAG_NAME, "input")
                first_radio_button.click()

    def submit_form(self):
        # Wait for the 'OK' button to be clickable
        wait = WebDriverWait(self.driver, 10)
        btnOK = wait.until(EC.element_to_be_clickable((By.ID, "btnOK")))

        # Click the 'OK' button
        btnOK.click()
        print("Submit successful")

    def switch_out_of_iframe(self):
        # Switch out of the iframe (parent frame)
        self.driver.switch_to.parent_frame()

    def enter_mileage(self):
        # Wait for the mileage field to be present
        wait = WebDriverWait(self.driver, 10)
        txtCurrentKMs_field = wait.until(EC.presence_of_element_located((By.ID, "ctl21_ctl19_ctl00_txtCurrentKMs")))

        # Clear the existing value and enter the mileage data
        txtCurrentKMs_field.clear()
        txtCurrentKMs_field.send_keys(self.data["fields"].get("Odometer", ""))
        print(f"txtCurrentKMs_field: {txtCurrentKMs_field.get_attribute('value')}")

    def select_program(self):
        # Wait for dropdown to be clickable
        program_selection_dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl21_ctl21_ctl00_ddlProgram"))
        )
        time.sleep(1)
        select = Select(program_selection_dropdown)
        options = select.options  # <option> 요소 리스트

        keywords = ["AUTO"]
        program_flag = False

        for option in options:

            program_flag = False # 첫 번째 keyword가 매칭되면 True로 설정
            if program_flag:
                break

            text = option.text.strip() # 옵션 텍스트를 소문자로 변환

            for keyword in keywords:

                if keyword in text:

                    print(f"Matching Option Found: {option.text.strip()}")

                    select.select_by_visible_text(option.text.strip())  # 매칭된 옵션 선택

                    program_flag = True
                    # Check the selected value

                    selected_option = select.first_selected_option

                    print(f"Selected Program: {selected_option.text}")

                    # 한 번 매칭되면 중복 선택 방지

                    return



                else:

                    print(f"No Matching Option Found for '{keyword}'")

    def enter_cash_price(self):
        # Wait for cash price field to be clickable
        cash_price_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl21_ctl22_ctl00_txtCashPrice"))
        )

        # Click and enter value
        cash_price_input.click()
        time.sleep(0.5)
        cash_price_input.send_keys(str(self.data["fields"].get("Cash Price", "")))
        cash_price_input.send_keys(Keys.TAB)
        time.sleep(0.5)

        # Check the entered value
        entered_value = cash_price_input.get_attribute("value")
        print(f"Entered Cash Price: {entered_value}")

    def select_term(self):
        def remove_country_code_and_non_digits(phone):
            return re.sub(r'\D', '', str(phone)[-10:])  # Extract last 10 digits
        # Wait for the 'Term' dropdown field
        term_dropdown = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl21_ctl29_ctl00_CTermDropDown1"))
        )

        # Create Select object
        select_term = Select(term_dropdown)
        term_value = remove_country_code_and_non_digits(self.data["fields"].get("Loan Term", 0))
        term_value = int(term_value) * 12
        select_term.select_by_value(str(term_value))

        # Wait and check the selected term
        time.sleep(1)
        selected_option = select_term.first_selected_option
        print(f"Selected Term: {selected_option.text}")

    def select_amortization(self):
        def remove_country_code_and_non_digits(phone):
            return re.sub(r'\D', '', str(phone)[-10:])  # Extract last 10 digits
        # Find amortization dropdown
        amortization_dropdown = self.driver.find_element(By.ID, "ctl21_ctl29_ctl00_CAmortizationPeriodDropDown1")

        # Create Select object and select value
        select_amortization = Select(amortization_dropdown)
        amortization_value = remove_country_code_and_non_digits(self.data["fields"].get("Loan Term", 0))
        amortization_value = int(amortization_value) * 12
        select_amortization.select_by_value(str(amortization_value))

        # Wait and check the selected amortization
        time.sleep(1)
        selected_option = select_amortization.first_selected_option
        print(f"Selected Amortization: {selected_option.text}")

    def select_payment_frequency(self):
        # Find Payment Frequency dropdown
        payment_frequency_dropdown = self.driver.find_element(By.ID, "ctl21_ctl29_ctl00_CPaymentFrequencyDropDown1")

        # Create Select object
        select_payment_frequency = Select(payment_frequency_dropdown)
        payment_frequency_value = "12"  # Default value for monthly
        if "Payment Frequency" in self.data["fields"]:
            if self.data["fields"]["Payment Frequency"] == "Monthly":
                payment_frequency_value = "12"
            elif self.data["fields"]["Payment Frequency"] == "Bi-Weekly":
                payment_frequency_value = "26"
            elif self.data["fields"]["Payment Frequency"] == "Weekly":
                payment_frequency_value = "52"

        select_payment_frequency.select_by_value(payment_frequency_value)

        # Wait and check the selected value
        selected_option = select_payment_frequency.first_selected_option
        print(f"Selected Payment Frequency: {selected_option.text}")

    def select_interest_rate(self):
        wait = WebDriverWait(self.driver, 20)
        def remove_country_code_and_non_digits(phone):
            return re.sub(r'\D', '', str(phone)[-10:])  # Extract last 10 digits
        
        program_selection_dropdown = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlProgram")

        program_selection = Select(program_selection_dropdown)

        program_selection_value = program_selection.first_selected_option

        term_value = remove_country_code_and_non_digits(self.data["fields"].get("Loan Term", 0))
        cnt = 0
        while True:
            select_element = wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl29_ctl00_CInterestRateDropDown1")))
            options = select_element.find_elements(By.TAG_NAME, 'option')
            
            # 옵션이 없으면 다른 작업을 수행
            if not options:
                print("옵션 값이 없습니다. 다른 작업을 수행합니다.")

                # 'program_selection' 드롭다운 요소 찾기
                program_selection_dropdown = self.driver.find_element(By.ID, "ctl21_ctl20_ctl00_ddlProgram")
                time.sleep(1)

                if program_selection_value == "standard fixed":
                    term_dropdown = self.driver.find_element(By.ID, "ctl21_ctl29_ctl00_CTermDropDown1")

                    # 드롭다운 선택을 위한 Select 객체 생성
                    select_term = Select(term_dropdown)
                    if cnt==0:
                        term_value = int(term_value) * 12 - 12
                    # 값을 선택 (예: '24')
                    else:
                        term_value = int(term_value) - 12
                    select_term.select_by_value(str(term_value))

                    time.sleep(1)
                    selected_option = select_term.first_selected_option
                    print(f"Selected Term: {selected_option.text}")


                    # 'Amortization' 드롭다운 필드 찾기
                    amortization_dropdown = self.driver.find_element(By.ID, "ctl21_ctl29_ctl00_CAmortizationPeriodDropDown1")

                    # 드롭다운 선택을 위한 Select 객체 생성
                    select_amortization = Select(amortization_dropdown)
                    select_amortization.select_by_value(str(term_value))

                    time.sleep(1)

                    selected_option = select_amortization.first_selected_option
                    print(f"Selected Amortization: {selected_option.text}")  # 출력: Selected Amortization: 36
                    cnt += 1
                # Select 객체 생성
                select = Select(program_selection_dropdown)

                # 값 선택 (예: 'AC AT CC ES')
                # 1966420 = Auto special
                # 1966448 = standard fixed rate
                standard_option = "standard fixed"

                program_selection_value = standard_option

                options = select.options  

                for option in options:

                    text = option.text.strip().lower()  # 옵션 텍스트를 소문자로 변환

                    if standard_option in text:

                        print(f"Matching Option Found: {option.text.strip()}")

                        select.select_by_visible_text(option.text.strip())  # 매칭된 옵션 선택

                        break  # 한 번 매칭되면 중복 선택 방지

                    else:

                        print(f"No Matching Option Found for '{standard_option}'")

                # 선택된 값 확인
                selected_option = select.first_selected_option
                print(f"Selected Program: {selected_option.text}")  
                # 여기에 다른 작업을 수행할 수 있는 코드를 추가하세요
            else:
                # 가장 큰 값을 찾기
                max_value = max([float(option.get_attribute('value')) for option in options])
                print(f"가장 큰 옵션 값: {max_value}")

                # 가장 큰 값을 가진 옵션을 선택
                select = Select(select_element)
                select.select_by_value(str(max_value))
                print(f"옵션 {max_value} 선택됨")
                break

    def enter_scene_card(self):
        wait = WebDriverWait(self.driver, 20)
        scene_card_input = wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl20_ctl00_txtSceneCard")))
        scene_card_input.send_keys("5718683723")
        entered_value = scene_card_input.get_attribute("value")
        print(f"Entered Scene Card: {entered_value}")

    def enter_trade_in_details(self):
        if "Trade In" in self.data["fields"]:
            if self.data["fields"].get("Trade In", "") == "Yes":
                self.enter_trade_in_field("Year", "Trade-In Year")
                self.enter_trade_in_field("Make", "Trade-In Make")
                self.enter_trade_in_field("Model", "Trade-In Model")
                self.enter_trade_in_field("VIN", "Trade-In VIN")
                self.enter_trade_in_field("Mileage", "Trade-In Odometer")
                self.enter_trade_in_field("Allowance", "Allowance")
                
                if "Trade-In Lien" in self.data["fields"]:
                    if self.data["fields"].get("Trade-In Lien", "") == "Yes":
                        self.enter_trade_in_field("LienAmount", "Trade-In Lien")
                        self.enter_trade_in_field("BalanceOwedTo", "Trade-In Lender")

    def enter_trade_in_field(self, field_id, field_name):
        # ctl21_ctl23_ctl00_txtYear
        input_field = self.driver.find_element(By.ID, f"ctl21_ctl23_ctl00_txt{field_id}")
        input_field.clear()
        input_field.send_keys(self.data["fields"].get(field_name, ""))
        entered_value = input_field.get_attribute("value")
        print(f"Entered {field_name}: {entered_value}")

    def enter_field(self, field_id, field_name):
        # ctl21_ctl26_ctl00_txtCashDownPayment
        input_field = self.driver.find_element(By.ID, f"ctl21_ctl26_ctl00_txt{field_id}")
        input_field.clear()
        input_field.send_keys(self.data["fields"].get(field_name, ""))
        input_field.send_keys(Keys.TAB)
        entered_value = input_field.get_attribute("value")
        print(f"Entered {field_name}: {entered_value}")

    def enter_cash_down_payment(self):
        # ctl21_ctl25_ctl00_txtCashDownPayment
        if "Cash Down Payment" in self.data["fields"]:
            self.enter_field("CashDownPayment", "Cash Down Payment")

    def fill_text_field(self, field_id, text):
        field = self.driver.find_element(By.ID, field_id)
        field.clear()
        field.send_keys(text)
        entered_value = field.get_attribute("value")
        print(f"Field '{field_id}' entered value: {entered_value}")

    def enter_gap_insurance_amount(self):
        wait = WebDriverWait(self.driver, 20)
        if "Gap Insurance Amount" in self.data["fields"]:
            gap_insurance_input = wait.until(EC.element_to_be_clickable((By.ID, "ctl21_ctl27_ctl00_txtAHInsurance")))
            gap_insurance_input.click()
            gap_insurance_input.send_keys(str(self.data["fields"].get("Gap Insurance Amount", "")))
            entered_value = gap_insurance_input.get_attribute("value")
            gap_insurance_input.send_keys(Keys.TAB)
            print(f"Entered Gap Insurance Amount: {entered_value}")

    def enter_other_taxable_amounts(self):
        fields = self.data.get("fields", {})
        other_taxable_amount = fields.get("Other Taxable Amounts", "")
        theft_protection = fields.get("Theft Protection", "")
        theft_protection_amount = fields.get("Theft Protection Amount", "")

        if theft_protection == "Yes" and theft_protection_amount:
            theft_protection_amount = int(theft_protection_amount)
            if 99 <= theft_protection_amount <= 250:
                other_taxable_amount = int(other_taxable_amount) + theft_protection_amount
                print(f"Theft Protection Amount: {theft_protection_amount}")

        if other_taxable_amount:
            self.fill_text_field("ctl21_ctl26_ctl00_txtOtherTaxable", str(other_taxable_amount))
            description = "ADMIN/OMVIC/THEFT PROTECTION" if theft_protection == "Yes" else fields.get("Other Taxable Description", "ADMIN/OMVIC")
            self.fill_text_field("ctl21_ctl26_ctl00_txtOtherTaxableDesc", description)

    def save_deal(self):
        save_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnSave2"))
        )
        save_button.click()

        ok_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "DTC$ModalPopup$OK"))
        )
        ok_button.click() 

        print("Save button clicked.")

    def run(self, airtable_client, client_data_id):
        try:
            # Read JSON data
            self.read_json_data(client_data_id)

            # Login to DealerTrack
            self.login()

            # Setup Selenium Driver
            self.setup_selenium_driver()

            # Navigate to DealerTrack URL
            default_url = "https://www.dealertrack.ca/default1.aspx"
            self.navigate_to_url(default_url)

            # Transfer cookies to Selenium
            self.transfer_cookies_to_selenium()

            # Navigate to application form URL
            app_form_url = "https://www.dealertrack.ca/DTCanada/Core/application/application_new_type.aspx"
            self.navigate_to_url(app_form_url)

            # Fill and submit the form
            self.fill_and_submit_form()

            # Fill salutation and name fields
            self.fill_salutation_and_name_fields()

            # Fill SIN field
            self.fill_sin_field()

            # Fill phone fields
            self.fill_phone_fields()

            # Fill date of birth field
            self.fill_dob_field()

            # Fill gender field
            self.select_gender()

            # Fill marital status field
            self.select_marital_status()

            # Fill email field
            self.enter_email()

            # Fill language field
            self.select_language()

            # Fill postal code field
            self.enter_postal_code(airtable_client, client_data_id)

            ###### Fill Address Fields ######

            self.select_address_type()

            self.enter_suit_number()

            self.enter_address_number()
            self.enter_street_name()

            self.enter_street_type()

            self.enter_duration_at_current_address()

            # Fill previous postal code field

            self.enter_previous_postal_code(airtable_client, client_data_id)



            ###### Fill Address Fields ######

            self.select_previous_address_type()

            self.enter_previous_suit_number()

            self.enter_previous_address_number()

            self.enter_previous_street_name()

            self.enter_previous_street_type()

            self.enter_duration_at_previous_address()

            #################################

            #################################
            # Fill duration field

            self.select_housing_status()

            self.enter_market_value_and_payments()

            self.select_employment_type()
            self.select_previous_employment_type()

            self.enter_employer_name()
            self.enter_previous_employer_name()

            self.select_employment_status_dropdown()
            self.select_previous_employment_status_dropdown()

            self.enter_occupation()
            self.enter_previous_occupation()

            self.enter_duration_of_employment()
            self.enter_previous_duration_of_employment()

            self.select_address_type_cur_employment()
            self.select_address_type_prev_employment()

            self.enter_suit_number_cur_employer()
            self.enter_suit_number_prev_employer()

            self.enter_street_number_cur_employer()
            self.enter_street_number_prev_employer()

            self.enter_street_name_cur_employer()
            self.enter_street_name_prev_employer()

            self.select_street_type_cur_employment()
            self.select_street_type_prev_employment()

            self.select_direction_cur_employment()
            self.select_direction_prev_employment()

            self.enter_employer_city()
            self.enter_previous_employer_city()

            self.select_employer_province_dropdown()
            self.select_previous_employer_province_dropdown()
            
            self.enter_employer_postal_code()
            self.enter_previous_employer_postal_code()

            self.enter_employer_phone()
            self.enter_previous_employer_phone()

            self.enter_gross_income()

            self.select_gross_income_per_dropdown()

            self.select_other_income_type_dropdown()
            
            self.enter_other_income()
            
            self.select_other_income_per_dropdown()

            self.enter_other_description

            self.click_worksheet_link()

            self.enter_vin()

            self.click_vin_lookup_button()

            self.wait_for_vin_lookup_popup()

            self.switch_to_vin_lookup_iframe()

            self.select_vehicle_trim_from_table()

            self.submit_form()

            self.switch_out_of_iframe()

            self.enter_mileage()

            self.select_program()

            self.enter_cash_price()

            self.select_term()

            self.select_amortization()

            self.select_payment_frequency()
            try:
                self.select_interest_rate()
            except:
                pass
            # NBC에는 없는 옵션
            # self.enter_scene_card()

            self.enter_trade_in_details()

            self.enter_cash_down_payment()

            self.enter_other_taxable_amounts()

            self.enter_gap_insurance_amount()

            # self.save_deal()

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
        finally:
            if self.driver:
                pass
                # self.driver.quit()

if __name__ == "__main__":
    automation = DealerTrackAutomation()
    automation.run()