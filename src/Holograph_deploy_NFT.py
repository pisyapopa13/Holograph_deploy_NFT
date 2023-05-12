from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.expected_conditions import invisibility_of_element_located
import time
import random
import threading
from queue import Queue
from selenium.common.exceptions import NoSuchElementException



max_simultaneous_profiles = 3
chrome_driver_path = Service("C:\\you\\personal\\path\\to\\chromedriver-win-x64.exe")
metamask_url = f"chrome-extension://cfkgdnlcieooajdnoehjhgbmpbiacopjflbjpnkm/home.html#"


with open("config\\profile_ids.txt", "r") as file:
    profile_ids = [line.strip() for line in file.readlines()]
with open("config\\passwords.txt", "r") as file:
    passwords = [line.strip() for line in file.readlines()]
start_idx = int(input("Enter the starting index of the profile range: "))
end_idx = int(input("Enter the ending index of the profile range: "))
holograph_url = f'https://app.holograph.xyz'
def input_text_if_exists(driver, locator, text, by=By.XPATH, timeout=20):
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            element.send_keys(text)
            return True
        except TimeoutException:
            return False
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(3)
    return False
def click_if_exists(driver, locator):
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, locator))
            )
            WebDriverWait(driver, 10).until(
                invisibility_of_element_located((By.CSS_SELECTOR, ".loading-overlay"))
            )
            element.click()
            return True
        except TimeoutException:
            return False
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(3)
    return False
def worker():
    while True:
        idx, profile_id = task_queue.get()
        if profile_id is None:
            break
        process_profile(idx, profile_id)
        task_queue.task_done()
def perform_transaction(driver, network_name, selector, initial_window_handle):
    driver.get(metamask_url)
    click_if_exists(driver, '/html/body/div[1]/div/div[1]/div/div[2]/div/div')
    time.sleep(random.uniform(1.2, 1.3))
    click_if_exists(driver, f"//*[contains(text(), '{network_name}')]")
    driver.get(holograph_url)
    click_if_exists(driver, '/html/body/div/main/header/nav/div/div[3]/div/div[2]/div[1]/div')
    time.sleep(random.uniform(0.7, 1.3))
    click_if_exists(driver, '/html/body/div/main/header/nav/div/div[3]/div/div[2]/div[2]/div/button')
    time.sleep(random.uniform(0.7, 1.3))
    click_if_exists(driver, '/html/body/div/main/main/section/div/div[3]/button[2]')
    time.sleep(random.uniform(0.7, 1.3))
    button = driver.find_element(By.CSS_SELECTOR, selector)
    button.click()
    time.sleep(random.uniform(0.7, 1.3))
    click_if_exists(driver, '/html/body/div/main/main/div/button')
    time.sleep(5)
    sign_transaction(driver)
    time.sleep(13)
    confirm_transaction(driver)
    driver.switch_to.window(initial_window_handle)
    try:
        element = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/aside[1]/div/div/div/button[2]')))
    except TimeoutException:
        print("Timed out waiting for element to appear.")
def element_exists(driver, xpath):
    time.sleep(random.uniform(1.2, 1.7))
    try:
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        return True
    except NoSuchElementException:
        return False
def confirm_transaction(driver):
    metamask_window_handle = None

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if 'MetaMask Notification' in driver.title:
            metamask_window_handle = handle
            break

    if metamask_window_handle:
        find_confirm_button_js = '''
        function findConfirmButton() {
          return document.querySelector('[data-testid="page-container-footer-next"]');
        }
        return findConfirmButton();
        '''
        confirm_button = driver.execute_script(find_confirm_button_js)

        if confirm_button:
            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
            for i in range(5):
                if metamask_window_handle not in driver.window_handles:
                    print("MetaMask Notification window closed as expected")
                    return
                driver.execute_script("arguments[0].click();", confirm_button)
                print(f"Click attempt {i + 1}")
                time.sleep(3)
            print("Transaction is confirmed")
        else:
            print("Confirm button not found")
    else:
        print("MetaMask Notification window not found")
    driver.switch_to.window(driver.window_handles[0])
def sign_transaction(driver):
    metamask_window_handle = None
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if 'MetaMask Notification' in driver.title:
            metamask_window_handle = handle
            break
    if metamask_window_handle:
        sign_xpath = '/html/body/div[1]/div/div[2]/div/div[3]/button[2]'
        click_if_exists(driver, sign_xpath)
        print("Transaction sign")
    else:
        print("No masage to sign")
    driver.switch_to.window(driver.window_handles[0])
