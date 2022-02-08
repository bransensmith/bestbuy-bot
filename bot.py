# import sys
import email
import imaplib
import smtplib
from datetime import datetime
from email.message import EmailMessage
from time import sleep

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import core_info
import user_info

# full path to files
errors = 'errors.txt'
stock = 'stock.txt'
log = 'log.txt'
carted = 'carted.txt'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
driver = uc.Chrome(options=chrome_options)


# updates are beyond this point
class ProductNow:
    item_name = ''
    item_image_link = ''


def email_bugs(subject, body):
    msg = EmailMessage()
    msg['subject'] = subject

    msg.set_content = body
    msg['to'] = core_info.debug_email
    user = core_info.outgoing_gmail_username
    msg['from'] = user

    password = core_info.outgoing_gmail_app_pass
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()


def email_form(subject, main_alert, more_info):
    personal_info = (user_info.first_name + ' | ' + user_info.target_store_name + ', ' + user_info.target_store_zip)

    image_link = ProductNow.item_image_link
    item_name = ProductNow.item_name

    msg = EmailMessage()
    msg['subject'] = '[ALERT] ' + subject

    msg.set_content(f"""<!DOCTYPE html>
        <html>
            <body>
                 <div style="border-radius: 10px; background-color:#eee;padding:5px">

                        <h2 style="text-align:center; color:red">{main_alert}</h2>
                    </div>

                <table width="100%" border="0" cellspacing="0" cellpadding="20">
                    <tr>
                        <td align="center">

                            <img style="max-height:200px; max-width:200px;" src="{image_link}">
                            <p style="font-size:12px">{item_name}</p>

                        </td>
                    </tr>
                </table>
                    <div style="text-align:center">

                        <h2 style="background-color: #FFFF00;">*** Status ***</h2>

                        <li>{more_info}</li>

                    </div>

                    <div style="text-align:center; font-size:15px; padding-top:20px">

                        <p style="color:grey;">{personal_info}</p>

                    </div
            </body>
        """, subtype='html')

    msg['to'] = user_info.personal_email
    user = core_info.outgoing_gmail_username
    msg['from'] = user
    password = core_info.outgoing_gmail_app_pass

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()


def fetch_email():
    imap = imaplib.IMAP4_SSL(core_info.imap_url)
    imap.login(user_info.personal_gmail_username, user_info.personal_gmail_app_pass)
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
        file_write.write(current_time + '[' + user_info.first_name + '] ' + event + '\n')

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

        if user_info.first_name in profile_name_check:
            return True

        else:
            raise Exception('Sign In Error')

    except Exception as Login_ScriptError:

        email_bugs('Auto-Cart', 'User: ' + user_info.first_name + '\n' + ' Exception: ' + '[Sign In Error]')

        events_log(errors, 'account_login Script Error: ' + str(Login_ScriptError))

        return False


def set_store_location(zip_code):
    try:
        store_name = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'store-display-name'))).text

        if store_name == user_info.target_store_name:
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

        email_bugs('Auto-Cart', 'User: ' + user_info.first_name + '\n' + ' Exception: ' + '[Store Location Error]')

        events_log(errors, 'set_store_location Script Error: ' + str(location_error))

        return False


def cart_wait():
    try:

        unknown_link = driver.current_url
        while 'signin?token' not in unknown_link:
            add_to_cart = WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
            add_to_cart.click()

            try:
                WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CLASS_NAME, "heading-3")))

                sleep(10)

                inventory_status = WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "heading-3"))).text

                if any(word in inventory_status.lower() for word in core_info.key_words_stop):

                    email_form('Auto-Cart', inventory_status, 'Your selected store has no available inventory.')
                    return False

                elif any(word in inventory_status.lower() for word in core_info.key_words_continue):

                    continue

            except TimeoutException:

                unknown_link = driver.current_url
                if unknown_link == core_info.BestBuy_Link_Cart:
                    email_form('Auto-Cart', 'Cart Successes', 'Check your BestBuy Mobile App to finish your purchase.')
                    events_log(carted, user_info.first_name + ' - Successfully carted: ' + ProductNow.item_name)
                    return False

                else:
                    continue

        return True

    except Exception as AutoAdd_ScriptError:

        email_bugs('Auto-Cart', 'User: ' + user_info.first_name + '\n' + ' Exception: ' + '[Cart Wait Error]')

        events_log(errors, 'Carting Script Error: ' + str(AutoAdd_ScriptError))
        return False


