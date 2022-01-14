import email
import imaplib
import smtplib
from datetime import datetime
from email.message import EmailMessage
from time import sleep
import info as info

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def emails(subject, body):
    msg = EmailMessage()
    msg.set_content(body)

    msg['subject'] = ('[Alert] ' + subject)
    msg['to'] = info.personal_email

    user = info.gmail_username
    msg['from'] = user
    password = info.gmail_app_pass

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()


def fetch_email():
    imap = imaplib.IMAP4_SSL(info.imap_url)
    imap.login(info.gmail_username, info.gmail_app_pass)
    imap.select('INBOX')

    status, data = imap.search(None, '(FROM "BestBuyInfo@emailinfo.bestbuy.com" SUBJECT "purchase" UNSEEN)')

    mail_ids = []

    for block in data:
        mail_ids += block.split()

        if mail_ids:
            # Get most recent Email from List filter
            mail_ids = mail_ids[-1]

            status, data = imap.fetch(mail_ids, '(RFC822)')

            for response_part in data:

                if isinstance(response_part, tuple):

                    message = email.message_from_bytes(response_part[1])

                    if message.is_multipart():
                        mail_content = ''

                        for part in message.get_payload():

                            if part.get_content_type() == 'text/plain':
                                mail_content += part.get_payload()
                    else:

                        mail_content = message.get_payload()

                    soup = BeautifulSoup(mail_content, 'html.parser')
                    soup.prettify()
                    main_text = soup.select('[style*="font-size:18px; color: #1d252c; font-weight:bold;"]')

                    for item in main_text:
                        verify_code = item.getText()

                        return verify_code
        else:

            return None

    imap.close()
    imap.logout()


def fetch_email_key():
    email_code_found = []

    check_code = True
    while check_code is True:

        value_code = fetch_email()

        if value_code is None:
            sleep(1)

        else:
            email_code_found = [value_code]
            check_code = False

    return email_code_found[-1]


def events_log(file, event):
    current_time = datetime.now().strftime('Time %I:%M %p on %m/%d/%y: ')

    opened_file = open(file, 'a')

    with opened_file as file_write:
        file_write.write(current_time + event + '\n')

    opened_file.close()


def account_login(account_email, account_password):
    try:

        bestbuy_email = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'fld-e')))
        bestbuy_email.click()
        bestbuy_email.send_keys(account_email)

        bestbuy_password = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'fld-p1')))
        bestbuy_password.click()
        bestbuy_password.send_keys(account_password)

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'c-button'))).click()

        # verify Name on Page

        profile_name_check = WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.CLASS_NAME, 'account'
                                                                                                            '-button '
                                                                                             ))).text

        if info.first_name in profile_name_check:
            return True

        else:
            raise Exception('Sign In Script Error')

    except Exception as Login_ScriptError:

        emails('Auto-Cart Error', 'Sign In Error')

        events_log('errors.txt', str(Login_ScriptError))

        return False


def set_store_location(zip_code):
    # Allow page to load
    sleep(10)

    store_name = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CLASS_NAME, 'store-display-name'))).text

    if store_name == info.target_store_name:
        return True

    else:

        try:
            find_store = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CLASS_NAME, 'zip-code-input')))
            find_store.click()
            sleep(2)
            find_store.send_keys(zip_code)
            sleep(1)
            find_store.send_keys(Keys.ENTER)
            sleep(2)
            select_store = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH,
                                                                                           '/html/body/div['
                                                                                           '2]/main/div[2]/div/div['
                                                                                           '1]/div/div/ul/li[1]/div['
                                                                                           '1]/div/div['
                                                                                           '2]/div/div/div/div['
                                                                                           '3]/button')))
            select_store.click()
            sleep(2)

            return True

        except Exception as Location_ScriptError:

            emails('Auto-Cart Error', 'Location Not Set')
            events_log('errors.txt', 'Location Set Script Error' + '\n' + str(Location_ScriptError))

            return False


