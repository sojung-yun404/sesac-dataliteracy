"""EDA 7단계 - 정기구독자 vs 일회 이용자 종합 프로파일"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eda_common import (BLUE, INK2, ORANGE, SURFACE, WEEK_ORDER, barstyle, load)

RED = '#e34948'
df = load()
df['주말'] = df['Weekday'].isin(['토', '일'])
S = df[df['User Type'] == 'Subscriber']
O = df[df['User Type'] == 'One-time user']
WD_DAYS, WE_DAYS = 52, 23          # 실제 기간의 평일/주말 일수

fig, axes = plt.subplots(2, 3, figsize=(17, 9.8))
fig.suptitle('정기구독자 vs 일회 이용자 — 종합 프로파일', fontsize=16,
             fontweight='bold', y=0.975)

# ══ ① 일당 이용건수 : 방향이 반대 ══════════════════════════════
ax = axes[0, 0]
rate = pd.DataFrame({
    '평일': [(~S['주말']).sum()/WD_DAYS, (~O['주말']).sum()/WD_DAYS],
    '주말': [S['주말'].sum()/WE_DAYS,    O['주말'].sum()/WE_DAYS]},
    index=['Subscriber', 'One-time user'])
x = np.arange(2); w = 0.38
b1 = ax.bar(x - w/2, rate['평일'], w, label='평일')
b2 = ax.bar(x + w/2, rate['주말'], w, label='주말')
barstyle(ax, b1, BLUE); barstyle(ax, b2, ORANGE)
ax.set_yscale('log'); ax.set_ylim(1, 800)
ax.set_yticks([1, 10, 100, 500]); ax.set_yticklabels(['1', '10', '100', '500'])
ax.minorticks_off()
for xi, v in zip(x - w/2, rate['평일']):
    ax.text(xi, v*1.15, f'{v:.1f}', ha='center', fontsize=9.5, color=INK2)
for xi, v in zip(x + w/2, rate['주말']):
    ax.text(xi, v*1.15, f'{v:.1f}', ha='center', fontsize=9.5, color=INK2)
ax.text(0, 300, '주말 0.53배\n(줄어듦)', ha='center', fontsize=10, color=BLUE)
ax.text(1, 30, '주말 1.84배\n(늘어남)', ha='center', fontsize=10, color=ORANGE)
ax.set_xticks(x); ax.set_xticklabels(rate.index)
ax.set_ylabel('하루당 건수 (로그축)')
ax.legend(frameon=False, loc='upper right')
ax.set_title('① 하루당 이용건수 — 주말에 방향이 정반대', fontsize=12, loc='left')

# ══ ② 대여시간 백분위수 ═══════════════════════════════════════
ax = axes[0, 1]
ps = [10, 25, 50, 75, 90, 95]
for name, d, c in [('Subscriber', S, BLUE), ('One-time user', O, ORANGE)]:
    v = [d['dur_min'].quantile(p/100) for p in ps]
    ax.plot(ps, v, color=c, lw=2, marker='o', ms=8,
            markeredgecolor=SURFACE, markeredgewidth=2, label=name)
    for p, y in zip(ps, v):
        ax.text(p, y*1.22, f'{y:.0f}', ha='center', fontsize=9, color=c)
ax.set_yscale('log'); ax.set_yticks([2, 5, 10, 30, 60, 150])
ax.set_yticklabels(['2분', '5분', '10분', '30분', '1시간', '2.5시간'])
ax.minorticks_off()
ax.set_xticks(ps); ax.set_xticklabels([f'{p}%' for p in ps])
ax.set_xlabel('백분위수'); ax.set_ylabel('대여시간 (로그축)')
ax.legend(frameon=False, loc='upper left')
ax.grid(axis='y'); ax.tick_params(length=0)
ax.set_title('② 대여시간 — 어느 지점에서 봐도 3~8배 차이', fontsize=12, loc='left')

# ══ ③ 이용 성격 지표 ══════════════════════════════════════════
ax = axes[0, 2]
met = pd.DataFrame({
    'Subscriber': [(S['dur_sec'] > 1800).mean()*100,
                   (S['Start Station ID'] == S['End Station ID']).mean()*100,
                   S['주말'].mean()*100],
    'One-time user': [(O['dur_sec'] > 1800).mean()*100,
                      (O['Start Station ID'] == O['End Station ID']).mean()*100,
                      O['주말'].mean()*100]},
    index=['30분 초과', '왕복 이용', '주말 비중'])
x3 = np.arange(3)
b1 = ax.bar(x3 - w/2, met['Subscriber'], w, label='Subscriber')
b2 = ax.bar(x3 + w/2, met['One-time user'], w, label='One-time user')
barstyle(ax, b1, BLUE); barstyle(ax, b2, ORANGE)
for xi, v in zip(x3 - w/2, met['Subscriber']):
    ax.text(xi, v + 1, f'{v:.1f}', ha='center', fontsize=9.5, color=INK2)
for xi, v in zip(x3 + w/2, met['One-time user']):
    ax.text(xi, v + 1, f'{v:.1f}', ha='center', fontsize=9.5, color=INK2)
ax.set_xticks(x3); ax.set_xticklabels(met.index)
ax.set_ylim(0, 55); ax.set_ylabel('%')
ax.legend(frameon=False, loc='upper left')
ax.set_title('③ 이용 성격 — 왕복 8배, 장시간 14배', fontsize=12, loc='left')

# ══ ④ 역별 일회 이용자 비율 ═══════════════════════════════════
ax = axes[1, 0]
tot = df['Start Station Name'].value_counts()
ov = O['Start Station Name'].value_counts()
r = pd.DataFrame({'총': tot, '일회': ov}).fillna(0)
r = r[r['총'] >= 50]
r['비율'] = r['일회'] / r['총'] * 100
pick = pd.concat([r.nlargest(7, '비율'), r.nsmallest(4, '비율')]).sort_values('비율')
y = np.arange(len(pick))
bars = ax.barh(y, pick['비율'], 0.72)
avg = len(O) / len(df) * 100
for b, v in zip(bars, pick['비율']):
    b.set_facecolor(ORANGE if v > avg else BLUE)
    b.set_edgecolor(SURFACE); b.set_linewidth(2)
ax.axvline(avg, color=RED, lw=2, ls='--')
ax.text(avg + .25, 0.1, f'전체 평균 {avg:.2f}%', color=RED, fontsize=9.5)
ax.set_yticks(y); ax.set_yticklabels(pick.index, fontsize=9.5)
for yi, v in zip(y, pick['비율']):
    ax.text(v + .2, yi, f'{v:.1f}%', va='center', fontsize=9, color=INK2)
ax.set_xlim(0, 14); ax.set_xlabel('출발 건수 중 일회 이용자 비율 (%)')
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('④ 역의 성격 — 관광형(주황) vs 통근형(파랑)', fontsize=12, loc='left')

# ══ ⑤ Subscriber 평일→주말 역 비중 변화 ═══════════════════════
ax = axes[1, 1]
wd = S[~S['주말']]['Start Station Name'].value_counts(normalize=True)*100
we = S[S['주말']]['Start Station Name'].value_counts(normalize=True)*100
k = pd.DataFrame({'평일': wd, '주말': we}).fillna(0)
k['차'] = k['주말'] - k['평일']
pick = pd.concat([k.nlargest(5, '차'), k.nsmallest(5, '차')]).sort_values('차')
y = np.arange(len(pick))
bars = ax.barh(y, pick['차'], 0.72)
for b, v in zip(bars, pick['차']):
    b.set_facecolor(ORANGE if v > 0 else BLUE)
    b.set_edgecolor(SURFACE); b.set_linewidth(2)
ax.axvline(0, color=INK2, lw=1)
ax.set_yticks(y); ax.set_yticklabels(pick.index, fontsize=9.5)
for yi, v in zip(y, pick['차']):
    ax.text(v + (.06 if v > 0 else -.06), yi, f'{v:+.2f}', va='center',
            ha='left' if v > 0 else 'right', fontsize=9, color=INK2)
ax.set_xlim(-3.1, 2.1); ax.set_xlabel('주말 비중 - 평일 비중 (%p)')
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('⑤ 정기구독자도 주말엔 다른 역에서 탄다', fontsize=12, loc='left')

# ══ ⑥ 주요 이동축 (OD) ════════════════════════════════════════
ax = axes[1, 2]
od = S.groupby(['Start Station Name', 'End Station Name']).size().nlargest(7).iloc[::-1]
lab = [f'{a} → {b}' for a, b in od.index]
y = np.arange(len(od))
bars = ax.barh(y, od.values, 0.72)
for b in bars:
    b.set_facecolor(BLUE); b.set_edgecolor(SURFACE); b.set_linewidth(2)
ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=9)
for yi, v in zip(y, od.values):
    ax.text(v + 4, yi, f'{v}', va='center', fontsize=9, color=INK2)
ax.set_xlim(0, 360); ax.set_xlabel('건수')
ax.grid(axis='x'); ax.tick_params(length=0)
ax.set_title('⑥ 정기구독자 주요 이동축 — 전부 환승역으로', fontsize=12, loc='left')

fig.tight_layout(rect=[0, 0, 1, 0.955])
fig.savefig('fig_06_profile.png', dpi=130)
print('저장: fig_06_profile.png')
