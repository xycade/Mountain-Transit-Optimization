import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from matplotlib.gridspec import GridSpec
from scipy.cluster.hierarchy import linkage, dendrogram

# ==============================================================================
# 1. Global Publication Settings
# ==============================================================================
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 500

TITLE_SIZE = 20
LABEL_SIZE = 16
TICK_SIZE = 15
ANNOT_SIZE = 14

STRAT_COLORS = {
    'Detour': '#C55A52', 'Truncation': '#6B9E78', 'Alternative': '#4A6984',
    'Stop-Skipping': '#DDA443', 'Freq Tuning': '#9B9B9B'
}
STRAT_ORDER = ['Detour', 'Truncation', 'Alternative', 'Stop-Skipping', 'Freq Tuning']
MUTE_RD_BU = sns.diverging_palette(240, 15, s=40, l=65, as_cmap=True)


# ==============================================================================
# 2. Data Preparation
# ==============================================================================
def get_all_data():
    # Use relative paths for GitHub portability
    scen_files = {
        'SP': 'results/Optimized_Lines_Service_Priority_SP.json',
        'CA': 'results/Optimized_Lines_Cost_Austerity_CA.json',
        'HS': 'results/Optimized_Lines_High_Synergy_HS.json',
        'BD': 'results/Optimized_Lines_Balanced_BD.json'
    }
    edges_df = pd.read_csv('data/Edges.csv')
    e_len = edges_df.set_index(['FromNode', 'ToNode'])['Length'].to_dict()
    e_ov = edges_df.set_index(['FromNode', 'ToNode'])['Overlap'].to_dict()
    e_tm = edges_df.set_index(['FromNode', 'ToNode'])['TravelTime'].to_dict()

    def calc(freq, path, stops):
        if freq < 0.1: return 0, 0, 0
        r_l, r_o, r_t = 0, 0, 0
        for i in range(1, len(path)):
            u, v = int(path[i - 1]), int(path[i])
            d = e_len.get((u, v), 500.0)
            r_l += d
            r_t += e_tm.get((u, v), d / 333) + (0.5 if stops[i] == 1 else 0)
            if e_ov.get((u, v), 0) == 1: r_o += d
        return (math.ceil(r_t * 2.2 * (freq / 60)) * 120) + (r_l * 2 * freq / 1000 * 0.18), r_o * 2 * freq / 1000, sum(
            stops) * freq

    with open('data/Baseline_Lines_With_Freq.json', 'r', encoding='utf-8') as f:
        base_d = json.load(f)
    base_m = {rid: {'cost': c, 'overlap': ov, 'dwell': dw, 'st': d['stop_pattern']}
              for rid, d in base_d.items() for c, ov, dw in [calc(d['frequency'], d['full_path'], d['stop_pattern'])]}

    attr = {scen: {s: {'cost': 0, 'overlap': 0, 'dwell': 0} for s in STRAT_COLORS} for scen in scen_files}
    for sn, path in scen_files.items():
        with open(path, 'r', encoding='utf-8') as f:
            sd = json.load(f)
        for rid, d in sd.items():
            strat = ('Detour' if d['chosen_candidate_id'] == 1 else 'Truncation' if d[
                                                                                        'chosen_candidate_id'] == 2 else 'Alternative' if
            d['chosen_candidate_id'] == 3 else 'Stop-Skipping' if d['stop_pattern'] != base_m[rid][
                'st'] else 'Freq Tuning')
            c, ov, dw = calc(d['frequency'], d['full_path'], d['stop_pattern'])
            attr[sn][strat]['cost'] += c - base_m[rid]['cost']
            attr[sn][strat]['overlap'] += ov - base_m[rid]['overlap']
            attr[sn][strat]['dwell'] += dw - base_m[rid]['dwell']

    df_hm = pd.read_csv('results/Network_Science_Metrics_FULL.csv').set_index('Scenario')
    for col in df_hm.columns:
        if df_hm[col].dtype == 'object': df_hm[col] = df_hm[col].str.replace('%', '').astype(float) / 100
    return attr, df_hm


attr_data, df_hm = get_all_data()

# ==============================================================================
# 3. Layout and Visualization
# ==============================================================================
fig = plt.figure(figsize=(14, 15))
gs_master = GridSpec(2, 2, height_ratios=[1.5, 1], width_ratios=[0.86, 0.14], hspace=0.4, wspace=0.01)

# ------------------------------------------------------------------------------
# (a) Top Panel: Multidimensional Performance Clustering Analysis
# ------------------------------------------------------------------------------
gs_a = gs_master[0, 0].subgridspec(2, 2, width_ratios=[0.1, 1], height_ratios=[0.1, 1.2], hspace=0, wspace=0)
ax_d_left = fig.add_subplot(gs_a[1, 0])  # Row dendrogram
ax_d_top = fig.add_subplot(gs_a[0, 1])  # Column dendrogram
ax_hm = fig.add_subplot(gs_a[1, 1])  # Heatmap core

# Perform Hierarchical Clustering
scaler = StandardScaler()
data_scaled = pd.DataFrame(scaler.fit_transform(df_hm), index=df_hm.index, columns=df_hm.columns)
Z_rows = linkage(data_scaled.T, method='ward')  # Metrics
Z_cols = linkage(data_scaled, method='ward')  # Scenarios

# Draw Dendrograms
with plt.rc_context({'lines.linewidth': 1.2}):
    d_l = dendrogram(Z_rows, ax=ax_d_left, orientation='left', no_labels=True, color_threshold=0,
                     link_color_func=lambda x: '#5D6D6E')
    d_t = dendrogram(Z_cols, ax=ax_d_top, orientation='top', no_labels=True, color_threshold=0,
                     link_color_func=lambda x: '#5D6D6E')

