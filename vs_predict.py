import pandas as pd
import numpy as np

# 데이터 불러오기
data_batter =  pd.read_csv('data_batter.csv')
data_pitcher = pd.read_csv('data_pitcher.csv')

# 숫자형 데이터 형식 변환
for col in data_batter.columns:
    if data_batter[col].dtype == 'object':
        try:
            data_batter[col] = data_batter[col].astype(float)
        except ValueError:
            pass

for col in data_pitcher.columns:
    if data_pitcher[col].dtype == 'object':
        try:
            data_pitcher[col] = data_pitcher[col].astype(float)
        except ValueError:
            pass

# 결측치 처리
data_batter = data_batter.fillna(data_batter.median(numeric_only=True))
data_pitcher = data_pitcher.fillna(data_pitcher.median(numeric_only=True))

# 필요한 컬럼 선택
batter_columns = [
    'Name', 'AB', 'H', '2B', '3B', 'HR', 'SO', 'BB', 'GB%', 'FB%', 'LD%',
    '좌%', '좌중%', '중%', '우중%', '우%', '좌_안타비율', '좌중안타비율', '중안타비율', '우중안타비율', '우안타비율'
]
pitcher_columns = [
    'Name', 'TBF', 'H', 'SO', 'BB', 'GB%', 'FB%', 'LD%', 'HR/FB%',
    '좌%', '좌중%', '중%', '우중%', '우%', '좌_안타비율', '좌중안타비율', '중안타비율', '우중안타비율', '우안타비율'
]

batter_data = data_batter[batter_columns].copy()
pitcher_data = data_pitcher[pitcher_columns].copy()

# 예측 함수 작성
def predict_matchup(batter_name, pitcher_name):
    batter = batter_data[batter_data['Name'] == batter_name]
    pitcher = pitcher_data[pitcher_data['Name'] == pitcher_name]
    print(batter)
    if batter.empty or pitcher.empty:
        return "Invalid batter or pitcher name."

    combined = {}

    combined['Batter_avg'] = batter['H'].values / batter['AB'].values
    combined['Pitcher_avg'] = pitcher['H'].values/pitcher['TBF'].values
    combined['AVG'] = (combined['Batter_avg']) * (combined['Pitcher_avg']) + (1-combined['Batter_avg']) * (combined['Pitcher_avg']) / 2 + (combined['Batter_avg']) * (1-combined['Pitcher_avg']) / 2
    combined['GB%'] = (batter['GB%'].values) * (pitcher['GB%'].values) + (1-batter['GB%'].values) * (pitcher['GB%'].values) / 2 + (batter['GB%'].values) * (1-pitcher['GB%'].values) / 2
    combined['FB%'] = (batter['FB%'].values) * (pitcher['FB%'].values) + (1-batter['FB%'].values) * (pitcher['FB%'].values) / 2 + (batter['FB%'].values) * (1-pitcher['FB%'].values) / 2
    # combined['LD%'] = 1 - combined['FB%'] - combined['GB%']
    combined['좌%'] = (batter['좌%'].values) * (pitcher['좌%'].values) + (1-batter['좌%'].values) * (pitcher['좌%'].values) / 2 + (batter['좌%'].values) * (1-pitcher['좌%'].values) / 2
    combined['좌중%'] = (batter['좌중%'].values) * (pitcher['좌중%'].values) + (1-batter['좌중%'].values) * (pitcher['좌중%'].values) / 2 + (batter['좌중%'].values) * (1-pitcher['좌중%'].values) / 2
    combined['중%'] = (batter['중%'].values) * (pitcher['중%'].values) + (1-batter['중%'].values) * (pitcher['중%'].values) / 2 + (batter['중%'].values) * (1-pitcher['중%'].values) / 2
    combined['우중%'] = (batter['우중%'].values) * (pitcher['우중%'].values) + (1-batter['우중%'].values) * (pitcher['우중%'].values) / 2 + (batter['우중%'].values) * (1-pitcher['우중%'].values) / 2
    combined['우%'] = (batter['우%'].values) * (pitcher['우%'].values) + (1-batter['우%'].values) * (pitcher['우%'].values) / 2 + (batter['우%'].values) * (1-pitcher['우%'].values) / 2



    # 예측할 결과들
    hit_prob = combined['AVG']
    out_prob = 1 - hit_prob
    
    # 각 확률 계산 (단일 값으로 변환)
    gb_prob = combined['GB%'] * out_prob / 100
    fb_prob = combined['FB%'] * out_prob / 100
    ld_prob = (1-gb_prob-fb_prob) * out_prob / 100
    left_prob = combined['좌%'][0] / 100,
    leftcenter_prob = combined['좌중%'][0] / 100,
    center_prob = combined['중%'][0] / 100,
    rightcenter_prob = combined['우중%'][0] / 100,
    right_prob = combined['우%'][0] / 100,

    result = {
        '안타 확률': hit_prob[0],
        '아웃 확률': out_prob[0],
        # '2루타 확률': combined['2B'].values[0] / combined['AB'].values[0],
        # '3루타 확률': combined['3B'].values[0] / combined['AB'].values[0],
        # '홈런 확률': combined['HR'].values[0] / combined['AB'].values[0],
        '뜬공 확률': fb_prob[0],
        '땅볼 확률': gb_prob[0],
        '직선타 확률': ld_prob[0],
        '좌측 확률': left_prob[0],
        '좌중간 확률': leftcenter_prob[0],
        '중간 확률': center_prob[0],
        '우중간 확률': rightcenter_prob[0],
        '우측 확률': right_prob[0]
    }
    
    return result

# 예측 예시
result = predict_matchup('김혜성', '김광현')
print(result)
