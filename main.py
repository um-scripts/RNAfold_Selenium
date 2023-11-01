from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec
import requests
import os
from PIL import Image


def fetch_and_store(browser, input_data):
    def white_background(filepath):
        image = Image.open(filepath).convert("RGBA")
        new_image = Image.new("RGBA", image.size, "WHITE")
        new_image.paste(image, (0, 0), image)
        new_image.convert('RGB').save(filepath, "PNG")

    for input_seq, output_path in input_data:
        if os.path.exists(output_path):
            continue
        else:
            os.mkdir(output_path)

        browser.get("http://rna.tbi.univie.ac.at/cgi-bin/RNAWebSuite/RNAfold.cgi")
        form = browser.find_element(By.ID, "contentmain").find_element(By.TAG_NAME, "form")
        form.find_element(By.ID, "SCREEN").send_keys(input_seq)
        form.find_element(By.NAME, "proceed").click()

        WebDriverWait(browser, 1000000).until(ec.all_of(
            ec.text_to_be_present_in_element((By.ID, 'contentmain'), 'Results for minimum free energy prediction'),
            ec.text_to_be_present_in_element((By.ID, 'contentmain'), 'Results for thermodynamic ensemble prediction'),
            ec.text_to_be_present_in_element((By.ID, 'contentmain'), 'Graphical output')
        ))

        mfe_vienna_link = browser.find_elements(By.LINK_TEXT, 'Vienna Format')[0].get_attribute('href')
        mfe_ct_link = browser.find_elements(By.LINK_TEXT, 'Ct Format')[0].get_attribute('href')
        with open(os.path.join(output_path, 'mfe_vienna_format.txt'), 'w') as f:
            f.write(requests.get(mfe_vienna_link).text)
            f.close()
        with open(os.path.join(output_path, 'mfe_ct_format.txt'), 'w') as f:
            f.write(requests.get(mfe_ct_link).text)
            f.close()

        browser.find_elements(By.LINK_TEXT, 'IMAGE CONVERTER')[1].click()
        img1 = browser.find_element(By.TAG_NAME, "form").find_element(By.TAG_NAME, "a").get_attribute("href")
        browser.back()
        browser.find_elements(By.LINK_TEXT, 'IMAGE CONVERTER')[3].click()
        img2 = browser.find_element(By.TAG_NAME, "form").find_element(By.TAG_NAME, "a").get_attribute("href")
        browser.back()

        img1_path = os.path.join(output_path, 'MFE plain structure drawing.png')
        with open(img1_path, 'wb') as f:
            f.write(requests.get(img1).content)
            f.close()
        white_background(img1_path)

        img2_path = os.path.join(output_path, 'MFE structure drawing encoding base-pair probabilities.png')
        with open(img2_path, 'wb') as f:
            f.write(requests.get(img2).content)
            f.close()
        white_background(img2_path)


result_path = '65nonstrandExperimentallyV_curated'
if not os.path.exists(result_path):
    os.mkdir(result_path)
file = open('66NonStrandExpV.fa', 'r')
lines = file.readlines()
file.close()
data = []
for i in range(0, len(lines), 2):
    ref = lines[i].strip('\n')
    seq = lines[i + 1].strip('\n')
    p = os.path.join(result_path, ref[1:].replace(':', ' '))
    data.append((f"{ref}\n{seq}", p))

N = 3
n_each = int(len(data)/N) + 1 if len(data) % N != 0 else int(len(data)/N)
browsers = [webdriver.Chrome(options=Options(), service=Service()) for _ in range(N)]
threads = [Thread(target=fetch_and_store, args=(browsers[i], data[i*n_each:(i+1)*n_each])) for i in range(3)]
for th in threads:
    th.start()

for th in threads:
    th.join()

for browser in browsers:
    browser.quit()