# Coordinate alignment
ax_d_left.set_ylim(0, len(df_hm.columns) * 10)
ax_d_top.set_xlim(0, len(df_hm.index) * 10)
ax_d_left.axis('off')
ax_d_top.axis('off')

# Reordered Heatmap Plotting
re_scen_idx, re_metr_idx = d_t['leaves'], d_l['leaves']
re_df = df_hm.iloc[re_scen_idx, re_metr_idx].T
re_sc = data_scaled.iloc[re_scen_idx, re_metr_idx].T

sns.heatmap(re_sc, cmap=MUTE_RD_BU, center=0, ax=ax_hm, cbar=False, linewidths=0.5, linecolor='white')

# Populate cell values
for i in range(re_df.shape[0]):
    for j in range(re_df.shape[1]):
        val = re_df.iloc[i, j]
        txt = f"{val / 1000:.1f}k" if val >= 1000 else (f"{val:.1e}" if val < 0.001 else f"{val:.3g}")
        c = "white" if abs(re_sc.iloc[i, j]) > 1.3 else "#1A1A1A"
        ax_hm.text(j + 0.5, i + 0.5, txt, ha='center', va='center', fontsize=ANNOT_SIZE, fontweight='bold', color=c)

# Align Y-axis tick labels on the right
ax_hm.yaxis.tick_right()
ax_hm.set_yticklabels(re_df.index, rotation=0, fontsize=TICK_SIZE, ha='left')
ax_hm.tick_params(axis='y', which='major', pad=15)
ax_hm.set_xticklabels(re_df.columns, rotation=0, fontsize=LABEL_SIZE, fontweight='bold')
ax_hm.tick_params(length=0)

# Colorbar setup
cb_ax = fig.add_axes([0.97, 0.65, 0.012, 0.12])
cb = plt.colorbar(ax_hm.get_children()[0], cax=cb_ax)
cb.outline.set_visible(False)
cb.set_label("Std. Score", fontsize=LABEL_SIZE - 2, style='italic')
cb.ax.tick_params(labelsize=TICK_SIZE - 2)

# ------------------------------------------------------------------------------
# (b) Bottom Panel: Algorithmic Strategy Attribution Analysis
# ------------------------------------------------------------------------------
gs_b = gs_master[1, 0].subgridspec(1, 3, wspace=0.3)
axes_b = [fig.add_subplot(gs_b[i]) for i in range(3)]

scen_list = ['BD', 'HS', 'CA', 'SP']
metrics_b = [('dwell', r'$\Delta$ Travel Time (min)', 'F1 Performance'),
             ('cost', r'$\Delta$ Cost (CNY)', 'F2 Performance'),
             ('overlap', r'$\Delta$ Overlap (km)', 'F3 Performance')]

for i, (m_key, m_label, m_title) in enumerate(metrics_b):
    ax = axes_b[i]
    x_pos = np.arange(len(scen_list))
    neg_b, pos_b = np.zeros(len(scen_list)), np.zeros(len(scen_list))

    for s in STRAT_ORDER:
        vals = np.array([attr_data[scen][s][m_key] for scen in scen_list])
        for idx, v in enumerate(vals):
            if v < 0:
                ax.bar(x_pos[idx], v, bottom=neg_b[idx], color=STRAT_COLORS[s],
                       width=0.4, edgecolor='white', linewidth=0.4, zorder=3)
                neg_b[idx] += v
            else:
                ax.bar(x_pos[idx], v, bottom=pos_b[idx], color=STRAT_COLORS[s],
                       width=0.4, edgecolor='white', linewidth=0.4, zorder=3)
                pos_b[idx] += v

    net_v = [sum(attr_data[scen][strat][m_key] for strat in STRAT_ORDER) for scen in scen_list]
    ax.scatter(x_pos, net_v, color='black', marker='D', s=20, zorder=5)

    ax.axhline(0, color='#333333', linewidth=1.2, alpha=0.8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(scen_list, fontsize=TICK_SIZE, fontweight='bold')
    ax.set_ylabel(m_label, fontsize=TICK_SIZE, style='italic')
    ax.set_title(m_title, fontsize=LABEL_SIZE, fontweight='bold', color='#2C3E50', pad=15)
    ax.spines[['top', 'right', 'bottom']].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.25)

# ------------------------------------------------------------------------------
# 4. Annotations & Alignment
# ------------------------------------------------------------------------------
fig.text(0.04, 0.94, '(a) Multidimensional Performance Clustering Analysis', fontsize=TITLE_SIZE, fontweight='bold',
         ha='left')
fig.text(0.04, 0.44, '(b) Algorithmic Strategy Attribution Analysis', fontsize=TITLE_SIZE, fontweight='bold', ha='left')

# Format legend panel on the bottom right
ax_leg = fig.add_axes([0.90, 0.15, 0.08, 0.25])
ax_leg.axis('off')
leg_el = [mpatches.Patch(color=STRAT_COLORS[s], label=s) for s in STRAT_ORDER]
leg_el.append(Line2D([0], [0], marker='D', color='w', markerfacecolor='black', markersize=8, label='Net Change'))

ax_leg.legend(handles=leg_el, loc='center left', frameon=False,
              fontsize=TICK_SIZE, title="Strategies", title_fontsize=LABEL_SIZE, labelspacing=1.8)

# Save final high-resolution figure
output_path = 'results/Figure_6_Production_Ready.png'
plt.savefig(output_path, dpi=600, bbox_inches='tight')
print(f"✅ Production-ready figure saved successfully to: {output_path}")