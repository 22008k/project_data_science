import pandas as pd
import requests
from bs4 import BeautifulSoup

# 웹 페이지 URL
url = 'https://statiz.sporki.com/stats/?m=main&m2=batting&m3=running&so=PA&ob=DESC&year=2024&sy=&ey=&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=PA&sk1=&sv1=&sf2=PA&sk2=&sv2='
# 웹 페이지에서 HTML 내용 가져오기
response = requests.get(url)
html_content = response.text

# HTML 내용 파싱
soup = BeautifulSoup(html_content, 'html.parser')
rows = soup.find_all('tr')

# 데이터를 저장할 딕셔너리
data_CS = {'Name': [], 'CS': [], 'CS%': []}

# 중복 이름 확인을 위한 집합
seen_names = set()

# 각 행별로 필요한 데이터 추출
for row in rows:
    columns = row.find_all('td')
    if len(columns) > 12:  # 충분한 데이터가 있는지 확인
        name = columns[1].get_text(strip=True)  # 이름

        CS_value = columns[31].get_text(strip=True)  # 11번째 열(E 열)
        CS_per_value = columns[32].get_text(strip=True)  # 12번째 열(F% 열)

        data_CS['Name'].append(name)
        data_CS['CS'].append(CS_value)
        data_CS['CS%'].append(CS_per_value)

# DataFrame 생성
df_CS = pd.DataFrame(data_CS)


# 웹 페이지 URL
url_teambatting = 'https://statiz.sporki.com/stats/?m=main&m2=batting&m3=team&so=GDP&ob=DESC&year=2024&sy=&ey=&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=WAROff&sk1=&sv1=&sf2=WAROff&sk2=&sv2='
# 웹 페이지에서 HTML 내용 가져오기
response = requests.get(url_teambatting)
html_content = response.text

# HTML 내용 파싱
soup = BeautifulSoup(html_content, 'html.parser')
rows = soup.find_all('tr')

# 데이터를 저장할 딕셔너리
data_teambatting = {'Name': [], 'GDP': [], 'GDP%': [], '잔루':[], '잔루%':[], '희생번트실패':[], '희생번트실패%':[]}


# 중복 이름 확인을 위한 집합
seen_names = set()

# 각 행별로 필요한 데이터 추출
for row in rows:
    columns = row.find_all('td')
    if len(columns) < 18:
        continue 
    name = columns[1].get_text(strip=True)  # 이름
    if name in seen_names:
        continue  # 이름이 이미 처리되었다면 이 행은 건너뜁니다.
    seen_names.add(name)  # 새 이름을 집합에 추가

    GDP_value = columns[9].get_text(strip=True)  # 11번째 열(E 열)
    GDPper_value = columns[11].get_text(strip=True)  # 12번째 열(F% 열)
    data1_value = columns[12].get_text(strip=True)  # 12번째 열(F% 열)
    data1per_value = columns[13].get_text(strip=True)  # 12번째 열(F% 열)
    data2_value = columns[16].get_text(strip=True)  # 12번째 열(F% 열)
    data2per_value = columns[17].get_text(strip=True)  # 12번째 열(F% 열)

    data_teambatting['Name'].append(name)
    data_teambatting['GDP'].append(GDP_value)
    data_teambatting['GDP%'].append(GDPper_value)
    data_teambatting['잔루'].append(data1_value)
    data_teambatting['잔루%'].append(data1per_value)
    data_teambatting['희생번트실패'].append(data2_value)
    data_teambatting['희생번트실패%'].append(data2per_value)

# DataFrame 생성
df_teambatting = pd.DataFrame(data_teambatting)


# CSV 파일을 데이터프레임으로 로드
df = pd.read_csv('data_batter.csv')

# Name, GDP, SO, BB 열만 선택
selected_columns_df = df[['Name',  'SO', 'ifFB%', 'AVG', 'OPS']]


# 웹 페이지 URL
url3 = 'https://statiz.sporki.com/stats/?m=main&m2=fielding&m3=default&so=&ob=&year=2024&sy=&ey=&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=G&sk1=&sv1=&sf2=G&sk2=&sv2='
# 웹 페이지에서 HTML 내용 가져오기
response = requests.get(url3)
html_content = response.text

