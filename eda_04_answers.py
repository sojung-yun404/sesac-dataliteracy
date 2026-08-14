"""EDA 5단계 - 문제 1~4번 답안"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eda_common import (AGE_ORDER, BLUE, INK2, ORANGE, SURFACE, WEEK_ORDER,
                        barstyle, load)

RED = '#e34948'          # 다이버징 반대 극
df = load()
df['주말'] = df['Weekday'].isin(['토', '일'])

# ── 역 집계 ──────────────────────────────────────────────────────
s = df['Start Station Name'].value_counts().rename('출발')
e = df['End Station Name'].value_counts().rename('도착')
st = pd.concat([s, e], axis=1).fillna(0).astype(int)
st['총이용'] = st['출발'] + st['도착']
st['순유입'] = st['도착'] - st['출발']
st = st.sort_values('총이용', ascending=False)

fig, axes = plt.subplots(2, 3, figsize=(17, 10))
fig.suptitle('문제 1~4번 답안', fontsize=16, fontweight='bold', y=0.975)

# ══ ① 문제1 : 가장 인기 있는 장소 ══════════════════════════════
ax = axes[0, 0]
top = st.head(12).iloc[::-1]
y = np.arange(len(top))
b1 = ax.barh(y, top['출발'], 0.72, label='출발')
b2 = ax.barh(y, top['도착'], 0.72, left=top['출발'], label='도착')
for b, c in [(b1, BLUE), (b2, ORANGE)]:
    for r in b:
        r.set_facecolor(c); r.set_edgecolor(SURFACE); r.set_linewidth(2)
ax.set_yticks(y); ax.set_yticklabels(top.index, fontsize=9.5)
for yi, v in zip(y, top['총이용']):
    ax.text(v + 60, yi, f'{v:,}', va='center', fontsize=9, color=INK2)
ax.set_xlim(0, 4500); ax.set_xlabel('건수 (출발+도착)')
ax.legend(frameon=False, loc='lower right')
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('① [문제1] 역별 총 이용량 TOP 12', fontsize=12, loc='left')

# ══ ② 문제1 심화 : 순유입 / 순유출 ════════════════════════════
ax = axes[0, 1]
flow = pd.concat([st.nlargest(5, '순유입')['순유입'],
                  st.nsmallest(5, '순유입')['순유입']]).sort_values()
y = np.arange(len(flow))
bars = ax.barh(y, flow.values, 0.72)
for r, v in zip(bars, flow.values):
    r.set_facecolor(BLUE if v > 0 else RED)
    r.set_edgecolor(SURFACE); r.set_linewidth(2)
ax.set_yticks(y); ax.set_yticklabels(flow.index, fontsize=9.5)
for yi, v in zip(y, flow.values):
    ax.text(v + (20 if v > 0 else -20), yi, f'{v:+,}', va='center',
            ha='left' if v > 0 else 'right', fontsize=9, color=INK2)
ax.axvline(0, color=INK2, lw=1)
ax.set_xlim(-260, 660); ax.set_xlabel('도착 - 출발 (건)')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor=BLUE, label='자전거가 쌓임 → 회수 필요'),
                   Patch(facecolor=RED, label='자전거가 마름 → 공급 필요')],
          frameon=False, loc='lower right', fontsize=9.5)
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('② [문제1 심화] 재배치가 필요한 역', fontsize=12, loc='left')

# ══ ③ 사용자유형별 출발역 ═════════════════════════════════════
ax = axes[0, 2]
sub = df[df['User Type'] == 'Subscriber']['Start Station Name'].value_counts(normalize=True) * 100
one = df[df['User Type'] == 'One-time user']['Start Station Name'].value_counts(normalize=True) * 100
names = list(dict.fromkeys(list(sub.head(5).index) + list(one.head(5).index)))[::-1]
y = np.arange(len(names)); h = 0.38
b1 = ax.barh(y + h/2, [sub.get(n, 0) for n in names], h, label='Subscriber')
b2 = ax.barh(y - h/2, [one.get(n, 0) for n in names], h, label='One-time user')
for b, c in [(b1, BLUE), (b2, ORANGE)]:
    for r in b:
        r.set_facecolor(c); r.set_edgecolor(SURFACE); r.set_linewidth(2)
ax.set_yticks(y); ax.set_yticklabels(names, fontsize=9.5)
ax.set_xlabel('그룹 내 출발 비중 (%)')
ax.legend(frameon=False, loc='lower right')
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('③ [보너스] 두 그룹은 아예 다른 역에서 탄다', fontsize=12, loc='left')

# ══ ④ 문제2 : 연령대별 대여시간 ═══════════════════════════════
ax = axes[1, 0]
g = df.groupby('Age Groups', observed=True)['dur_sec'].agg(['mean', 'median']) / 60
x = np.arange(6); w = 0.38
b1 = ax.bar(x - w/2, g['mean'], w, label='평균')
b2 = ax.bar(x + w/2, g['median'], w, label='중앙값')
barstyle(ax, b1, BLUE); barstyle(ax, b2, ORANGE)
for xi, v in zip(x - w/2, g['mean']):
    ax.text(xi, v + .2, f'{v:.1f}', ha='center', fontsize=9, color=INK2)
for xi, v in zip(x + w/2, g['median']):
    ax.text(xi, v + .2, f'{v:.1f}', ha='center', fontsize=9, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(AGE_ORDER)
ax.set_ylim(0, 14); ax.set_ylabel('분')
ax.legend(frameon=False, loc='upper right')
ax.annotate('표본 43건\n신뢰 어려움', xy=(0, 12.3), xytext=(0.55, 12.6),
            fontsize=9, color=RED,
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
ax.set_title('④ [문제2] 연령대별 대여시간', fontsize=12, loc='left')

# ══ ⑤ 문제3 : 연령대별 건수 ═══════════════════════════════════
ax = axes[1, 1]
c = df['Age Groups'].value_counts().reindex(AGE_ORDER)
bars = ax.bar(np.arange(6), c.values)
barstyle(ax, bars)
bars[2].set_facecolor(ORANGE)
for xi, v in zip(np.arange(6), c.values):
    ax.text(xi, v + 90, f'{v:,}\n({v/c.sum()*100:.1f}%)', ha='center',
            fontsize=9, color=INK2)
ax.set_xticks(np.arange(6)); ax.set_xticklabels(AGE_ORDER)
ax.set_ylim(0, 7600); ax.set_ylabel('대여 건수')
ax.set_title('⑤ [문제3] 연령대별 대여 건수', fontsize=12, loc='left')

# ══ ⑥ 문제4 : 요일 × 사용자유형 ═══════════════════════════════
ax = axes[1, 2]
ct = pd.crosstab(df['Weekday'], df['User Type']).reindex(WEEK_ORDER)
pct = ct.div(ct.sum(axis=0), axis=1) * 100
x7 = np.arange(7)
b1 = ax.bar(x7 - w/2, pct['Subscriber'], w, label='Subscriber')
b2 = ax.bar(x7 + w/2, pct['One-time user'], w, label='One-time user')
barstyle(ax, b1, BLUE); barstyle(ax, b2, ORANGE)
for xi, v in zip(x7 - w/2, pct['Subscriber']):
    ax.text(xi, v + .4, f'{v:.0f}', ha='center', fontsize=9, color=INK2)
for xi, v in zip(x7 + w/2, pct['One-time user']):
    ax.text(xi, v + .4, f'{v:.0f}', ha='center', fontsize=9, color=INK2)
ax.axvspan(4.5, 6.5, color=ORANGE, alpha=.07, zorder=0)
ax.text(5.5, 25.6, '주말', ha='center', fontsize=10, color=ORANGE)
ax.set_xticks(x7); ax.set_xticklabels(WEEK_ORDER)
ax.set_ylabel('그룹 내 비중 (%)'); ax.set_ylim(0, 28)
ax.legend(frameon=False, loc='upper left')
ax.set_title('⑥ [문제4] 요일별 사용자그룹 비교 (비율)', fontsize=12, loc='left')

fig.tight_layout(rect=[0, 0, 1, 0.955])
fig.savefig('fig_04_answers.png', dpi=130)
print('저장: fig_04_answers.png')