def verify_account():
    try:
        password_verify = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'fld-p1')))
        password_verify.click()
        password_verify.send_keys(user_info.account_pass_bestbuy)

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
        email_bugs('Auto-Cart',
                   'User: ' + user_info.first_name + '\n' + ' Exception: ' + '[Two-Factor authentication failure]')

        events_log(errors, 'Two-Factor authentication failure: ' + str(AutoVerify_ScriptError))

        return False


def auto_cart_main():
    email_form('Auto-Cart', 'Inventory Found', 'Starting Auto-Cart. Please watch for more updates.')

    events_log(stock, 'In Stock ' + ProductNow.item_name)

    if cart_wait() is True:

        if verify_account() is True:

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
                        if any(word in inventory_status.lower() for word in core_info.key_words_continue):
                            pass

                        # if message contains error key word - break loop
                        elif any(word in inventory_status.lower() for word in core_info.key_words_stop):

                            email_form('Auto-Cart', inventory_status,
                                       'Your selected store has no available inventory.')

                            message_value = False

                        sleep(3)

                    except TimeoutException:

                        # if no pop-up box is displayed, check URL for status

                        unknown_link = driver.current_url

                        # if URL is cart address, item is now in the cart

                        if unknown_link == core_info.BestBuy_Link_Cart:
                            email_form('Auto-Cart', 'Cart Successes',
                                       'Check your BestBuy Mobile App to finish your purchase.')

                            events_log(carted, user_info.first_name + ' - Successfully carted: ' + ProductNow.item_name)

                            message_value = False

            except TimeoutException:

                # if no pop-up box is displayed, check URL for status

                unknown_link = driver.current_url

                if unknown_link == core_info.BestBuy_Link_Cart:
                    email_form('Auto-Cart', 'Cart Successes', 'Check your BestBuy Mobile App to finish your purchase.')

                events_log(carted, user_info.first_name + ' - Successfully carted: ' + ProductNow.item_name)


def main():
    driver.get(core_info.sign_in_link_bestbuy)

    if account_login(user_info.account_email_bestbuy, user_info.account_pass_bestbuy) is True:

        driver.get(core_info.location_link_bestbuy)

        if set_store_location(user_info.target_store_zip) is True:

            events_log(log, 'Bot Successfully Started')

            url_list = user_info.item_links_bestbuy

            while len(url_list) != 0:

                for i in url_list:

                    driver.get(i)

                    try:
                        add_to_cart = WebDriverWait(driver, 5).until(
                            ec.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
                        add_to_cart.click()

                        pop_up_box = WebDriverWait(driver, 10).until(
                            ec.presence_of_element_located((By.CLASS_NAME, "c-modal-close-icon")))
                        pop_up_box.click()

                        product_name = WebDriverWait(driver, 10).until(
                            ec.presence_of_element_located((By.CLASS_NAME, "heading-5"))).text
                        # update class name for emails
                        ProductNow.item_name = product_name

                        product_image = WebDriverWait(driver, 10).until(
                            ec.presence_of_element_located((By.CLASS_NAME, "primary-image"))).get_attribute("src")

                        ProductNow.item_image_link = product_image

                    except TimeoutException:

                        continue

                    auto_cart_main()
                    url_list.remove(i)

    driver.close()
    sleep(1)
    driver.quit()