# HTML 내용 파싱
soup = BeautifulSoup(html_content, 'html.parser')
rows = soup.find_all('tr')

# 데이터를 저장할 딕셔너리
data3 = {'Name': [], 'Team':[],'E': [], 'F%': []}

# 중복 이름 확인을 위한 집합
seen_names = set()

# 각 행별로 필요한 데이터 추출
for row in rows:
    columns = row.find_all('td')
    if len(columns) > 12:  # 충분한 데이터가 있는지 확인
        name = columns[1].get_text(strip=True)  # 이름
        if name in seen_names:
            continue  # 이름이 이미 처리되었다면 이 행은 건너뜁니다.
        seen_names.add(name)  # 새 이름을 집합에 추가
        team = columns[2].get_text(strip=True)[2:]
        e_value = columns[10].get_text(strip=True)  # 11번째 열(E 열)
        f_value = columns[11].get_text(strip=True)  # 12번째 열(F% 열)
        if team == 'P':
          continue
        if f_value == None:
          f_Value = 0
        data3['Name'].append(name)
        data3['Team'].append(team)
        data3['E'].append(e_value)
        data3['F%'].append(f_value)

# DataFrame 생성
df3 = pd.DataFrame(data3)


df_merge1 = df_CS.merge(df_teambatting, on='Name')
df_merge2 = df_merge1.merge(selected_columns_df, on='Name')
df_merge3 = df_merge2.merge(df3, on='Name')


df_merge3.to_csv("bs_base_data.csv", index=False)



final_data_filled = df_merge3
##
# Renaming the columns to English for easier processing
final_data_filled.columns = ['Name', 'CS', 'CS%', 'GDP', 'GDP%', 'Lob', 'Lob%', 'BuntOut', 'BuntOut%', 'SO', 'ifFB%', 'AVG', 'OPS', 'Team', 'E', 'F%']
# Convert columns to numeric values, forcing errors to NaN (which are then filled with 0)
numeric_columns = [ 'CS', 'CS%', 'GDP', 'GDP%', 'Lob', 'Lob%', 'BuntOut', 'BuntOut%', 'SO', 'ifFB%', 'AVG', 'OPS', 'E', 'F%']
final_data_filled[numeric_columns] = final_data_filled[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Fill NaN values with 0
final_data_filled.fillna(0, inplace=True)

# Normalize each numeric column to have min 0 and max 100
for column in numeric_columns:
    min_val = final_data_filled[column].min()
    max_val = final_data_filled[column].max()
    final_data_filled[column] = (final_data_filled[column] - min_val) / (max_val - min_val) * 100

# Calculate the average of columns 7 (AVG) and 8 (OPS) after normalization
avg_col_avg = final_data_filled['AVG'].mean()
avg_col_ops = final_data_filled['OPS'].mean()

# Define a function to calculate the new data for each row with normalized values
def calculate_bs_indicator(row):
    new_value = int(
        row['GDP'] * 15 +
        row['GDP%'] * 10 +
        row['Lob%'] * 6 +
        (row['SO']) * 6 +
        row['BuntOut'] * 7 +
        row['ifFB%'] * 3 +
        ((row['AVG'] - avg_col_avg) / avg_col_avg) * 100 * 5 +
        ((row['OPS'] - avg_col_ops) / avg_col_ops) * 100 * 8 +
        row['E'] * 15 +
        (100 - row['F%'])
    )
    return new_value

# Apply the function to each row to get the new 'BS지표' column
final_data_filled['BS지표'] = final_data_filled.apply(calculate_bs_indicator, axis=1)

# Create a new dataframe with 'Name' and 'BS지표' and sort by 'BS지표' in ascending order
bs_data = final_data_filled[['Name', 'BS지표']].sort_values(by='BS지표', ascending=False).reset_index(drop=True)


# Display the sorted dataframe in ascending order
bs_data.head(15)


bs_data.to_csv("bs_data.csv", index=False)
