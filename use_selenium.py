import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load initial data from CSV
df_data_batter = pd.read_csv('data_batter.csv')

# Setup Selenium WebDriver with headless option
options = Options()
options.add_argument("headless")
service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# Starting URL
starting_url = "https://statiz.sporki.com/stats/?m=main&m2=batting&m3=default&so=PA&ob=DESC&year=2024&sy=&ey=&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=WAROff&sk1=&sv1=&sf2=WAROff&sk2=&sv2="
driver.get(starting_url)
time.sleep(1)  # Initial page load time

# Define the specific row indices and their corresponding labels
indices_ranges = [(2, 9), (16, 25), (30, 38)]
labels = ['2사 득점권', 'CL & Late', '동점 상황', '1점차 이내', '2점차 이내', '3점차 이내', '4점차 이내', '5점차 이상', '득점권', '주자 있음', '주자 없음', '주자 1루', '주자 2루', '주자 3루', '주자 1,2루', '주자 1,3루', '주자 2,3루', '주자 만루', '1회', '2회', '3회', '4회', '5회', '6회', '7회', '8회', '9회']

# Process each row in the DataFrame
for i in range(3, len(df_data_batter) + 3):
    try:
        # Navigate to player detail page
        player_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[2]/div[6]/section/div[8]/table/tbody/tr[{i}]/td[2]")))
        player_link.click()
        time.sleep(1)  # Detail page loading time

        # Collect additional data
        team = driver.find_element(By.XPATH, "/html/body/div[2]/div[6]/section/div[3]/div[1]/div[3]/div[2]/span[1]").text
        position = driver.find_element(By.XPATH, "/html/body/div[2]/div[6]/section/div[3]/div[1]/div[3]/div[2]/span[2]").text
        style = driver.find_element(By.XPATH, "/html/body/div[2]/div[6]/section/div[3]/div[1]/div[3]/div[2]/span[3]").text
        
        # Append data to DataFrame
        df_data_batter.loc[i - 3, '팀'] = team
        df_data_batter.loc[i - 3, '포지션'] = position
        df_data_batter.loc[i - 3, '투타유형'] = style

        # # Click on the button to open a new set of data
        # navigation_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/section/div[2]/div[2]/ul/li[5]/a")))
        # navigation_button.click()
        # time.sleep(1)

        # # Interact with dropdown menu
        # dropdown_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select_si"]/button')))
        # dropdown_button.click()
        # time.sleep(0.5)
        
        # dropdown_selection = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select_si"]/ul/li[5]')))
        # dropdown_selection.click()
        # time.sleep(2)

        # # Collect specific data from the table
        # data_collected = {}
        # cnt = 0
        # for start, end in indices_ranges:
        #     for idx in range(start, end + 1):
        #         data_xpath = f"/html/body/div[2]/div[6]/section/div[3]/table/tbody/tr[{idx}]/td[19]"
        #         data_element = driver.find_element(By.XPATH, data_xpath)
        #         data_collected[labels[cnt]] = data_element.text if data_element else 'No data'
        #         cnt += 1
        
        # # Example of storing data in df_data_batter
        # for label, value in data_collected.items():
        #     df_data_batter.at[i-3, label] = value
        
        # # print(df_data_batter.iloc[i-3])
        # # print('\n')
        
        # Navigate back to the initial list page
        print(f"{i-2}/{len(df_data_batter)}")
        driver.get(starting_url)
        time.sleep(0.5)
    except Exception as e:
        print(f"Error processing player at index {i}: {str(e)}")

# Close the WebDriver
driver.quit()

# Save the updated DataFrame
df_data_batter.to_csv('22222.csv', index=False)
print("Data scraping and saving completed.")
