"""리포트용 차트 - 한 장에 메시지 하나. 리포트와 같은 색/폰트를 쓴다."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eda_common import load

# ── 리포트 토큰과 동일 ───────────────────────────────────────────
BLUE, ORANGE, SLATE = '#2a78d6', '#d9541f', '#5d7387'
CARD, INK, INK2, INK3, RULE = '#ffffff', '#0f151c', '#465565', '#75859a', '#d0d9e2'

plt.rcParams.update({
    'font.family': 'Apple SD Gothic Neo',
    'axes.unicode_minus': False,
    'figure.facecolor': CARD, 'axes.facecolor': CARD,
    'axes.edgecolor': RULE, 'axes.labelcolor': INK2,
    'text.color': INK, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.spines.left': False,
    'grid.color': RULE, 'grid.linewidth': 0.7,
    'axes.axisbelow': True, 'font.size': 12.5,
})


def title(fig, text, sub=None, top=0.855):
    """그림 왼쪽 끝에 맞춘 제목 — 4장 모두 같은 위치."""
    fig.text(0.011, 0.972, text, fontsize=15.5, fontweight='600',
             color=INK, va='top')
    if sub:
        fig.text(0.011, 0.905, sub, fontsize=12, color=INK3, va='top')
    fig.tight_layout(rect=[0, 0, 1, top])


df = load()
df['주말'] = df['Weekday'].isin(['토', '일'])
S = df[df['User Type'] == 'Subscriber']
O = df[df['User Type'] == 'One-time user']

# ══════════════════════════════════════════════════════════════
# 그림 1 — 대여시간 분포
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 5.2))
bins = np.linspace(np.log10(60), np.log10(7200), 29)
for name, d, c in [('정기구독자', S, BLUE), ('일회 이용자', O, ORANGE)]:
    v = d.loc[d['dur_sec'] <= 7200, 'dur_sec']      # 클리핑 아님 — 2시간 초과는 제외
    ax.hist(np.log10(v), bins=bins, density=True,
            color=c, alpha=.55, label=f'{name} ({len(d):,}건)')
for d, c, lab, dy in [(S, BLUE, '5.2분', .93), (O, ORANGE, '20.3분', .78)]:
    m = np.log10(d['dur_sec'].median())
    ax.axvline(m, color=c, lw=2.2, ls=(0, (5, 3)))
    ax.text(m + .035, ax.get_ylim()[1]*dy, f'중앙값 {lab}', color=c,
            fontsize=12.5, fontweight='600')
ax.set_xticks([np.log10(v) for v in [60, 180, 300, 600, 1200, 3600, 7200]])
ax.set_xticklabels(['1분', '3분', '5분', '10분', '20분', '1시간', '2시간'])
ax.set_yticks([])
ax.set_xlabel('대여시간 (로그 간격)', fontsize=12, labelpad=10)
ax.legend(frameon=False, fontsize=12.5, loc='upper right')
ax.grid(axis='x')
ax.tick_params(length=0)
title(fig, '두 그룹은 애초에 다른 길이의 이동을 한다',
      '대여시간 중앙값 — 정기구독자 5.2분, 일회 이용자 20.3분 · '
      '막대 높이는 각 그룹 내 비율 · 2시간 초과 제외', top=0.845)
fig.savefig('rf_1_duration.png', dpi=118)
print('rf_1_duration.png')

# ══════════════════════════════════════════════════════════════
# 그림 2 — 평일 → 주말 출발역 이동 (덤벨)
# ══════════════════════════════════════════════════════════════
wd = S[~S['주말']]['Start Station Name'].value_counts(normalize=True)*100
we = S[S['주말']]['Start Station Name'].value_counts(normalize=True)*100
k = pd.DataFrame({'평일': wd, '주말': we}).fillna(0)
k['차'] = k['주말'] - k['평일']
k = k[k['평일'] >= 1.5]
pick = pd.concat([k.nlargest(5, '차'), k.nsmallest(5, '차')]).sort_values('차')

TAG = {'Exchange Place': '환승역', 'Newport PATH': '환승역',
       'Grove St PATH': '환승역', 'Sip Ave': '경전철역',
       'Newark Ave': '상점가', 'Van Vorst Park': '공원',
       'Warren St': '다운타운', 'Jersey & 3rd': '주거지',
       'Dixon Mills': '주거지', 'Essex Light Rail': '경전철역',
       'Hamilton Park': '공원'}

fig, ax = plt.subplots(figsize=(13, 6.2))
y = np.arange(len(pick))
for yi, (name, r) in zip(y, pick.iterrows()):
    up = r['차'] > 0
    ax.plot([r['평일'], r['주말']], [yi, yi], color=RULE, lw=2.5, zorder=1)
    ax.scatter(r['평일'], yi, s=110, color=SLATE, zorder=2,
               edgecolor=CARD, linewidth=2)
    ax.scatter(r['주말'], yi, s=140, color=ORANGE if up else BLUE, zorder=3,
               edgecolor=CARD, linewidth=2)
    ax.text(max(r['평일'], r['주말']) + .22, yi, f"{r['차']:+.2f}%p",
            va='center', fontsize=11.5, color=ORANGE if up else BLUE,
            fontweight='600')
labels = [f'{n}  ·{TAG.get(n, "")}' if TAG.get(n) else n for n in pick.index]
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=12.5)
ax.set_xlim(0, 15.2)
ax.set_xlabel('정기구독자 출발 비중 (%)', fontsize=12, labelpad=10)
ax.scatter([], [], s=110, color=SLATE, label='평일')
ax.scatter([], [], s=140, color=ORANGE, label='주말 — 올라감')
ax.scatter([], [], s=140, color=BLUE, label='주말 — 내려감')
ax.legend(frameon=False, fontsize=12.5, loc='upper right', scatterpoints=1)
ax.grid(axis='x'); ax.tick_params(length=0)
title(fig, '주말엔 환승역이 내려가고 동네 거리가 올라온다',
      '같은 정기구독자인데도 출발역 구성이 바뀐다 · 평일 비중 1.5% 이상인 역',
      top=0.875)
fig.savefig('rf_2_weekend_shift.png', dpi=118)
print('rf_2_weekend_shift.png')

# ══════════════════════════════════════════════════════════════
# 그림 3 — 비율 vs 절대량
# ══════════════════════════════════════════════════════════════
tot = df['Start Station Name'].value_counts()
ov = O['Start Station Name'].value_counts()
r = pd.DataFrame({'총': tot, '일회': ov}).fillna(0).astype(int)
r['정기'] = r['총'] - r['일회']
r = r[r['총'] >= 50]
r['비율'] = r['일회'] / r['총'] * 100
pick = pd.concat([r.nlargest(5, '비율'), r.nlargest(4, '총')])
pick = pick[~pick.index.duplicated()].sort_values('총')

fig, axes = plt.subplots(1, 2, figsize=(13.6, 5.4))
y = np.arange(len(pick))

ax = axes[0]
ax.barh(y, pick['비율'], .66, color=ORANGE, edgecolor=CARD, linewidth=2)
for yi, v in zip(y, pick['비율']):
    ax.text(v + .25, yi, f'{v:.1f}%', va='center', fontsize=11.5, color=INK2)
ax.set_yticks(y); ax.set_yticklabels(pick.index, fontsize=12)
ax.set_xlim(0, 14.5)
ax.set_xlabel('일회 이용자 비율 (%)', fontsize=12, labelpad=8)
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('비율로 보면  Liberty가 1위', fontsize=14, fontweight='600',
             loc='left', color=INK, pad=12)

ax = axes[1]
ax.barh(y, pick['정기'], .66, color=BLUE, edgecolor=CARD, linewidth=2,
        label='정기구독자')
ax.barh(y, pick['일회'], .66, left=pick['정기'], color=ORANGE,
        edgecolor=CARD, linewidth=2, label='일회 이용자')
for yi, v in zip(y, pick['총']):
    ax.text(v + 30, yi, f'{v:,}', va='center', fontsize=11.5, color=INK2)
ax.set_yticks(y); ax.set_yticklabels(pick.index, fontsize=12)
ax.set_xlim(0, 2000)
ax.set_xlabel('출발 건수', fontsize=12, labelpad=8)
ax.legend(frameon=False, fontsize=12, loc='lower right')
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('양으로 보면  순서가 뒤집힌다', fontsize=14, fontweight='600',
             loc='left', color=INK, pad=12)

title(fig, '일회 이용자 비율이 가장 높은 역도, 이용의 88.8%는 정기구독자다',
      '비율은 어디에 씨앗이 있는지를, 절대량은 어디가 큰지를 말한다', top=0.845)
fig.savefig('rf_3_ratio_vs_volume.png', dpi=118)
print('rf_3_ratio_vs_volume.png')

# ══════════════════════════════════════════════════════════════
# 그림 4 — 기온 × 대여건수
# ══════════════════════════════════════════════════════════════
daily = df.groupby('Start Time').agg(건수=('trip_id', 'count'),
                                     기온=('Temperature_화씨', 'first'))
daily['주말'] = daily.index.dayofweek >= 5
daily['순번'] = np.arange(len(daily))

fig, ax = plt.subplots(figsize=(12.2, 5.4))
for lab, sub, c in [('평일', daily[~daily['주말']], BLUE),
                    ('주말', daily[daily['주말']], ORANGE)]:
    ax.scatter(sub['기온'], sub['건수'], s=62, color=c, alpha=.72,
               edgecolor=CARD, linewidth=1.6, label=lab)
    z = np.polyfit(sub['기온'], sub['건수'], 1)
    xs = np.linspace(sub['기온'].min(), sub['기온'].max(), 10)
    ax.plot(xs, np.poly1d(z)(xs), color=c, lw=2.4, ls=(0, (5, 3)))
    rr = sub['건수'].corr(sub['기온'])
    ax.text(.022, .95 if lab == '평일' else .875, f'{lab}   r = {rr:+.3f}',
            transform=ax.transAxes, color=c, fontsize=13, fontweight='600')


def resid(v, x):
    return v - np.poly1d(np.polyfit(x, v, 1))(x)


pr = np.corrcoef(resid(daily['기온'].values, daily['순번'].values),
                 resid(daily['건수'].values, daily['순번'].values))[0, 1]
ax.text(.022, .80, f'날짜 추세 제거 후   r = {pr:+.3f}', transform=ax.transAxes,
        color=INK2, fontsize=13, fontweight='600')
ax.set_xlabel('기온 (단위 불명 — 상대값)', fontsize=12, labelpad=10)
ax.set_ylabel('일별 대여 건수', fontsize=12, labelpad=10)
ax.legend(frameon=False, fontsize=12.5, loc='lower right')
ax.grid(); ax.tick_params(length=0)
title(fig, '기온 효과는 실은 계절이 흘러간 흔적이다',
      '평일과 주말의 방향이 반대이고, 날짜 추세를 통제하면 상관이 사라진다 · 75일',
      top=0.845)
fig.savefig('rf_4_temperature.png', dpi=118)
print('rf_4_temperature.png')
