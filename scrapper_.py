from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from threading import Thread
import requests
import time
import imaplib
import email
from email.header import decode_header
import re

# Replace with your 5sim.net API key
API_KEY = ('eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9'
           '.eyJleHAiOjE3Mzk5NTc5MDAsImlhdCI6MTcwODQyMTkwMCwicmF5IjoiOTllZTIzMDhmNjEzOTU1NzM1NzQ3NzIwZjEwZTJlMDMiLCJzdWIiOjE4NDY5OTF9.xgH1kbRKqYvT4WpquYd8bnGHJdHCHbDfEQucrYp-lBiOtoYe-k3qFzE6LQwwbEa8b2DBUahQ3zHaGDOBwvK4CKNR7yui_3XKs7ThmLXyUcmEISGPSfaU0uD3KXgvhfBhjDTlW5W9Qoug9epUXxcQc_xWvjxCcSllfWplOOS-NM-jf6eSS_CWRtGubKvKZrUkkjyQOGXz6_TirHnpAlxecYGEO9dczjE86QrVVlRMpR-deXaUpdadXhM70uIVWFSzYcrSP9ktCg4BNq5s2Ft1IrjHimzmlwFWGHicf8sdaCufR5AUkzzDRKtcFFtxf4iqHoCOb-KV2Un1rXIRnX8aiw')

# Replace with cPanel API credentials
IMAP_SERVER = 'idsbanao.com'
IMAP_PORT = 993
EMAIL_PASSWORD = 'Admin@000'

otp_previous = ''

TIME_LIMIT=180

# Function to get OTP from phone number using 5sim.net API
def get_otp_from_phone(order_id, otp_previous):
    def get_otp(order_id, otp_previous):
        url = f'https://5sim.net/v1/user/check/{order_id}'
        headers = {'Authorization': f'Bearer {API_KEY}'}
        start_time = time.time()
        try:
            while True:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if 'sms' in data and data['sms']:
                    # Get the latest OTP
                    otp_message = data['sms'][-1]['text']
                    otp = ''.join([c for c in otp_message if c.isdigit()])
                    if otp != otp_previous:
                        otp_previous = otp
                        return otp
                    else:
                        pass

                print("Waiting for OTP...")
                time.sleep(5)

                if time.time() - start_time > TIME_LIMIT:
                    print("Timeout: No recent OTP received within the specified time.")
                    return None
        except Exception as e:
            print(f"Error fetching OTP: {e}")
            return None

    try:
        otp = get_otp(order_id, otp_previous)
        if otp:
            return otp[:6]
        else:
            print('Failed to retrieve OTP from phone.')

    except Exception as e:
        print(f'Error: {e}')


def decode_content(content):
    # Try UTF-8 encoding first
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        # If UTF-8 fails, try ISO-8859-1 (Latin-1) or fallback to default encoding
        try:
            return content.decode('iso-8859-1')
        except UnicodeDecodeError:
            return content.decode('ascii', 'ignore')  # Final fallback with ignoring errors


# Function to get the latest OTP from the email inbox
def get_otp_from_email(email_id):
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(email_id, EMAIL_PASSWORD)

    # Select the inbox folder
    mail.select("inbox")

    # Search for all emails
    result, data = mail.search(None, 'ALL')

    if result != "OK":
        print("No emails found!")
        return None

    # Get the list of email IDs and fetch the latest email
    email_ids = data[0].split()
    latest_email_id = email_ids[-1]

    # Fetch the email by ID
    result, message_data = mail.fetch(latest_email_id, '(RFC822)')

    if result != "OK":
        print("Failed to fetch the email!")
        return None

    # Parse the email content
    raw_email = message_data[0][1]
    msg = email.message_from_bytes(raw_email)

    # Decode the email subject
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else 'utf-8')

    # Initialize the email body content
    body = ""

    # If the email message is multipart, iterate over the parts
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Get the body of the email
            if "attachment" not in content_disposition:
                if content_type == "text/plain" or content_type == "text/html":
                    # Try to decode the email body safely using our custom decode function
                    body = decode_content(part.get_payload(decode=True))
                    break
    else:
        # If the email is not multipart, extract the body
        body = decode_content(msg.get_payload(decode=True))

    # Use regex to find the OTP (assuming it's a 6-digit number)
    otp_match = re.search(r'\b\d{6}\b', body)
    otp = otp_match.group(0) if otp_match else None

    # Logout and close the connection
    mail.logout()

    # Return the extracted OTP
    return otp


def func_(mobile_number, email_id, order_id, counter):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get('https://www.flipkart.com/account/login?signup=true&ret=/')
    number_place = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div/div[2]/div/form/div[1]/input')
    number_place.send_keys(mobile_number)
    sleep(2)
    driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div/div[2]/div/form/div[3]/button').click()
    sleep(10)
    try:
        for i in range(2):
            driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div/div[2]/div/form/div[3]/button').click()
            sleep(2)
    except:
        pass
    sleep(60)
    otp = get_otp_from_phone(order_id, otp_previous)
    print("Mobile Otp:",otp)
    try:
        driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div/div[2]/div/form/div[3]/input').send_keys(otp)
        sleep(3)
        driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div/div[2]/div/form/div[4]/button').click()
    except:
        try:
            for o_, o in enumerate(otp):
                driver.find_element(By.XPATH,
                                    f'//*[@id="container"]/div/div[3]/div/div[2]/div/div/form/div/div[{o_ + 1}]/input').send_keys(
                    o)
        except:
            pass
    sleep(30)
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div/div[1]/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/header/div[2]/div[2]/div/div/div/div/a/span').click()
    sleep(10)
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div/div[1]/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/header/div[2]/div[2]/div/div/div/ul/a[1]/li/div').click()
    sleep(5)
    driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div/div[2]/div/div/div[1]/div[2]/div[1]/div/div/a').click()
    sleep(5)
    email_box = driver.find_element(By.XPATH,
                                    '/html/body/div/div/div[3]/div/div[2]/div/div/div[1]/div[2]/div[1]/div/form/div/div/div/input')
    email_box.clear()
    email_box.send_keys(email_id)
    sleep(5)
    driver.find_element(By.XPATH,
                        '/html/body/div/div/div[3]/div/div[2]/div/div/div[1]/div[2]/div[1]/div/form/div/button').click()
    sleep(40)
    otp_1 = driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div/form/div[1]/div/input')
    otp_2 = driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div/form/div[2]/div/input')
    try:
        otp__ = get_otp_from_email(email_id)
    except:
        sleep(20)
        otp__ = get_otp_from_email(email_id)
    otp2__ = get_otp_from_phone(order_id, otp_previous)
    otp_1.send_keys(otp__)
    sleep(2)
    otp_2.send_keys(otp2__)
    sleep(2)
    driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div/form/button').click()
    sleep(10)
    counter += 1


def func_main(threads, start_from, ends_at, list_):
    return_list=[]
    counter = 0
    number_of_threads = int(threads)
    start = start_from
    for th in range((ends_at - start_from) // number_of_threads):
        threads = []
        for res in range(start, start + number_of_threads):
            try:
                t = Thread(target=func_,
                           args=(list_[res]['mobile_number'], list_[res]['email_id'], list_[res]['order_id'], counter))
                t.start()
                threads.append(t)
                return_list.append(list_[res]['id'])
            except Exception as e:
                print(e, '!!!!!')
                continue
        for t in threads:
            t.join()
        start += number_of_threads
    return return_list