def cart_wait():
    try:

        add_to_cart = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
        add_to_cart.click()

        pop_up_box = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "c-modal-close-icon")))
        pop_up_box.click()

        verify_check_account = False

        while not verify_check_account:

            try:
                add_to_cart = WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
                add_to_cart.click()
                WebDriverWait(driver, 8).until(ec.presence_of_element_located((By.ID, 'fld-p1')))

                verify_check_account = True

            finally:
                continue

        return True

    except Exception as AutoAdd_ScriptError:

        emails('Auto-Cart Error', 'Carting Script Error')

        events_log('errors.txt', 'Carting Script Error' + '\n' + str(AutoAdd_ScriptError))

        return False


def verify_account():
    try:
        password_verify = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'fld-p1')))
        password_verify.click()
        password_verify.send_keys(info.account_pass_bestbuy)

        continue_button = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'c-button')))
        continue_button.click()

        email_verify = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'email-radio')))
        email_verify.click()

        continue_button = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'c-button')))
        continue_button.click()

        email_code = fetch_email_key()

        email_verify_code = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'verificationCode')))
        email_verify_code.click()
        email_verify_code.send_keys(email_code)

        continue_button = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'c-button')))
        continue_button.click()

        return True

    except Exception as AutoVerify_ScriptError:

        emails('Auto-Cart Error', '2FA Verify Script Error')

        events_log('errors.txt', '2FA Verify Script Error' + '\n' + str(AutoVerify_ScriptError))

        return False


def auto_cart_main():

    try:
        stock_error = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "inactive-product-message"))).text

        emails('Auto-Cart Error', 'Inventory Type Issue: ' + stock_error)
        events_log('errors.txt', 'Inventory Type Issue' + '\n' + stock_error)

    except:

        events_log('log.txt', 'Bot Successfully Started')

        try:

            find_button_cart = False
            while not find_button_cart:

                try:
                    WebDriverWait(driver, 7).until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
                    find_button_cart = True

                finally:
                    driver.refresh()
                    continue

            emails('Auto-Cart Started', 'Inventory Found.')

            events_log('stock.txt', 'In Stock')

            if cart_wait() is True:

                if verify_account() is True:

                    emails('Auto-Cart Update', 'Email Verification Passed.')

                    try:
                        WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.CLASS_NAME, "heading-3")))

                        checking_alert = False

                        while not checking_alert:

                            try:

                                inventory_status = WebDriverWait(driver, 30).until(
                                    ec.presence_of_element_located((By.CLASS_NAME, "heading-3"))).text

                                if inventory_status == 'Searching Inventory':
                                    pass

                                elif any(word in inventory_status.lower() for word in info.key_words):

                                    emails('Auto-Cart Error', inventory_status)

                                    checking_alert = True

                                sleep(3)

                            except:

                                unknown_link = driver.current_url

                                if unknown_link == info.BestBuy_Link_Cart:
                                    emails('Auto-Cart Success',
                                           'Check Mobile App to finish your purchase.')

                                    checking_alert = True

                                else:

                                    emails('Auto-Cart Error',
                                           'Unknown Final Conditions - Check Mobile App for possible Inventory Error. '
                                           '[2]')

                                    checking_alert = True

                    except Exception as unknown_final:

                        emails('Auto-Cart Error',
                               'Unknown Final Conditions - Check Mobile App for possible Inventory Error. [1]')

                        events_log('errors.txt', 'Script Error' + '\n' + str(unknown_final))

        except Exception as Script_Error:

            emails('Auto-Cart Error', 'auto_cart_main Script Error')

            events_log('errors.txt', 'auto_cart_main Script Error' + '\n' + str(Script_Error))


def main():
    driver.get(info.sign_in_link_bestbuy)

    if account_login(info.account_email_bestbuy, info.account_pass_bestbuy) is True:

        driver.get(info.location_link_bestbuy)

        if set_store_location(info.target_store_zip) is True:
            driver.get(info.item_link_bestbuy)
            auto_cart_main()

    driver.close()
    sleep(1)
    driver.quit()


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = uc.Chrome(options=chrome_options)

    main()
