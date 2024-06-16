import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load initial data from CSV
df_data_pitcher = pd.read_csv('data_pitcher.csv')

# Setup Selenium WebDriver with headless option
options = Options()
options.add_argument("headless")
service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# Starting URL
starting_url = "https://statiz.sporki.com/stats/?m=main&m2=pitching&m3=default&so=G&ob=DESC&year=2024&sy=&ey=&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=G&sk1=&sv1=&sf2=G&sk2=&sv2="
driver.get(starting_url)
time.sleep(1)  # Initial page load time

# Define the specific row indices and their corresponding labels
indices_ranges = [(2, 9), (16, 25)]
labels = ['2사 득점권', 'CL & Late', '동점 상황', '1점차 이내', '2점차 이내', '3점차 이내', '4점차 이내', '5점차 이상', '득점권', '주자 있음', '주자 없음', '주자 1루', '주자 2루', '주자 3루', '주자 1,2루', '주자 1,3루', '주자 2,3루', '주자 만루']

# Process each row in the DataFrame
for i in range(3, len(df_data_pitcher) + 3):
    try:
        # Navigate to player detail page
        player_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[2]/div[6]/section/div[8]/table/tbody/tr[{i}]/td[2]")))
        player_link.click()
        time.sleep(2)  # Detail page loading time

        # Collect additional data
        team = driver.find_element(By.XPATH, "/html/body/div[2]/div[6]/section/div[3]/div[1]/div[3]/div[2]/span[1]").text
        position = driver.find_element(By.XPATH, "/html/body/div[2]/div[6]/section/div[3]/div[1]/div[3]/div[2]/span[2]").text
        style = driver.find_element(By.XPATH, "/html/body/div[2]/div[6]/section/div[3]/div[1]/div[3]/div[2]/span[3]").text
        
        # Append data to DataFrame
        df_data_pitcher.loc[i - 3, '팀'] = team
        df_data_pitcher.loc[i - 3, '포지션'] = position
        df_data_pitcher.loc[i - 3, '투타유형'] = style
        print(team, position, style)

        # Click on the button to open a new set of data
        navigation_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/section/div[2]/div[2]/ul/li[5]/a")))
        navigation_button.click()
        time.sleep(2)

        # Interact with dropdown menu
        dropdown_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select_si"]/button')))
        dropdown_button.click()
        time.sleep(1)
        
        dropdown_selection = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select_si"]/ul/li[5]')))
        dropdown_selection.click()
        time.sleep(4)

        # Collect specific data from the table
        data_collected = {}
        cnt = 0
        for start, end in indices_ranges:
            for idx in range(start, end + 1):
                data_xpath = f"/html/body/div[2]/div[6]/section/div[3]/table/tbody/tr[{idx}]/td[17]"
                data_element = driver.find_element(By.XPATH, data_xpath)
                data_collected[labels[cnt]] = data_element.text if data_element else 'No data'
                cnt += 1
        
        # Example of storing data in df_data_pitcher
        for label, value in data_collected.items():
            df_data_pitcher.at[i-3, label] = value
        
        # print(df_data_pitcher.iloc[i-3])
        # print('\n')
        
        # Navigate back to the initial list page
        print(f"{i-2}/{len(df_data_pitcher)}")
        driver.get(starting_url)
        time.sleep(1)
    except Exception as e:
        print(f"Error processing player at index {i}: {str(e)}")
        driver.get(starting_url)
        time.sleep(1)

# Close the WebDriver
driver.quit()

# Save the updated DataFrame
df_data_pitcher.to_csv('pitcher_data_option2.csv', index=False)
print("Data scraping and saving completed.")

# 에러 목록: 5-ssg, 85-nc, 92키움, 94기아, 96기아, 97기아, 98소시지, 100키움, 102접씨, 103엔씨, 105엔씨, 107엘지, 109엘지, 110엘지, 111소시지, 112킅, 113엘지, 116삼성, 119엘지, 120엘지, 121삼성, 122기아, 127-우투우타, 팀x?, 133두산, 137소시지, 139두산, 140소시지, 141소시지, 142두산, 145키움, 147소시지, 148소시지, 149, 150키움, 152기아, 153, 154기아, 156킅, 157크트, 159쥐, 162롯데, 163두산, 164?, 165두산, 166두산, 166큠, 169?, 171크트, 173소시지, 174두산, 175크트우언우타, 176?, 177?, 178기아, 180롯데, 181롯데, 182롯데, 183?, 184삼성, 
# 6-한두솔, 73-ssg, 75-kia, 77기아, 89기아, 93-키움, 97키움, 

# 에러: 선수 별 존재하지 않는 경우의 데이터 존재 -> 수동으로 확인 및 채우기