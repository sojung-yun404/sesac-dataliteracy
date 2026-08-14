"""차트 ④ 정정 - 비율 막대를 양으로 오해하지 않기"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eda_common import BLUE, INK2, ORANGE, SURFACE, load

RED = '#e34948'
df = load()
df['주말'] = df['Weekday'].isin(['토', '일'])
O = df[df['User Type'] == 'One-time user']

tot = df['Start Station Name'].value_counts()
ov = O['Start Station Name'].value_counts()
r = pd.DataFrame({'총': tot, '일회': ov}).fillna(0).astype(int)
r['정기'] = r['총'] - r['일회']
r = r[r['총'] >= 50]
r['일회%'] = r['일회'] / r['총'] * 100

pick = pd.concat([r.nlargest(6, '일회%'), r.nlargest(4, '총')])
pick = pick[~pick.index.duplicated()].sort_values('총')

fig, axes = plt.subplots(1, 3, figsize=(17, 6.2))
fig.suptitle('차트 ④ 정정 — 비율 막대는 "양"이 아니다', fontsize=15,
             fontweight='bold', y=0.98)

# ── ① 비율 (원래 보여드린 것) ────────────────────────────────────
ax = axes[0]
y = np.arange(len(pick))
bars = ax.barh(y, pick['일회%'], 0.72)
for b in bars:
    b.set_facecolor(ORANGE); b.set_edgecolor(SURFACE); b.set_linewidth(2)
ax.set_yticks(y); ax.set_yticklabels(pick.index, fontsize=9.5)
for yi, v in zip(y, pick['일회%']):
    ax.text(v + .2, yi, f'{v:.1f}%', va='center', fontsize=9, color=INK2)
ax.set_xlim(0, 14); ax.set_xlabel('일회 이용자 비율 (%)')
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('① 비율로 보면\nLiberty가 제일 길다', fontsize=12, loc='left')

# ── ② 같은 역, 절대 건수 ─────────────────────────────────────────
ax = axes[1]
b1 = ax.barh(y, pick['정기'], 0.72, label='Subscriber')
b2 = ax.barh(y, pick['일회'], 0.72, left=pick['정기'], label='One-time user')
for b, c in [(b1, BLUE), (b2, ORANGE)]:
    for rr in b:
        rr.set_facecolor(c); rr.set_edgecolor(SURFACE); rr.set_linewidth(2)
ax.set_yticks(y); ax.set_yticklabels(pick.index, fontsize=9.5)
for yi, v in zip(y, pick['총']):
    ax.text(v + 25, yi, f'{v:,}', va='center', fontsize=9, color=INK2)
ax.set_xlim(0, 1950); ax.set_xlabel('출발 건수')
ax.legend(frameon=False, loc='lower right')
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('② 양으로 보면\n순서가 완전히 뒤집힌다', fontsize=12, loc='left')

# ── ③ Liberty Light Rail 뜯어보기 ────────────────────────────────
ax = axes[2]
L = df[df['Start Station Name'] == 'Liberty Light Rail']
ct = pd.crosstab(L['주말'], L['User Type']).reindex([False, True])
x = np.arange(2); w = 0.38
b1 = ax.bar(x - w/2, ct['Subscriber'], w, label='Subscriber')
b2 = ax.bar(x + w/2, ct['One-time user'], w, label='One-time user')
for b, c in [(b1, BLUE), (b2, ORANGE)]:
    for rr in b:
        rr.set_facecolor(c); rr.set_edgecolor(SURFACE); rr.set_linewidth(2)
for xi, v in zip(x - w/2, ct['Subscriber']):
    ax.text(xi, v + 4, f'{v}', ha='center', fontsize=10, color=INK2)
for xi, v in zip(x + w/2, ct['One-time user']):
    ax.text(xi, v + 4, f'{v}', ha='center', fontsize=10, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(['평일', '주말'])
ax.set_ylim(0, 205); ax.set_ylabel('건수')
ax.legend(frameon=False, loc='upper right')
ax.grid(axis='y'); ax.tick_params(length=0)
ax.text(0.5, 130, '가장 "관광형"인 역조차\n241건 중 214건(88.8%)이\n정기구독자이고,\n평일이 주말의 3배',
        ha='center', fontsize=10.5, color=RED)
ax.set_title('③ 가장 관광형인 Liberty도\n실은 통근역이다', fontsize=12, loc='left')

fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig('fig_07_correction.png', dpi=130)
print('저장: fig_07_correction.png')
