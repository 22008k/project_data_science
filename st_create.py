import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
import random


# 한글 폰트 설정
mpl.rcParams['font.family'] = 'NanumGothic'

# # 한글 폰트 설정
# font_path = 'NanumGothic.ttf'  # 폰트 파일 경로를 정확하게 지정하세요.
# font_name = fm.FontProperties(fname=font_path).get_name()
# mpl.rcParams['font.family'] = font_name
# plt.rc('font', family=font_name)

# Use st.cache_data to cache file reads
@st.cache_data
def load_data(filename):
    return pd.read_csv(filename)

# Data loading with specified paths
df_batter_name = load_data('player_data.csv')
df_batter_stat = load_data('data_batter.csv')
df_pitcher_name = load_data('pitcher_data.csv')
df_pitcher_stat = load_data('data_pitcher.csv')
df_bs_data = load_data('bs_data.csv')
df_bs_base_data = load_data('bs_base_data.csv')

df_merged = pd.merge(df_bs_data, df_batter_stat[['Name', 'WAR']], on='Name', how='inner')


# Renaming the columns to English for easier processing
df_bs_base_data.columns = ['Name', 'CS', 'CS%', 'GDP', 'GDP%', 'Lob', 'Lob%', 'BuntOut', 'BuntOut%', 'SO', 'ifFB%', 'AVG', 'OPS', 'Team', 'E', 'F%']
# Convert columns to numeric values, forcing errors to NaN (which are then filled with 0)
numeric_columns = [ 'CS', 'CS%', 'GDP', 'GDP%', 'Lob', 'Lob%', 'BuntOut', 'BuntOut%', 'SO', 'ifFB%', 'AVG', 'OPS', 'E', 'F%']
df_bs_base_data[numeric_columns] = df_bs_base_data[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Normalize each numeric column to have min 0 and max 100
for column in numeric_columns:
    min_val = df_bs_base_data[column].min()
    max_val = df_bs_base_data[column].max()
    if max_val != min_val:  # Avoid division by zero
        df_bs_base_data[column] = (df_bs_base_data[column] - min_val) / (max_val - min_val) * 100


# Sidebar options
sidebar_options = ['야구 데이터 설명', '타자정보', '투수정보', 'vs', 'NEW 지표!', '미니게임']
selected_option = st.sidebar.selectbox("메뉴를 선택하세요:", sidebar_options)

# Resetting session state when a new name query is made
def reset_state():
    st.session_state.pop('selected_row', None)  # Remove specific key if exists
    st.session_state.pop('stat_data', None)  # Clear detailed stats
    st.session_state.button_clicked = False

# Initialize session state
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Function to display player data
def display_player_data(player_data, stat_data=None):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="personal-info">', unsafe_allow_html=True)
        st.markdown("### Personal Info")
        st.markdown(f"**Name:** <span class='highlight'>{player_data['Name']}</span>", unsafe_allow_html=True)
        st.markdown(f"**Team:** {player_data['Team']}")
        st.markdown(f"**Position:** {player_data['Position']}")
        st.markdown(f"**Birth:** {player_data['Birth'][5:]}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="game-stats">', unsafe_allow_html=True)
        st.markdown("### Game Stats")
        for key, value in stat_data.to_dict().items():
            st.markdown(f"**{key}:** <span class='highlight'>{value}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# 숫자형 데이터 형식 변환
for col in df_batter_stat.columns:
    if df_batter_stat[col].dtype == 'object':
        try:
            df_batter_stat[col] = df_batter_stat[col].astype(float)
        except ValueError:
            pass

for col in df_pitcher_stat.columns:
    if df_pitcher_stat[col].dtype == 'object':
        try:
            df_pitcher_stat[col] = df_pitcher_stat[col].astype(float)
        except ValueError:
            pass

# 결측치 처리
data_batter = df_batter_stat.fillna(df_batter_stat.median(numeric_only=True))
data_pitcher = df_pitcher_stat.fillna(df_pitcher_stat.median(numeric_only=True))

# 필요한 컬럼 선택
batter_columns = [
    'Name', 'AB', 'H', '2B', '3B', 'HR', 'SO', 'BB', 'GB%', 'FB%', 'LD%',
    '좌%', '좌중%', '중%', '우중%', '우%', '좌_안타비율', '좌중안타비율', '중안타비율', '우중안타비율', '우안타비율'
]
pitcher_columns = [
    'Name', 'TBF', 'H', '2B', '3B', 'HR', 'SO', 'BB', 'GB%', 'FB%', 'LD%', 'HR/FB%',
    '좌%', '좌중%', '중%', '우중%', '우%', '좌_안타비율', '좌중안타비율', '중안타비율', '우중안타비율', '우안타비율'
]

batter_data = df_batter_stat[batter_columns].copy()
pitcher_data = df_pitcher_stat[pitcher_columns].copy()
# Additional CSS for better styling
st.markdown(
    """
    <style>
    .highlight {
        color: #ffcc00;
        font-weight: bold;
    }
    .personal-info, .game-stats {
        padding: 20px;
        background-color: #282828;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .personal-info h2, .game-stats h2 {
        border-bottom: 2px solid #ffcc00;
        padding-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# 예측 함수 작성
def predict_matchup(batter_name, pitcher_name):
    batter = batter_data[batter_data['Name'] == batter_name]
    pitcher = pitcher_data[pitcher_data['Name'] == pitcher_name]
    if batter.empty or pitcher.empty:
        return "Invalid batter or pitcher name."

    combined = {}

    combined['Batter_avg'] = batter['H'].values / batter['AB'].values
    combined['Pitcher_avg'] = pitcher['H'].values / pitcher['TBF'].values
    combined['Batter_2B'] = batter['2B'].values / batter['H'].values
    combined['Pitcher_2B'] = pitcher['2B'].values / pitcher['H'].values
    combined['Batter_3B'] = batter['3B'].values / batter['H'].values
    combined['Pitcher_3B'] = pitcher['3B'].values / pitcher['H'].values
    combined['Batter_HR'] = batter['HR'].values / batter['H'].values
    combined['Pitcher_HR'] = pitcher['HR'].values / pitcher['H'].values

    combined['AVG'] = (combined['Batter_avg']) * (combined['Pitcher_avg']) * 1.2 + (1 - combined['Batter_avg']) * (
    combined['Pitcher_avg']) / 2.5 + (combined['Batter_avg']) * (1 - combined['Pitcher_avg']) / 1.5
    combined['2B'] = ((combined['Batter_2B']) * (combined['Pitcher_2B']) + (1 - combined['Batter_2B']) * (
    combined['Pitcher_2B']) / 2 + (combined['Batter_2B']) * (1 - combined['Pitcher_2B']) / 2)
    combined['3B'] = ((combined['Batter_3B']) * (combined['Pitcher_3B']) + (1 - combined['Batter_3B']) * (
    combined['Pitcher_3B']) / 2 + (combined['Batter_3B']) * (1 - combined['Pitcher_3B']) / 2)
    combined['HR'] = ((combined['Batter_HR']) * (combined['Pitcher_HR']) + (1 - combined['Batter_HR']) * (
    combined['Pitcher_HR']) / 2 + (combined['Batter_HR']) * (1 - combined['Pitcher_HR']) / 2)

    combined['GB%'] = (batter['GB%'].values) * (pitcher['GB%'].values) + (1 - batter['GB%'].values) * (
        pitcher['GB%'].values) / 2 + (batter['GB%'].values) * (1 - pitcher['GB%'].values) / 2
    combined['FB%'] = (batter['FB%'].values) * (pitcher['FB%'].values) + (1 - batter['FB%'].values) * (
        pitcher['FB%'].values) / 2 + (batter['FB%'].values) * (1 - pitcher['FB%'].values) / 2
    # combined['LD%'] = 1 - combined['FB%'] - combined['GB%']
    combined['좌%'] = (batter['좌%'].values) * (pitcher['좌%'].values) + (1 - batter['좌%'].values) * (
        pitcher['좌%'].values) / 2 + (batter['좌%'].values) * (1 - pitcher['좌%'].values) / 2
    combined['좌중%'] = (batter['좌중%'].values) * (pitcher['좌중%'].values) + (1 - batter['좌중%'].values) * (
        pitcher['좌중%'].values) / 2 + (batter['좌중%'].values) * (1 - pitcher['좌중%'].values) / 2
    combined['중%'] = (batter['중%'].values) * (pitcher['중%'].values) + (1 - batter['중%'].values) * (
        pitcher['중%'].values) / 2 + (batter['중%'].values) * (1 - pitcher['중%'].values) / 2
    combined['우중%'] = (batter['우중%'].values) * (pitcher['우중%'].values) + (1 - batter['우중%'].values) * (
        pitcher['우중%'].values) / 2 + (batter['우중%'].values) * (1 - pitcher['우중%'].values) / 2
    combined['우%'] = (batter['우%'].values) * (pitcher['우%'].values) + (1 - batter['우%'].values) * (
        pitcher['우%'].values) / 2 + (batter['우%'].values) * (1 - pitcher['우%'].values) / 2

    # 예측할 결과들
    hit_prob = combined['AVG']
    out_prob = 1 - hit_prob

    # 루타 예측
    a_2b_prob = combined['2B'] * hit_prob
    a_3b_prob = combined['3B'] * hit_prob
    a_HR_prob = combined['HR'] * hit_prob
    a_1b_prob = hit_prob - a_2b_prob - a_3b_prob - a_HR_prob

    # 각 확률 계산 (단일 값으로 변환)
    gb_prob = combined['GB%'] * out_prob / 100
    fb_prob = combined['FB%'] * out_prob / 100
    ld_prob = (1 - gb_prob - fb_prob) * out_prob / 100
    left_prob = combined['좌%'][0] / 100,
    leftcenter_prob = combined['좌중%'][0] / 100,
    center_prob = combined['중%'][0] / 100,
    rightcenter_prob = combined['우중%'][0] / 100,
    right_prob = combined['우%'][0] / 100,

    result = {
        '안타 확률': hit_prob[0],
        '아웃 확률': out_prob[0],
        '1루타 확률': a_1b_prob[0],
        '2루타 확률': a_2b_prob[0],
        '3루타 확률': a_3b_prob[0],
        '홈런 확률': a_HR_prob[0],
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

# Pages based on selection
if selected_option == '야구 데이터 설명':
    st.title('야구 데이터 설명')
    st.markdown('''
### 타자

1. **Name (이름)**: 선수의 이름을 나타냅니다.
2. **oWAR (공격 기여도)**: 공격에서 선수의 기여도를 나타냅니다.
3. **dWAR (수비 기여도)**: 수비에서 선수의 기여도를 나타냅니다.
4. **G (경기수)**: 선수가 출전한 경기의 수를 나타냅니다.
5. **PA (타석수)**: 선수가 타석에 들어선 총 횟수를 나타냅니다.
6. **ePA (조정된 타석수)**: 조정된 타석수를 나타냅니다.
7. **AB (타수)**: 선수가 타석에서 실제로 타격을 시도한 횟수를 나타냅니다.
8. **R (득점)**: 선수가 득점한 횟수를 나타냅니다.
9. **H (안타)**: 선수가 기록한 안타의 수를 나타냅니다.
10. **2B (2루타)**: 선수가 기록한 2루타의 수를 나타냅니다.
11. **3B (3루타)**: 선수가 기록한 3루타의 수를 나타냅니다.
12. **HR (홈런)**: 선수가 기록한 홈런의 수를 나타냅니다.
13. **TB (총루타수)**: 선수가 기록한 총 루타수를 나타냅니다.
14. **RBI (타점)**: 선수가 기록한 타점의 수를 나타냅니다.
15. **SB (도루)**: 선수가 기록한 도루의 수를 나타냅니다.
16. **CS (도루 실패)**: 도루를 시도하다 실패한 횟수를 나타냅니다.
17. **BB (볼넷)**: 선수가 기록한 볼넷의 수를 나타냅니다.
18. **HP (몸에 맞는 공)**: 선수의 몸에 맞은 공의 횟수를 나타냅니다.
19. **IB (고의사구)**: 선수가 기록한 고의사구의 수를 나타냅니다.
20. **SO (삼진)**: 선수가 삼진을 당한 횟수를 나타냅니다.
21. **GDP (병살타)**: 선수가 기록한 병살타의 수를 나타냅니다.
22. **SH (희생번트)**: 선수가 기록한 희생번트의 수를 나타냅니다.
23. **SF (희생플라이)**: 선수가 기록한 희생플라이의 수를 나타냅니다.
24. **AVG (타율)**: 타자의 타율을 나타냅니다.
25. **OBP (출루율)**: 타자의 출루율을 나타냅니다.
26. **SLG (장타율)**: 타자의 장타율을 나타냅니다.
27. **OPS (출루율+장타율)**: 출루율과 장타율을 합한 값으로, 타자의 전체적인 공격력을 나타냅니다.
28. **R/ePA (조정된 타석당 득점)**: 조정된 타석당 득점을 나타냅니다.
29. **WRC+ (조정된 득점 창출 능력)**: 타자의 득점 창출 능력을 조정하여 나타낸 값입니다.
30. **WAR (승리 기여도)**: 대체 선수 대비 승리에 기여한 정도를 나타냅니다.
31. **BIP (인플레이 타구)**: 인플레이 된 타구의 수를 나타냅니다.
32. **BABIP (타구시 안타 비율)**: 인플레이 된 타구가 안타가 될 확률을 나타냅니다.
33. **GB% (땅볼 비율)**: 전체 타구 중 땅볼의 비율을 나타냅니다.
34. **ifFB% (내야 뜬공 비율)**: 전체 타구 중 내야 뜬공의 비율을 나타냅니다.
35. **ofFB% (외야 뜬공 비율)**: 전체 타구 중 외야 뜬공의 비율을 나타냅니다.
36. **FB% (뜬공 비율)**: 전체 타구 중 뜬공의 비율을 나타냅니다.
37. **LD% (직선타 비율)**: 전체 타구 중 직선타의 비율을 나타냅니다.
38. **GB/FB (땅볼/뜬공 비율)**: 땅볼과 뜬공의 비율을 나타냅니다.
39. **HR/FB% (뜬공 중 홈런 비율)**: 뜬공 중 홈런이 된 비율을 나타냅니다.
40. **if1B% (내야 1루타 비율)**: 전체 타구 중 내야에서 기록한 1루타의 비율을 나타냅니다.
41. **ROE (수비 실책에 의한 출루)**: 수비 실책으로 인해 타자가 출루한 횟수를 나타냅니다.
42. **LROB (잔루 타율)**: 잔루 상황에서의 타율을 나타냅니다.
43. **번트안타 (번트로 기록한 안타)**: 번트를 통해 기록한 안타의 수를 나타냅니다.
44. **번트아웃 (번트아웃)**: 번트를 시도했으나 아웃된 횟수를 나타냅니다.
45. **타율 (타율)**: 타자의 타율을 나타냅니다.
46. **시도 (도루 시도)**: 도루 시도 횟수를 나타냅니다.
47. **% (도루 성공률)**: 도루 시도의 성공률을 나타냅니다.
48. **좌% (좌측 비율)**: 타구가 좌측으로 날아간 비율을 나타냅니다.
49. **좌중% (좌중간 비율)**: 타구가 좌중간으로 날아간 비율을 나타냅니다.
50. **중% (중앙 비율)**: 타구가 중앙으로 날아간 비율을 나타냅니다.
51. **우중% (우중간 비율)**: 타구가 우중간으로 날아간 비율을 나타냅니다.
52. **우% (우측 비율)**: 타구가 우측으로 날아간 비율을 나타냅니다.
53. **당% (당겨친 비율)**: 타구를 당겨 친 비율을 나타냅니다.
54. **밀% (밀어친 비율)**: 타구를 밀어 친 비율을 나타냅니다.
55. **좌 (좌측 안타)**: 좌측으로 날아간 안타의 수를 나타냅니다.
56. **좌중 (좌중간 안타)**: 좌중간으로 날아간 안타의 수를 나타냅니다.
57. **중 (중앙 안타)**: 중앙으로 날아간 안타의 수를 나타냅니다.
58. **우중 (우중간 안타)**: 우중간으로 날아간 안타의 수를 나타냅니다.
59. **우 (우측 안타)**: 우측으로 날아간 안타의 수를 나타냅니다.
60. **당 (당겨친 안타)**: 당겨 친 안타의 수를 나타냅니다.
61. **밀 (밀어친 안타)**: 밀어 친 안타의 수를 나타냅니다.
62. **좌_안타비율 (좌측 안타 비율)**: 좌측 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
63. **좌중안타비율 (좌중간 안타 비율)**: 좌중간 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
64. **중안타비율 (중앙 안타 비율)**: 중앙 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
65. **우중안타비율 (우중간 안타 비율)**: 우중간 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
66. **우안타비율 (우측 안타 비율)**: 우측 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
67. **당안타비율 (당겨친 안타 비율)**: 당겨 친 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
68. **밀안타비율 (밀어친 안타 비율)**: 밀어 친 안타가 전체 안타 중 차지하는 비율을 나타냅니다.

### 투수

69. **GS (선발경기수)**: 선수가 선발로 출전한 경기의 수를 나타냅니다.
70. **GR (구원경기수)**: 선수가 구원투수로 출전한 경기의 수를 나타냅니다.
71. **GF (경기종료수)**: 선수가 경기를 마무리한 횟수를 나타냅니다.
72. **CG (완투)**: 선수가 완투한 경기의 수를 나타냅니다.
73. **SHO (완봉)**: 선수가 상대 팀을 무득점으로 완투한 경기의 수를 나타냅니다.
74. **W (승리)**: 선수가 기록한 승리 횟수를 나타냅니다.
75. **L (패배)**: 선수가 기록한 패배 횟수를 나타냅니다.
76. **S (세이브)**: 선수가 기록한 세이브 횟수를 나타냅니다.
77. **HD (홀드)**: 선수가 기록한 홀드 횟수를 나타냅니다.
78. **IP (이닝)**: 선수가 던진 이닝 수를 나타냅니다.
79. **ER (자책점)**: 선수가 기록한 자책점의 수를 나타냅니다.
80. **R (실점)**: 선수가 기록한 실점의 수를 나타냅니다.
81. **rRA (조정 실점율)**: 선수의 실점율을 조정한 값을 나타냅니다.
82. **TBF (상대 타자수)**: 선수가 상대했던 타자의 총 수를 나타냅니다.
83. **H (피안타)**: 선수가 맞은 안타의 수를 나타냅니다.
84. **2B (피2루타)**: 선수가 맞은 2루타의 수를 나타냅니다.
85. **3B (피3루타)**: 선수가 맞은 3루타의 수를 나타냅니다.
86. **HR (피홈런)**: 선수가 맞은 홈런의 수를 나타냅니다.
87. **BB (볼넷)**: 선수가 기록한 볼넷의 수를 나타냅니다.
88. **HP (몸에 맞는 공)**: 선수가 몸에 맞는 공을 맞은 횟수를 나타냅니다.
89. **IB (고의사구)**: 선수가 기록한 고의사구의 수를 나타냅니다.
90. **SO (삼진)**: 선수가 기록한 삼진의 수를 나타냅니다.
91. **ROE (수비 실책에 의한 출루)**: 수비 실책으로 인해 타자가 출루한 횟수를 나타냅니다.
92. **BK (보크)**: 선수가 기록한 보크의 수를 나타냅니다.
93. **WP (폭투)**: 선수가 기록한 폭투의 수를 나타냅니다.
94. **ERA (평균자책점)**: 9이닝당 평균 자책점을 나타냅니다.
95. **RA9 (9이닝당 실점)**: 9이닝당 평균 실점을 나타냅니다.
96. **rRA9 (조정된 9이닝당 실점)**: 조정된 9이닝당 평균 실점을 나타냅니다.
97. **rRA9pf (조정된 9이닝당 실점+구장보정)**: 구장 요인을 고려하여 조정된 9이닝당 평균 실점을 나타냅니다.
98. **FIP (수비 무관 평균자책점)**: 투수의 실제 능력을 더 잘 반영하는 평균자책점을 나타냅니다.
99. **WHIP (이닝당 출루 허용률)**: 이닝당 허용한 출루율을 나타냅니다.
100. **WAR (대체 선수 대비 승리 기여도)**: 대체 선수 대비 승리에 기여한 정도를 나타냅니다.
101. **BIP (인플레이 타구)**: 인플레이 된 타구의 수를 나타냅니다.
102. **BABIP (타구시 안타 비율)**: 인플레이 된 타구가 안타가 될 확률을 나타냅니다.
103. **GB% (땅볼 비율)**: 전체 타구 중 땅볼의 비율을 나타냅니다.
104. **ifFB% (내야 뜬공 비율)**: 전체 타구 중 내야 뜬공의 비율을 나타냅니다.
105. **ofFB% (외야 뜬공 비율)**: 전체 타구 중 외야 뜬공의 비율을 나타냅니다.
106. **FB% (뜬공 비율)**: 전체 타구 중 뜬공의 비율을 나타냅니다.
107. **LD% (직선타 비율)**: 전체 타구 중 직선타의 비율을 나타냅니다.
108. **GB/FB (땅볼/뜬공 비율)**: 땅볼과 뜬공의 비율을 나타냅니다.
109. **HR/FB% (뜬공 중 홈런 비율)**: 뜬공 중 홈런이 된 비율을 나타냅니다.
110. **if1B% (내야 1루타 비율)**: 전체 타구 중 내야에서 기록한 1루타의 비율을 나타냅니다.
111. **좌% (좌측 비율)**: 타구가 좌측으로 날아간 비율을 나타냅니다.
112. **좌중% (좌중간 비율)**: 타구가 좌중간으로 날아간 비율을 나타냅니다.
113. **중% (중앙 비율)**: 타구가 중앙으로 날아간 비율을 나타냅니다.
114. **우중% (우중간 비율)**: 타구가 우중간으로 날아간 비율을 나타냅니다.
115. **우% (우측 비율)**: 타구가 우측으로 날아간 비율을 나타냅니다.
116. **당% (당겨친 비율)**: 타구를 당겨 친 비율을 나타냅니다.
117. **밀% (밀어친 비율)**: 타구를 밀어 친 비율을 나타냅니다.
118. **좌 (좌측 안타)**: 좌측으로 날아간 안타의 수를 나타냅니다.
119. **좌중 (좌중간 안타)**: 좌중간으로 날아간 안타의 수를 나타냅니다.
120. **중 (중앙 안타)**: 중앙으로 날아간 안타의 수를 나타냅니다.
121. **우중 (우중간 안타)**: 우중간으로 날아간 안타의 수를 나타냅니다.
122. **우 (우측 안타)**: 우측으로 날아간 안타의 수를 나타냅니다.
123. **당 (당겨친 안타)**: 당겨 친 안타의 수를 나타냅니다.
124. **밀 (밀어친 안타)**: 밀어 친 안타의 수를 나타냅니다.
125. **좌_안타비율 (좌측 안타 비율)**: 좌측 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
126. **좌중안타비율 (좌중간 안타 비율)**: 좌중간 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
127. **중안타비율 (중앙 안타 비율)**: 중앙 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
128. **우중안타비율 (우중간 안타 비율)**: 우중간 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
129. **우안타비율 (우측 안타 비율)**: 우측 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
130. **당안타비율 (당겨친 안타 비율)**: 당겨 친 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
131. **밀안타비율 (밀어친 안타 비율)**: 밀어 친 안타가 전체 안타 중 차지하는 비율을 나타냅니다.
    ''')

elif selected_option == '타자정보':
    
    st.title('타자 정보')
    
    batter_name = st.selectbox("타자를 선택하세요:", df_batter_name['Name'].unique())
    if batter_name:
        results = df_batter_name[df_batter_name['Name'] == batter_name]
        if not results.empty:
            st.write("선택한 타자 정보:")
            for i, row in results.iterrows():
                button_key = f"button_{i}"
                if st.button(f"{row['Name']} - {row['Position']} at {row['Team']}", key=button_key):
                    st.session_state['selected_row'] = row.to_dict()
                    row['Name'] = re.sub(r'\s*\(.*?\)', '', row['Name'])
                    matching_stats = df_batter_stat[df_batter_stat['Name'] == row['Name']].iloc[0]
                    st.session_state['stat_data'] = matching_stats if not matching_stats.empty else None
                    st.session_state['button_clicked'] = True
                
            if st.session_state.get('button_clicked', False):
                if 'selected_row' in st.session_state and 'stat_data' in st.session_state:
                    display_player_data(st.session_state['selected_row'], st.session_state['stat_data'])
                # Reset button clicked state
                st.session_state['button_clicked'] = False
        else:
            st.error("선택한 타자 정보가 없습니다.")

elif selected_option == '투수정보':
    st.title('투수 정보')
    
    pitcher_name = st.selectbox("투수를 선택하세요:", df_pitcher_name['Name'].unique())
    if pitcher_name:
        results = df_pitcher_name[df_pitcher_name['Name'] == pitcher_name]
        if not results.empty:
            st.write("선택한 투수 정보:")
            for i, row in results.iterrows():
                button_key = f"button_{i}"
                if st.session_state.get('button_clicked', False):
                    continue

                if st.button(f"{row['Name']} - {row['Position']} at {row['Team']}", key=button_key):
                    st.session_state['selected_row'] = row.to_dict()
                    row['Name'] = re.sub(r'\s*\(.*?\)', '', row['Name'])
                    matching_stats = df_pitcher_stat[df_pitcher_stat['Name'] == row['Name']].iloc[0]
                    st.session_state['stat_data'] = matching_stats if not matching_stats.empty else None
                    st.session_state['button_clicked'] = True

            if st.session_state.get('button_clicked', False):
                if 'selected_row' in st.session_state and 'stat_data' in st.session_state:
                    display_player_data(st.session_state['selected_row'], st.session_state['stat_data'])
                # Reset button clicked state
                st.session_state['button_clicked'] = False
        else:
            st.error("선택한 투수 정보가 없습니다.")


elif selected_option == 'vs':
    st.title('대결')

    col1, col2 = st.columns(2)
    with col1:
        batter_name = st.selectbox('타자를 선택하세요:', batter_data['Name'].unique(), key='batter_select')
    with col2:
        pitcher_name = st.selectbox('투수를 선택하세요:', pitcher_data['Name'].unique(), key='pitcher_select')


    if st.button('예측 실행'):
        if batter_name not in batter_data['Name'].values:
            st.error('존재하지 않는 타자입니다.')
        elif pitcher_name not in pitcher_data['Name'].values:
            st.error('존재하지 않는 투수입니다.')
        else:
            result = predict_matchup(batter_name, pitcher_name)
            st.write("예측 결과:")
            st.write(result)

            # 안타 확률과 아웃 확률을 원그래프로 시각화
            fig, ax = plt.subplots()
            ax.pie(
                [result['안타 확률'], result['아웃 확률']],
                labels=['Hit probability', 'Out probability'],
                autopct='%1.1f%%',
                startangle=90
            )
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)

            # 좌측 확률, 좌중간 확률, 중간 확률, 우중간 확률, 우측 확률을 원그래프로 시각화
            fig, ax = plt.subplots()
            ax.pie(
                [result['좌측 확률'], result['좌중간 확률'], result['중간 확률'], result['우중간 확률'], result['우측 확률']],
                labels=['Left', 'Left-Center', 'Center', 'Right-Center', 'Right'],
                autopct='%1.1f%%',
                startangle=90
            )
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)

            # 1루타, 2루타, 3루타, 홈런, 뜬공, 땅볼, 직선타 확률을 원그래프로 시각화
            fig, ax = plt.subplots()
            ax.pie(
                [result['1루타 확률'], result['2루타 확률'], result['3루타 확률'], result['홈런 확률'], result['뜬공 확률'], result['땅볼 확률'], result['직선타 확률']],
                labels=['1B probability', '2B probability', '3B probability', 'HR probability', 'FB probability', 'GB probability', 'LD probability'],
                autopct='%1.1f%%',
                startangle=90
            )
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)

elif selected_option == 'NEW 지표!':
    st.title('NEW 지표!')
    st.write('BS 지표 데이터를 확인하세요.')
    
    fm.fontManager.addfont(font_file)
    fm._load_fontmanager(try_read_cache=False)
    
    st.write(fm.fontManager.ttflist)
    st.write(type(fm.fontManager.ttflist))

    # BS 지표 데이터프레임을 스트림릿 애플리케이션에 표시
    st.dataframe(df_bs_data[['Name', 'BS지표']])

    # BS 지표 상위 10명을 차트로 시각화
    top_10_bs = df_bs_data.nlargest(10, 'BS지표')

    fig, ax = plt.subplots()
    ax.bar(top_10_bs['Name'], top_10_bs['BS지표'])
    ax.set_xlabel('Name')
    ax.set_ylabel('BS data')
    ax.set_title('Top 10 BS data')
    plt.xticks(rotation=45)
    
    # font_file = fm.findSystemFonts(fontpaths='NanumGothic.ttf')

    
    
    font_name = fm.FontProperties(fname='NanumGothic.ttf').get_name()
    mpl.rcParams['font.family'] = font_name
    plt.rc('font', family=font_name)

    st.pyplot(fig)

    # BS지표와 WAR의 관계를 나타내는 그래프
    fig, ax = plt.subplots()
    ax.scatter(df_merged['BS지표'], df_merged['WAR'])
    ax.set_xlabel('BS data')
    ax.set_ylabel('WAR')
    ax.set_title('BS data, WAR')
    st.pyplot(fig)

    # 선수 이름 검색
    player_name = st.text_input("선수 이름을 입력하세요:")

    if player_name:
        # 선수 데이터 검색
        player_data_bs = df_bs_data[df_bs_data['Name'].str.contains(player_name, case=False)]
        player_data_base = df_bs_base_data[df_bs_base_data['Name'].str.contains(player_name, case=False)]

        if not player_data_bs.empty and not player_data_base.empty:
            # 선수의 순위 계산dd
            player_rank = (df_bs_data['BS지표'].rank(ascending=False, method='min')[
                df_bs_data['Name'].str.contains(player_name, case=False)].values[0]).astype(int)
            player_bs = player_data_bs.iloc[0]['BS지표']

            st.write(f"선수 이름: {player_name}")
            st.write(f"순위: {player_rank}등")
            st.write(f"BS 지표: {player_bs}")

            # 정규화된 지표 막대 그래프로 시각화
            player_stats = player_data_base[numeric_columns].iloc[0]
            fig, ax = plt.subplots()
            ax.bar(player_stats.index, player_stats.values)
            ax.set_xlabel('bs data')
            ax.set_ylabel('data')
            ax.set_title(f"{player_name}'s data")
            plt.xticks(rotation=45)

            st.pyplot(fig)
        else:
            st.error("해당 선수의 데이터를 찾을 수 없습니다.")

elif selected_option == '미니게임':
    st.write("""
    # 야구 시뮬레이터
    이 앱을 통해 선택한 타자와 투구 위치, 투구 유형을 바탕으로 실제 투구 결과를 예측할 수 있습니다.

    ## 사용 방법

    1. **타자 선택:** 드롭다운 메뉴에서 타자를 선택하세요.
    2. **투구 위치 선택:** 3x3 그리드에서 투구 위치(1~9)를 선택하세요.
    3. **투구 유형 선택:** 라디오 버튼에서 직구 또는 변화구를 선택하세요.
    4. **예측:** "예측!" 버튼을 눌러 결과를 확인하세요.

    예측한 투구 위치와 유형이 실제 투구와 얼마나 일치하는지에 따라 다양한 타격 결과가 나옵니다.
    """)

    # Display the columns to check the correct column names
    # st.write("데이터프레임 열 이름:", df_batter_stat.columns.tolist())


    # Display 3x3 grid using HTML
    st.markdown("""
    <style>
    .table-container {
        display: flex;
        justify-content: center;
    }
    table {
        border-collapse: collapse;
        margin: 20px 0;
        table-layout: fixed;
    }
    table, th, td {
        border: 1px solid black;
        width: 100px;
        height: 100px;
        text-align: center;
        font-size: 24px;
    }
    </style>
    <div class="table-container">
    <table>
        <tr>
            <td>1</td>
            <td>2</td>
            <td>3</td>
        </tr>
        <tr>
            <td>4</td>
            <td>5</td>
            <td>6</td>
        </tr>
        <tr>
            <td>7</td>
            <td>8</td>
            <td>9</td>
        </tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

    # Helper function to check if two positions are in the same line
    def same_line(pos1, pos2):
        rows = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        cols = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        diags = [[1, 5, 9], [3, 5, 7]]
        lines = rows + cols + diags
        return any(pos1 in line and pos2 in line for line in lines)

    # Select batter
    batter_name = st.selectbox("타자를 선택하세요", df_batter_stat['Name'].unique())

    # Select pitch location (3x3 grid, represented as 1-9)
    pitch_location = st.selectbox("투구 위치를 선택하세요 (1-9)", list(range(1, 10)))

    # Select pitch type
    pitch_type = st.radio("투구 유형을 선택하세요", ['직구', '변화구'])

    # Predict button
    if st.button("예측!"):
        # Get the selected batter's data
        batter_data = df_batter_stat[df_batter_stat['Name'] == batter_name].iloc[0]
        
        # Randomly determine the actual pitch location and type
        actual_pitch_location = random.choice(list(range(1, 10)))
        actual_pitch_type = random.choice(['직구', '변화구'])

        st.write(f"실제 투구 위치: {actual_pitch_location}, 실제 투구 유형: {actual_pitch_type}")

        # Define hit and out probabilities
        hit_probabilities = {
            '좌중간 안타': batter_data['좌중안타비율'],
            '중간 안타': batter_data['중안타비율'],
            '우중간 안타': batter_data['우중안타비율'],
            '좌익수 앞 안타': batter_data['좌_안타비율'],
            '우익수 앞 안타': batter_data['우안타비율'],
            '당겨서 안타': batter_data['당안타비율'],
            '밀어서 안타': batter_data['밀안타비율']
        }

        out_probabilities = {
            '뜬공': 0.25,
            '땅볼': 0.25,
            '직선타': 0.2
        }

        total_probabilities = {**hit_probabilities, **out_probabilities}
        total = sum(total_probabilities.values())
        normalized_probabilities = {k: v/total for k, v in total_probabilities.items()}

        # Determine the result
        if pitch_type == actual_pitch_type:
            if same_line(pitch_location, actual_pitch_location):
                result = random.choices(list(normalized_probabilities.keys()), list(normalized_probabilities.values()), k=1)[0]
            else:
                result = random.choices(list(out_probabilities.keys()), list(out_probabilities.values()), k=1)[0]
        else:
            result = '삼진'
        
        st.write(f"결과: {result}")