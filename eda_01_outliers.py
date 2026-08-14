"""EDA 1단계 - trip_id 부여 + 이상치/정합성 점검"""
import pandas as pd

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)

SRC = '1.2 EDA_뉴욕 따릉이_Level2_문제 .xlsx'


def load():
    df = pd.read_excel(SRC, sheet_name='RAW')
    df.insert(0, 'trip_id', range(1, len(df) + 1))   # 임시 일련번호
    return df


def sec(title):
    print(f'\n{"="*70}\n{title}\n{"="*70}')


df = load()
print('shape:', df.shape, '| trip_id 고유값:', df['trip_id'].nunique())

# ── 1. Age / Birth Year ──────────────────────────────────────────
sec('1. Age / Birth Year')
print(df[['Birth Year', 'Age']].describe().to_string())
print('\nAge != 2023 - Birth Year 인 행:',
      (df['Age'] != 2023 - df['Birth Year']).sum())
print('Age 최소/최대:', df['Age'].min(), '/', df['Age'].max())
print('\nAge Groups 별 실제 Age 범위 (구간 정의와 맞는지)')
print(df.groupby('Age Groups')['Age'].agg(['min', 'max', 'count']).to_string())

# ── 2. Trip Duration ─────────────────────────────────────────────
sec('2. Trip Duration')
d = df['Trip Duration_초']
print(d.describe(percentiles=[.01, .25, .5, .75, .95, .99, .999]).to_string())
print('\n0초 이하:', (d <= 0).sum())
print('60초 미만:', (d < 60).sum())
print('1시간 초과:', (d > 3600).sum())
print('24시간 초과:', (d > 86400).sum())

q1, q3 = d.quantile([.25, .75])
iqr = q3 - q1
hi = q3 + 1.5 * iqr
print(f'\nIQR 상한: {hi:.0f}초 ({hi/60:.1f}분) -> 초과 {(d > hi).sum()}건 '
      f'({(d > hi).mean()*100:.1f}%)')

print('\n분 단위 컬럼과 정합성 (초/60 반올림 != 분 인 행):',
      (d.div(60).round().astype(int) != df['Trip_Duration_in_min']).sum())
print('내림으로 계산했을 때 불일치:',
      (d.floordiv(60) != df['Trip_Duration_in_min']).sum())

print('\n상위 10건')
print(df.nlargest(10, 'Trip Duration_초')[
    ['trip_id', 'Start Station Name', 'End Station Name',
     'Trip Duration_초', 'Trip_Duration_in_min', 'Age', 'User Type']].to_string(index=False))

print('\n하위 10건')
print(df.nsmallest(10, 'Trip Duration_초')[
    ['trip_id', 'Start Station Name', 'End Station Name',
     'Trip Duration_초', 'Trip_Duration_in_min', 'Age', 'User Type']].to_string(index=False))

# ── 3. 왕복(출발역=도착역) ───────────────────────────────────────
sec('3. 출발역 == 도착역')
rt = df['Start Station ID'] == df['End Station ID']
print('왕복 건수:', rt.sum(), f'({rt.mean()*100:.1f}%)')
print('\n왕복 건의 소요시간 분포')
print(df.loc[rt, 'Trip Duration_초'].describe().to_string())
print('\n왕복 & 60초 미만 (대여 실패 의심):', (rt & (d < 60)).sum())

# ── 4. Weekday 정합성 ────────────────────────────────────────────
sec('4. Weekday 컬럼 vs 실제 날짜')
actual = df['Start Time'].dt.day_name()
clean = df['Weekday'].str.replace(r'^\d', '', regex=True)
print('원본 Weekday 값:', sorted(df['Weekday'].unique()))
print('불일치 행 수:', (actual != clean).sum())
print('\n요일별 건수 (실제 날짜 기준)')
print(actual.value_counts().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
     'Saturday', 'Sunday']).to_string())

# ── 5. Season / Month / Temperature ─────────────────────────────
sec('5. Season / Month / Temperature')
print(pd.crosstab(df['Month'], df['Season']).to_string())
print('\nTemperature_화씨 고유값:', sorted(df['Temperature_화씨'].unique()))
print('섭씨 환산:', [round((f-32)*5/9, 1) for f in sorted(df['Temperature_화씨'].unique())])
print('\n같은 날짜에 온도가 여러 개인 날:',
      (df.groupby('Start Time')['Temperature_화씨'].nunique() > 1).sum())
print('날짜별 온도 (앞 15일)')
print(df.groupby('Start Time')['Temperature_화씨'].agg(['min', 'max', 'count']).head(15).to_string())

# ── 6. 역 ID ↔ 이름 매핑 ─────────────────────────────────────────
sec('6. 역 ID <-> 이름 정합성')
s = df.groupby('Start Station ID')['Start Station Name'].nunique()
e = df.groupby('End Station ID')['End Station Name'].nunique()
print('출발역 ID 하나에 이름이 2개 이상:', (s > 1).sum())
print('도착역 ID 하나에 이름이 2개 이상:', (e > 1).sum())
start_ids = set(df['Start Station ID'])
end_ids = set(df['End Station ID'])
print('\n출발역으로만 등장:', sorted(start_ids - end_ids))
only_end = sorted(end_ids - start_ids)
print('도착역으로만 등장:', only_end)
if only_end:
    print(df[df['End Station ID'].isin(only_end)]
          .groupby(['End Station ID', 'End Station Name']).size()
          .rename('건수').to_string())

# ── 7. Stop Time ────────────────────────────────────────────────
sec('7. Stop Time')
print('Stop < Start 인 행:', (df['Stop Time'] < df['Start Time']).sum())
print('Stop != Start (날짜 넘어간 대여):', (df['Stop Time'] != df['Start Time']).sum())
