import email
import imaplib
import smtplib
from datetime import datetime
from email.message import EmailMessage
from time import sleep

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import info as info


class LinkForUpdates:
    item_link = ''

    def __init__(self, item_link):
        self.item_link = item_link


def emails(subject, body):
    msg = EmailMessage()
    msg.set_content(body + '\n' * 2 + LinkForUpdates.item_link)

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
    while True:

        value_code = fetch_email()

        if value_code is None:
            sleep(1)

        else:
            email_code_found = value_code
            break

    return email_code_found


def events_log(file, event):
    current_time = datetime.now().strftime('time %I:%M %p on %m/%d/%y: ')

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

        profile_name_check = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'account'
                                                                                                            '-button '
                                                                                             ))).text

        if info.first_name in profile_name_check:
            return True

        else:
            raise Exception('Sign In Script Error')

    except Exception as Login_ScriptError:

        emails('Auto-Cart Error', 'account_login Script Error')

        events_log('errors.txt', str(Login_ScriptError))

        return False


def set_store_location(zip_code):
    try:
        store_name = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'store-display-name'))).text

        if store_name == info.target_store_name:
            return True

        else:

            try:
                # time sensitive input fields

                find_store = WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.CLASS_NAME, 'zip-code-input')))
                find_store.click()
                sleep(3)
                find_store.send_keys(zip_code)
                sleep(3)
                find_store.send_keys(Keys.ENTER)
                sleep(3)
                select_store = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH,
                                                                                               '/html/body/div['
                                                                                               '2]/main/div[2]/div/div['
                                                                                               '1]/div/div/ul/li['
                                                                                               '1]/div[ '
                                                                                               '1]/div/div['
                                                                                               '2]/div/div/div/div['
                                                                                               '3]/button')))
                select_store.click()
                sleep(3)

                return True

            except:

                raise Exception('Location Not Set')

    except Exception as location_error:

        emails('Auto-Cart Error', 'set_store_location Script Error')
        events_log('errors.txt', location_error)

        return False


def cart_wait():
    try:

        unknown_link = driver.current_url
        while 'signin?token' not in unknown_link:
            add_to_cart = WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
            add_to_cart.click()

            try:
                WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "heading-3")))
                
                sleep(10)
                
                inventory_status = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "heading-3"))).text

                if any(word in inventory_status.lower() for word in info.key_words):

                    emails('Auto-Cart Update', inventory_status)

                    return False


            except:

                unknown_link = driver.current_url
                if unknown_link == info.BestBuy_Link_Cart:
                    emails('Auto-Cart Success',
                           'Pre Verify Carting (Testing Result)')
                    return False

                else:
                    pass

        return True

    except Exception as AutoAdd_ScriptError:

        emails('Auto-Cart Error', 'cart_wait Script Error')
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
    emails('Auto-Cart Started', 'Inventory Found.')
    events_log('stock.txt', 'In Stock')

    if cart_wait() is True:

        if verify_account() is True:

            emails('Auto-Cart Update', 'Email Verification Passed.')

            try:
                # wait for stock pop-up status box (15 Seconds)

                WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.CLASS_NAME, "heading-3")))

                # read pop-up box status messages, loop until condition is met.

                message_value = True
                while message_value is True:

                    try:
                        inventory_status = WebDriverWait(driver, 10).until(
                            ec.presence_of_element_located((By.CLASS_NAME, "heading-3"))).text

                        # if message says 'Searching' - continue

                        if inventory_status == 'Searching Inventory':
                            pass

                        # if message contains error key word - break loop

                        elif any(word in inventory_status.lower() for word in info.key_words):

                            emails('Auto-Cart Error', inventory_status)

                            message_value = False

                        sleep(3)

                    except:

                        # if no pop-up box is displayed, check URL for status

                        unknown_link = driver.current_url

                        # if URL is cart address, item is now in the cart

                        if unknown_link == info.BestBuy_Link_Cart:
                            emails('Auto-Cart Success',
                                   'Check Mobile App to finish your purchase.')

                            message_value = False

            except:

                # if no pop-up box is displayed, check URL for status

                unknown_link = driver.current_url

                if unknown_link == info.BestBuy_Link_Cart:
                    emails('Auto-Cart Success',
                           'Check Mobile App to finish your purchase.')


def main():
    driver.get(info.sign_in_link_bestbuy)

    if account_login(info.account_email_bestbuy, info.account_pass_bestbuy) is True:

        driver.get(info.location_link_bestbuy)

        if set_store_location(info.target_store_zip) is True:

            events_log('log.txt', 'Bot Successfully Started')

            url_list = info.item_links_bestbuy

            while len(url_list) != 0:

                for i in url_list:

                    LinkForUpdates.item_link = i
                    driver.get(i)

                    try:
                        add_to_cart = WebDriverWait(driver, 10).until(
                            ec.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
                        add_to_cart.click()

                        pop_up_box = WebDriverWait(driver, 10).until(
                            ec.presence_of_element_located((By.CLASS_NAME, "c-modal-close-icon")))
                        pop_up_box.click()

                    except:
                        continue

                    auto_cart_main()
                    url_list.remove(i)

    driver.close()
    sleep(1)
    driver.quit()


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = uc.Chrome(options=chrome_options)

    main()
