"""EDA 3단계 - 이변량 관계 (변수를 둘씩 엮어서 본다)"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eda_common import (AGE_ORDER, BLUE, GRID, INK, INK2, ORANGE, SURFACE,
                        WEEK_ORDER, barstyle, load)

df = load()

fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.5))
fig.suptitle('이변량 관계 — 변수를 둘씩 엮어서 본다', fontsize=15,
             fontweight='bold', y=0.975)

# ══ ① 연령대 × 대여시간 : 평균 vs 중앙값 ═══════════════════════
ax = axes[0, 0]
g = df.groupby('Age Groups', observed=True)['dur_sec'].agg(['mean', 'median']) / 60
x = np.arange(len(AGE_ORDER)); w = 0.38
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
ax.set_title('① 연령대별 대여시간 — 평균과 중앙값의 순위가 다르다',
             fontsize=12, loc='left')

# ══ ② 같은 데이터, 박스플롯 ════════════════════════════════════
ax = axes[0, 1]
data = [df.loc[df['Age Groups'] == a, 'dur_sec'] / 60 for a in AGE_ORDER]
bp = ax.boxplot(data, patch_artist=True, widths=.55,
                flierprops=dict(marker='o', markersize=2.5, alpha=.18,
                                markerfacecolor=BLUE, markeredgecolor='none'))
for b in bp['boxes']:
    b.set(facecolor=BLUE, edgecolor=BLUE, alpha=.35)
for m in bp['medians']:
    m.set(color=ORANGE, lw=2)
for w_ in bp['whiskers'] + bp['caps']:
    w_.set(color=INK2, lw=1.1)
ax.set_yscale('log')
ax.set_yticks([1, 5, 15, 60, 240, 1440])
ax.set_yticklabels(['1분', '5분', '15분', '1시간', '4시간', '24시간'])
ax.minorticks_off()
ax.set_xticklabels(AGE_ORDER)
ax.grid(axis='y'); ax.tick_params(length=0)
ax.set_title('② 같은 데이터의 실제 퍼짐 (로그축)', fontsize=12, loc='left')

# ══ ③ 요일 × 사용자유형 : 절대건수 (함정) ══════════════════════
ax = axes[0, 2]
ct = pd.crosstab(df['Weekday'], df['User Type']).reindex(WEEK_ORDER)
x7 = np.arange(7)
b1 = ax.bar(x7 - w/2, ct['Subscriber'], w, label='Subscriber')
b2 = ax.bar(x7 + w/2, ct['One-time user'], w, label='One-time user')
barstyle(ax, b1, BLUE); barstyle(ax, b2, ORANGE)
ax.set_xticks(x7); ax.set_xticklabels(WEEK_ORDER)
ax.set_ylabel('건수')
ax.legend(frameon=False, loc='upper right')
ax.set_ylim(0, 3100)
ax.annotate('One-time user는 바닥에 눌려\n형태가 안 보임 (전체의 1.8%)',
            xy=(5.2, 60), xytext=(0.6, 900), fontsize=10, color=ORANGE,
            arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.4,
                            connectionstyle='arc3,rad=-0.25'))
ax.set_title('③ 절대건수로 비교 → 아무것도 안 보인다', fontsize=12, loc='left')

# ══ ④ 요일 × 사용자유형 : 그룹 내 비율 (정답) ══════════════════
ax = axes[1, 0]
pct = ct.div(ct.sum(axis=0), axis=1) * 100
b1 = ax.bar(x7 - w/2, pct['Subscriber'], w, label='Subscriber')
b2 = ax.bar(x7 + w/2, pct['One-time user'], w, label='One-time user')
barstyle(ax, b1, BLUE); barstyle(ax, b2, ORANGE)
for xi, v in zip(x7 - w/2, pct['Subscriber']):
    ax.text(xi, v + .4, f'{v:.0f}', ha='center', fontsize=9, color=INK2)
for xi, v in zip(x7 + w/2, pct['One-time user']):
    ax.text(xi, v + .4, f'{v:.0f}', ha='center', fontsize=9, color=INK2)
ax.axvspan(4.5, 6.5, color=ORANGE, alpha=.07, zorder=0)
ax.text(5.5, 25.5, '주말', ha='center', fontsize=10, color=ORANGE)
ax.set_xticks(x7); ax.set_xticklabels(WEEK_ORDER)
ax.set_ylabel('그룹 내 비중 (%)'); ax.set_ylim(0, 28)
ax.legend(frameon=False, loc='upper left')
ax.set_title('④ 각 그룹을 100%로 환산 → 패턴이 드러난다', fontsize=12, loc='left')

# ══ ⑤ 사용자유형별 대여시간 분포 ═══════════════════════════════
ax = axes[1, 1]
for name, col in [('Subscriber', BLUE), ('One-time user', ORANGE)]:
    s = np.log10(df.loc[df['User Type'] == name, 'dur_sec'])
    ax.hist(s, bins=45, density=True, alpha=.55, color=col, label=name)
    ax.axvline(s.median(), color=col, lw=2, ls='--')
ax.set_xticks([np.log10(v) for v in [60, 300, 1200, 3600, 86400]])
ax.set_xticklabels(['1분', '5분', '20분', '1시간', '24시간'])
ax.set_ylabel('밀도(비율로 환산)')
ax.legend(frameon=False)
ax.grid(axis='y'); ax.tick_params(length=0)
ax.set_title('⑤ 사용자유형별 대여시간 — 중앙값 5.2분 vs 20.3분',
             fontsize=12, loc='left')

# ══ ⑥ 기온 × 일별 대여건수 ═════════════════════════════════════
ax = axes[1, 2]
daily = df.groupby('Start Time').agg(건수=('trip_id', 'count'),
                                     기온=('Temperature_화씨', 'first'))
daily['주말'] = daily.index.dayofweek >= 5
for lab, sub, col in [('평일', daily[~daily['주말']], BLUE),
                      ('주말', daily[daily['주말']], ORANGE)]:
    ax.scatter(sub['기온'], sub['건수'], s=42, color=col, alpha=.7,
               edgecolor=SURFACE, linewidth=1.5, label=lab)
    z = np.polyfit(sub['기온'], sub['건수'], 1)
    xs = np.linspace(sub['기온'].min(), sub['기온'].max(), 10)
    ax.plot(xs, np.poly1d(z)(xs), color=col, lw=2, ls='--', alpha=.8)
    r = sub['건수'].corr(sub['기온'])
    ax.text(.03, .95 if lab == '평일' else .88, f'{lab} r = {r:+.3f}',
            transform=ax.transAxes, color=col, fontsize=11, fontweight='bold')
ax.set_xlabel('기온 (단위 불명 — 상대값)'); ax.set_ylabel('일별 대여 건수')
ax.legend(frameon=False, loc='lower right')
ax.grid(); ax.tick_params(length=0)
ax.set_title('⑥ 기온 × 대여건수 — 평일과 주말의 방향이 반대',
             fontsize=12, loc='left')

fig.tight_layout(rect=[0, 0, 1, 0.955])
fig.savefig('fig_03_bivariate.png', dpi=130)
print('저장: fig_03_bivariate.png')
