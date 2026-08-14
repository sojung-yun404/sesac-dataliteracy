"""공통 로더 + 차트 스타일. 이후 모든 스크립트가 이걸 import 합니다."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

SRC = '1.2 EDA_뉴욕 따릉이_Level2_문제 .xlsx'

# ── 색 (검증된 팔레트) ──────────────────────────────────────────
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e5e4e0'

plt.rcParams.update({
    'font.family': 'Apple SD Gothic Neo',
    'axes.unicode_minus': False,
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
    'text.color': INK, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.spines.top': False, 'axes.spines.right': False,
    'grid.color': GRID, 'grid.linewidth': 0.8,
    'axes.axisbelow': True, 'font.size': 11,
})

WEEK_KO = {'Monday': '월', 'Tuesday': '화', 'Wednesday': '수', 'Thursday': '목',
           'Friday': '금', 'Saturday': '토', 'Sunday': '일'}
WEEK_ORDER = ['월', '화', '수', '목', '금', '토', '일']
AGE_ORDER = ['18-24', '25-34', '35-44', '45-54', '55-64', '65-74']


def load(clean=True):
    df = pd.read_excel(SRC, sheet_name='RAW')
    df.insert(0, 'trip_id', range(1, len(df) + 1))
    if clean:
        # 1) Weekday 정렬용 숫자 접두사 제거 -> 한글 요일
        df['Weekday'] = (df['Weekday'].str.replace(r'^\d', '', regex=True)
                                      .map(WEEK_KO))
        df['Weekday'] = pd.Categorical(df['Weekday'], WEEK_ORDER, ordered=True)
        # 2) 정비소 이동 기록 제외 (이용자 대여가 아님)
        df = df[df['End Station Name'] != 'JCBS Depot'].copy()
        # 3) 연령대 순서 고정
        df['Age Groups'] = pd.Categorical(df['Age Groups'], AGE_ORDER, ordered=True)
        # 4) 분석용 별칭
        df['dur_sec'] = df['Trip Duration_초']
        df['dur_min'] = df['dur_sec'] / 60
    return df


def barstyle(ax, bars, color=BLUE):
    """막대 사이 2px 여백 + 얇은 마크"""
    for b in bars:
        b.set_facecolor(color)
        b.set_edgecolor(SURFACE)
        b.set_linewidth(2)
    ax.grid(axis='y')
    ax.tick_params(length=0)