def confirm_connection(driver):
    metamask_window_handle = None
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if 'MetaMask Notification' in driver.title:
            metamask_window_handle = handle
            break
    if metamask_window_handle:
        Confirm_conection_xpath = '/html/body/div[1]/div/div[2]/div/div[3]/div[2]/button[2]'
        Confirm_conection2_xpath = '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]'
        Confirm_conection3_xpath = '/html/body/div[1]/div/div[2]/div/div[3]/button[2]'

        button_clicked = click_if_exists(driver, Confirm_conection_xpath)
        if button_clicked:
            click_if_exists(driver, Confirm_conection2_xpath)
            click_if_exists(driver, Confirm_conection3_xpath)
        else:
            click_if_exists(driver, Confirm_conection3_xpath)

        print("Metamask is connected")
    else:
        print("MetaMask already connected")
    driver.switch_to.window(driver.window_handles[0])
def process_profile(idx, profile_id):

    print(f"Opening ID {idx}: {profile_id}")
    req_url = f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1'
    response = requests.get(req_url)
    response_json = response.json()
    print(response_json)
    port = str(response_json['automation']['port'])
    options = webdriver.ChromeOptions()
    options.debugger_address = f'127.0.0.1:{port}'
    driver = webdriver.Chrome(service=chrome_driver_path, options=options)
    initial_window_handle = driver.current_window_handle

    driver.get(metamask_url)
    try:
        for tab in driver.window_handles:
            if tab != initial_window_handle:
                driver.switch_to.window(tab)
                driver.close()
        driver.switch_to.window(initial_window_handle)
        password_input = '//*[@id="password"]'
        input_text_if_exists(driver, password_input, passwords[idx - 1])
        click_if_exists(driver, '//*[@id="app-content"]/div/div[3]/div/div/button')
        time.sleep(random.uniform(0.7, 1.3))
        perform_transaction(driver, 'Polygon Mainnet', '#Polygon', initial_window_handle)
        perform_transaction(driver, 'Avalanche Network C-Chain', '#Avalanche', initial_window_handle)
        perform_transaction(driver, 'BNB Smart Chain (previously Binance Smart Chain Mainnet)', '#BNB\\ Chain',
                            initial_window_handle)
        mint_options = [
            ('Polygon Mainnet',),
            ('Avalanche Network C-Chain',),
            ('BNB Smart Chain (previously Binance Smart Chain Mainnet)',)
        ]
        chosen_option = random.choice(mint_options)
        driver.get(metamask_url)
        click_if_exists(driver, '/html/body/div[1]/div/div[1]/div/div[2]/div/div')
        time.sleep(random.uniform(1.2, 1.3))
        click_if_exists(driver, f"//*[contains(text(), '{chosen_option}')]")
        driver.get(holograph_url)
        click_if_exists(driver, '/html/body/div/main/header/nav/div/div[3]/div/div[2]/div[1]/div')
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/main/header/nav/div/div[3]/div/div[2]/div[2]/div/button')
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/main/main/section/div[1]/div[3]/button[1]')
        time.sleep(random.uniform(0.7, 1.3))
        click_if_exists(driver, '/html/body/div/main/main/section/div/div[2]/button')
        time.sleep(random.uniform(3.7, 4.3))
        click_if_exists(driver, '/html/body/div/main/main/section/div/div[2]/button')
        time.sleep(random.uniform(3.7, 4.3))
        confirm_transaction(driver)
        try:
            element = WebDriverWait(driver, 300).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div/main/div[3]/div/div/button[1]')))
        except TimeoutException:
            print("Timed out waiting for element to appear.")
        driver.close()
        print(f"Done for profile №{idx}!")
    except Exception as e:
        print(f"Fail for profile №{idx}...{e}!")
        driver.quit()

task_queue = Queue(max_simultaneous_profiles)
threads = []

for _ in range(max_simultaneous_profiles):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for idx, profile_id in zip(range(start_idx, end_idx + 1), profile_ids[start_idx - 1:end_idx]):
    task_queue.put((idx, profile_id))
    time.sleep(20)

task_queue.join()

for _ in range(max_simultaneous_profiles):
    task_queue.put((None, None))

for t in threads:
    t.join()
#PERFORM BY @BROKEBOI_CAPITAL & GPT4