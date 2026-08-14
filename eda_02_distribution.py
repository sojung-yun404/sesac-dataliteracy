"""EDA 2단계 - 단변량 분포 (변수 하나씩 혼자 보기)"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eda_common import (AGE_ORDER, BLUE, GRID, INK2, ORANGE, SURFACE,
                        WEEK_ORDER, barstyle, load)

df = load()
print('클리닝 후 shape:', df.shape)

# ── 숫자로 먼저 ──────────────────────────────────────────────────
d = df['dur_sec']
print('\n[대여시간 초]')
print(d.describe(percentiles=[.25, .5, .75, .95, .99]).round(1).to_string())
print(f'\n평균 {d.mean()/60:.1f}분 vs 중앙값 {d.median()/60:.1f}분  '
      f'-> 평균이 {d.mean()/d.median():.2f}배 부풀려짐')
print(f'왜도(skewness) {d.skew():.2f}   (0=좌우대칭, 양수=오른쪽 꼬리)')
print(f'로그 변환 후 왜도 {np.log(d).skew():.2f}')

print('\n[상위 1%가 전체 대여시간에서 차지하는 비중]')
top1 = d.nlargest(int(len(d) * .01)).sum()
print(f'{top1/d.sum()*100:.1f}%  (건수로는 1%)')

print('\n[연령]')
print(df['Age'].describe().round(1).to_string())

print('\n[연령대별 건수]')
print(df['Age Groups'].value_counts().reindex(AGE_ORDER).to_string())

print('\n[요일별 건수]')
print(df['Weekday'].value_counts().reindex(WEEK_ORDER).to_string())

# ── 그림 ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle('단변량 분포 — 변수를 하나씩 혼자 본다', fontsize=15,
             fontweight='bold', y=0.97)

# (1) 대여시간 원본 스케일
ax = axes[0, 0]
ax.hist(d[d <= 3600] / 60, bins=60, color=BLUE, edgecolor=SURFACE, linewidth=0.5)
ax.axvline(d.median()/60, color=ORANGE, lw=2)
ax.axvline(d.mean()/60, color=ORANGE, lw=2, ls='--')
ax.text(d.median()/60 + 1, ax.get_ylim()[1]*0.92, f'중앙값 {d.median()/60:.1f}분',
        color=ORANGE, fontsize=10)
ax.text(d.mean()/60 + 1, ax.get_ylim()[1]*0.78, f'평균 {d.mean()/60:.1f}분',
        color=ORANGE, fontsize=10)
ax.set_title('① 대여시간 (1시간 이내, 원본 스케일)', fontsize=12, loc='left')
ax.set_xlabel('분'); ax.set_ylabel('건수')
ax.grid(axis='y'); ax.tick_params(length=0)

# (2) 대여시간 로그 스케일
ax = axes[0, 1]
ax.hist(np.log10(d), bins=60, color=BLUE, edgecolor=SURFACE, linewidth=0.5)
ax.set_title('② 같은 데이터, 로그 스케일 → 정규분포로 변신', fontsize=12, loc='left')
ax.set_xlabel('log10(초)'); ax.set_ylabel('건수')
ax.set_xticks([np.log10(x) for x in [60, 300, 1800, 7200, 86400]])
ax.set_xticklabels(['1분', '5분', '30분', '2시간', '24시간'])
ax.grid(axis='y'); ax.tick_params(length=0)

# (3) 박스플롯
ax = axes[0, 2]
bp = ax.boxplot([d/60], orientation='horizontal', widths=0.5, patch_artist=True,
                flierprops=dict(marker='o', markersize=3, alpha=.25,
                                markerfacecolor=BLUE, markeredgecolor='none'))
bp['boxes'][0].set(facecolor=BLUE, edgecolor=BLUE, alpha=.35)
for m in bp['medians']:
    m.set(color=ORANGE, lw=2)
for w in bp['whiskers'] + bp['caps']:
    w.set(color=INK2, lw=1.2)
ax.set_xscale('log')
ax.set_title('③ 박스플롯 — 점 하나하나가 "이상치" 판정된 정상 데이터', fontsize=12, loc='left')
ax.set_xlabel('분 (로그축)'); ax.set_yticks([])
ax.set_xticks([1, 5, 16, 60, 240, 1440])
ax.set_xticklabels(['1분', '5분', '16분\n(IQR상한)', '1시간', '4시간', '24시간'])
ax.minorticks_off()
ax.grid(axis='x')

# (4) 연령 분포
ax = axes[1, 0]
ax.hist(df['Age'], bins=range(20, 78, 2), color=BLUE, edgecolor=SURFACE, linewidth=1)
ax.axvline(df['Age'].median(), color=ORANGE, lw=2)
ax.text(df['Age'].median()+1, ax.get_ylim()[1]*0.9,
        f"중앙값 {df['Age'].median():.0f}세", color=ORANGE, fontsize=10)
ax.set_title('④ 연령 분포', fontsize=12, loc='left')
ax.set_xlabel('나이'); ax.set_ylabel('건수')
ax.grid(axis='y'); ax.tick_params(length=0)

# (5) 연령대별 건수
ax = axes[1, 1]
c = df['Age Groups'].value_counts().reindex(AGE_ORDER)
bars = ax.bar(c.index, c.values)
barstyle(ax, bars)
for x, v in zip(c.index, c.values):
    ax.text(x, v + 90, f'{v:,}', ha='center', fontsize=10, color=INK2)
ax.set_title('⑤ 연령대별 대여 건수', fontsize=12, loc='left')
ax.set_ylabel('건수'); ax.set_ylim(0, c.max()*1.15)

# (6) 요일별 건수
ax = axes[1, 2]
c = df['Weekday'].value_counts().reindex(WEEK_ORDER)
bars = ax.bar(c.index, c.values)
barstyle(ax, bars)
for b, x in zip(bars, WEEK_ORDER):          # 주말만 다른 색
    if x in ('토', '일'):
        b.set_facecolor(ORANGE)
for x, v in zip(c.index, c.values):
    ax.text(x, v + 40, f'{v:,}', ha='center', fontsize=10, color=INK2)
ax.set_title('⑥ 요일별 대여 건수 (주황=주말)', fontsize=12, loc='left')
ax.set_ylabel('건수'); ax.set_ylim(0, c.max()*1.15)

fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig('fig_02_distribution.png', dpi=130)
print('\n저장: fig_02_distribution.png')
