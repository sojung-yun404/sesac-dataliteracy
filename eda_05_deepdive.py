"""EDA 6단계 - 심화 3제
   1) 주말 Subscriber의 정체  2) 연령대 x 사용자유형  3) 연령대 x 주말비중
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eda_common import (AGE_ORDER, BLUE, INK2, ORANGE, SURFACE, WEEK_ORDER,
                        barstyle, load)

RED = '#e34948'
df = load()
df['주말'] = df['Weekday'].isin(['토', '일'])
sub = df[df['User Type'] == 'Subscriber']
one = df[df['User Type'] == 'One-time user']

fig, axes = plt.subplots(2, 3, figsize=(17, 9.8))
fig.suptitle('심화 분석 — 주말 정기구독자 / 연령대 교차', fontsize=16,
             fontweight='bold', y=0.975)

# ══ ① Subscriber 요일별 대여시간 중앙값 ════════════════════════
ax = axes[0, 0]
m = (sub.groupby('Weekday', observed=True)['dur_sec'].median() / 60).reindex(WEEK_ORDER)
bars = ax.bar(np.arange(7), m.values)
barstyle(ax, bars)
for b, d in zip(bars, WEEK_ORDER):
    if d in ('토', '일'):
        b.set_facecolor(ORANGE)
for xi, v in zip(np.arange(7), m.values):
    ax.text(xi, v + .08, f'{v:.2f}', ha='center', fontsize=9.5, color=INK2)
ax.set_xticks(np.arange(7)); ax.set_xticklabels(WEEK_ORDER)
ax.set_ylim(0, 6.6); ax.set_ylabel('중앙값 (분)')
ax.set_title('① 정기구독자 대여시간 — 주말도 거의 그대로 (+7.9%)',
             fontsize=12, loc='left')

# ══ ② Subscriber 평일 vs 주말 : 레저 신호 ══════════════════════
ax = axes[0, 1]
met = pd.DataFrame({
    '평일': [(sub[~sub['주말']]['dur_sec'] > 1800).mean() * 100,
             (sub[~sub['주말']]['Start Station ID'] ==
              sub[~sub['주말']]['End Station ID']).mean() * 100],
    '주말': [(sub[sub['주말']]['dur_sec'] > 1800).mean() * 100,
             (sub[sub['주말']]['Start Station ID'] ==
              sub[sub['주말']]['End Station ID']).mean() * 100]},
    index=['30분 초과 비율', '왕복(출발=도착) 비율'])
x = np.arange(2); w = 0.38
b1 = ax.bar(x - w/2, met['평일'], w, label='평일')
b2 = ax.bar(x + w/2, met['주말'], w, label='주말')
barstyle(ax, b1, BLUE); barstyle(ax, b2, ORANGE)
for xi, v in zip(x - w/2, met['평일']):
    ax.text(xi, v + .08, f'{v:.2f}%', ha='center', fontsize=9.5, color=INK2)
for xi, v in zip(x + w/2, met['주말']):
    ax.text(xi, v + .08, f'{v:.2f}%', ha='center', fontsize=9.5, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(met.index)
ax.set_ylim(0, 5.2); ax.set_ylabel('%')
ax.legend(frameon=False, loc='upper left')
ax.set_title('② 다만 레저형 신호는 2배 이상 늘어남', fontsize=12, loc='left')

# ══ ③ One-time user 나이 분포 — 결정적 발견 ═══════════════════
ax = axes[0, 2]
v = one['Age'].value_counts().sort_index()
bars = ax.bar(v.index.astype(str), v.values)
barstyle(ax, bars, RED)
for xi, val in zip(range(len(v)), v.values):
    ax.text(xi, val + 5, f'{val}건', ha='center', fontsize=10, color=INK2)
ax.set_xlabel('나이'); ax.set_ylabel('건수'); ax.set_ylim(0, 285)
ax.text(0.03, 0.72, '250건 중 248건(99.2%)이\n똑같이 1986년생(37세)\n\n→ 실제 나이가 아니라\n   결측값을 최빈값으로\n   채운 흔적',
        transform=ax.transAxes, fontsize=10.5, color=RED, va='top')
ax.set_title('③ 일회 이용자의 나이는 가짜다', fontsize=12, loc='left')

# ══ ④ 연령대 × 사용자유형 구성 ════════════════════════════════
ax = axes[1, 0]
ct = pd.crosstab(df['Age Groups'], df['User Type'])
pct = ct.div(ct.sum(axis=0), axis=1) * 100
x6 = np.arange(6)
b1 = ax.bar(x6 - w/2, pct['Subscriber'], w, label='Subscriber')
b2 = ax.bar(x6 + w/2, pct['One-time user'], w, label='One-time user')
barstyle(ax, b1, BLUE); barstyle(ax, b2, ORANGE)
for xi, val in zip(x6 - w/2, pct['Subscriber']):
    ax.text(xi, val + 1.5, f'{val:.0f}', ha='center', fontsize=9, color=INK2)
for xi, val in zip(x6 + w/2, pct['One-time user']):
    ax.text(xi, val + 1.5, f'{val:.0f}', ha='center', fontsize=9, color=INK2)
ax.set_xticks(x6); ax.set_xticklabels(AGE_ORDER)
ax.set_ylim(0, 112); ax.set_ylabel('그룹 내 구성비 (%)')
ax.legend(frameon=False, loc='upper left')
ax.set_title('④ 그 결과 — 일회 이용자가 한 칸에 몰림', fontsize=12, loc='left')

# ══ ⑤ 연령대별 주말 비중 ══════════════════════════════════════
ax = axes[1, 1]
t = sub.groupby('Age Groups', observed=True)['주말'].mean() * 100
bars = ax.bar(x6, t.values)
barstyle(ax, bars)
base = sub['주말'].mean() * 100
ax.axhline(base, color=RED, lw=2, ls='--')
ax.text(5.4, base + .5, f'전체 평균 {base:.1f}%', ha='right', fontsize=10, color=RED)
for xi, val in zip(x6, t.values):
    ax.text(xi, val + .4, f'{val:.1f}', ha='center', fontsize=9.5, color=INK2)
ax.set_xticks(x6); ax.set_xticklabels(AGE_ORDER)
ax.set_ylim(0, 27); ax.set_ylabel('주말 비중 (%)')
ax.set_title('⑤ 정기구독자 연령대별 주말 비중', fontsize=12, loc='left')

# ══ ⑥ 문제2 수정 — 오염 제거 전후 ═════════════════════════════
ax = axes[1, 2]
a = df.groupby('Age Groups', observed=True)['dur_sec'].mean() / 60
b = sub.groupby('Age Groups', observed=True)['dur_sec'].mean() / 60
b1 = ax.bar(x6 - w/2, a.values, w, label='전체 (오염됨)')
b2 = ax.bar(x6 + w/2, b.values, w, label='Subscriber만')
barstyle(ax, b1, ORANGE); barstyle(ax, b2, BLUE)
for xi, val in zip(x6 - w/2, a.values):
    ax.text(xi, val + .2, f'{val:.1f}', ha='center', fontsize=9, color=INK2)
for xi, val in zip(x6 + w/2, b.values):
    ax.text(xi, val + .2, f'{val:.1f}', ha='center', fontsize=9, color=INK2)
ax.annotate('8.8 → 7.5분', xy=(2.2, 8.9), xytext=(2.6, 11.6), fontsize=10,
            color=RED, arrowprops=dict(arrowstyle='->', color=RED, lw=1.3))
ax.set_xticks(x6); ax.set_xticklabels(AGE_ORDER)
ax.set_ylim(0, 14); ax.set_ylabel('평균 (분)')
ax.legend(frameon=False, loc='upper right')
ax.set_title('⑥ [문제2 수정] 35-44 평균이 부풀려져 있었다',
             fontsize=12, loc='left')

fig.tight_layout(rect=[0, 0, 1, 0.955])
fig.savefig('fig_05_deepdive.png', dpi=130)
print('저장: fig_05_deepdive.png')
