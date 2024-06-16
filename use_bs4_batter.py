import requests
from bs4 import BeautifulSoup
import pandas as pd

# URLs
url_default = "https://statiz.sporki.com/stats/?m=main&m2=batting&m3=default&so=PA&ob=DESC&year=2024&sy=&ey=&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=WAROff&sk1=&sv1=&sf2=WAROff&sk2=&sv2="
url_bat = "https://statiz.sporki.com/stats/?m=main&m2=batting&m3=bat&so=PA&ob=DESC&year=2024&sy=&ey=&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=WAROff&sk1=&sv1=&sf2=WAROff&sk2=&sv2="
url_direction = "https://statiz.sporki.com/stats/?m=main&m2=batting&m3=direction&so=PA&ob=DESC&year=2024&sy=&ey=&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=WAROff&sk1=&sv1=&sf2=WAROff&sk2=&sv2="

# Fetch and create DataFrame for Default Stats
response_default = requests.get(url_default)
soup_default = BeautifulSoup(response_default.text, 'html.parser')
rows_default = [[td.text.strip() for td in tr.find_all('td')] for tr in soup_default.find_all('tr')[1:]]
df_default = pd.DataFrame(rows_default, columns=['Rank', 'Name', 'Team', 'PAs', 'oWAR', 'dWAR', 'G', 'PA', 'ePA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'TB', 'RBI', 'SB', 'CS' ,'BB', 'HP', 'IB', 'SO', 'GDP', 'SH', 'SF', 'AVG', 'OBP', 'SLG', 'OPS', 'R/ePA', 'WRC+', 'WAR'])

# Fetch and create DataFrame for Bat Stats
response_bat = requests.get(url_bat)
soup_bat = BeautifulSoup(response_bat.text, 'html.parser')
rows_bat = [[td.text.strip() for td in tr.find_all('td')] for tr in soup_bat.find_all('tr')[1:]]
df_bat = pd.DataFrame(rows_bat, columns=['Rank', 'Name', 'Team', 'PAs', 'PA', 'BIP', 'BABIP','GB%','ifFB%', 'ofFB%', 'FB%', 'LD%','GB/FB','HR/FB%', 'if1B%','ROE','LROB', '번트안타','번트아웃','타율', '시도', '%'])

# Fetch and create DataFrame for Direction Stats
response_direction = requests.get(url_direction)
soup_direction = BeautifulSoup(response_direction.text, 'html.parser')
rows_direction = [[td.text.strip() for td in tr.find_all('td')] for tr in soup_direction.find_all('tr')[1:]]
df_direction = pd.DataFrame(rows_direction, columns=['Rank', 'Name', 'Team', 'PAs','PA','좌%','좌중%','중%','우중%','우%','당%','밀%','좌','좌중','중','우중', '우', '당', '밀', '좌_안타', '좌중_안타', '중_안타', '우중_안타', '우_안타','당_안타','밀_안타','좌_안타비율', '좌중안타비율', '중안타비율', '우중안타비율', '우안타비율', '당안타비율', '밀안타비율', 'BABIP'])

# 각 DataFrame에서 중복 검사
print(df_default.duplicated('Name').sum())
print(df_bat.duplicated('Name').sum())
print(df_direction.duplicated('Name').sum())

# 중복 제거
df_default = df_default.drop_duplicates('Name')
df_bat = df_bat.drop_duplicates('Name')
df_direction = df_direction.drop_duplicates('Name')

df_bat.drop(['PAs', 'PA', 'Rank', 'Team'], axis=1, inplace=True)
df_direction.drop(['PAs', 'PA', 'Rank', 'Team', 'BABIP'], axis=1, inplace=True)


# Assuming Name column is kept for merging purposes
df_data_batter_info = pd.merge(df_default, df_bat, on='Name', how='left')
df_data_batter_info = pd.merge(df_data_batter_info, df_direction, on='Name', how='left')

df_data_batter_info.drop(['PAs', 'Rank', 'Team'], axis=1, inplace=True)
df_data_batter_info.drop(0, axis=0, inplace=True)
df_data_batter_info['PA'] = df_data_batter_info['PA'].astype(int)
df_data_batter_info = df_data_batter_info.sort_values('PA', ascending=False)
# Print the final DataFrame to verify it
print(df_data_batter_info)
df_data_batter_info.to_csv("data_batter.csv", index=False)

