import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from itertools import groupby
import streamlit as st
import io
from matplotlib import font_manager
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from dashboard.constants import NUMBER_TO_GRAY, DIM_COLORS, LEVEL_MAP_FRAC, LEVEL_MAP_ORD
from dashboard.utils import wrap_text

    

def polar_base(categories, dim_map):
    """Create base polar chart with dimension bands + indicator labels."""
    N = len(categories)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False)
    sector_w = 2*np.pi / N

    dim_sequence = [dim_map[c] for c in categories]
    dim_segments = [(d, sum(1 for _ in grp)) for d, grp in groupby(dim_sequence)]

    fig = plt.figure(figsize=(9,9), dpi=150)
    ax = fig.add_subplot(111, projection="polar")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 5.5)
    ax.set_yticks([])
    ax.set_xticks(angles)
    ax.set_xticklabels([])
    ax.grid(color="grey", linestyle="--", linewidth=0.5)

    outer_bottom, outer_height = 4.1, 6
    start = 0
    wrap_w_dim = 30
    for dim_name, count in dim_segments:
        w = count * sector_w
        if dim_name == "Engineering | 工程":
            outer_height = 4.3
        else: outer_height = 4.1

        ax.bar(start, outer_height, width=w, bottom=outer_bottom, align="edge",
               color=DIM_COLORS.get(dim_name, "gray"), edgecolor="white", linewidth=1.5)
        mid = start + w/2
        ang_deg = 360 - np.degrees(mid)
        if 90 < ang_deg < 270: 
            ang_deg += 180
        dim_label = "\n".join(wrap_text(dim_name, wrap_w_dim).split("\n"))
        
        if dim_name == "Engineering | 工程":
            offset = 1.1
        else: offset = 0.9
        ax.text(mid, outer_bottom+offset, dim_label,
                rotation=ang_deg, rotation_mode="anchor",
                ha="center", va="center", fontsize=9, fontweight="bold", color="black")
        start += w

    label_r, wrap_w = 4.5, 13
    for i, cat in enumerate(categories):
        th = angles[i] + sector_w/2
        ang_deg = 360 - np.degrees(th)
        if 100 <= ang_deg <= 280: ang_deg += 180
        ax.text(th, label_r, "\n".join(wrap_text(cat, wrap_w).split("\n")),
                rotation=ang_deg, ha="center", va="center", fontsize=7)#, fontweight="bold")
    return fig, ax, angles, sector_w

def _draw_questions(ax, df, cat, theta, sector_w):
    for level in range(1,5):
        q = df.loc[(df["INDICATOR | 指标"]==cat) & (df["LEVEL"]==level), "NUMBER | 编号"].values
        if len(q): ax.text(theta+sector_w/2, level-0.2, wrap_text(q[0], 20),
                           ha="center", va="center", fontsize=5, color="black")

def plot_maturity(df):

    plt.rcParams['font.sans-serif'] = ['SimHei']   
    plt.rcParams['axes.unicode_minus'] = False     

    dim_map = dict(zip(df["INDICATOR | 指标"], df["DIMENSION | 维度"]))
    cats = df["INDICATOR | 指标"].unique().tolist()
    fig, ax, angles, sector_w = polar_base(cats, dim_map)

    df["RESPONSE_NUMBER"] = (df["RESPONSE_NUMBER"].fillna(-1).astype(int))

    GRAY_SCALE = 0.8
    for i, cat in enumerate(cats):
        th = angles[i]
        for level in range(1,5):
            vals = df.loc[(df["INDICATOR | 指标"]==cat) & (df["LEVEL"]==level), "RESPONSE_NUMBER"].values
            val = int(vals[0]) if len(vals) else 0
            if val == 0:   color = "#FFF064"
            elif val == -1: color = "white"
            elif val == 99: color = "#d9c7a1" 
            elif val == 1: color = 'white'
            else:          color = str(1 - NUMBER_TO_GRAY.get(val,0.0)*GRAY_SCALE)
            ax.bar(th, 1, width=sector_w, bottom=level-1, align="edge",
                   color=color, edgecolor="black", linewidth=0.5)
        _draw_questions(ax, df, cat, th, sector_w)

    base_legend = [
        #mpatches.Patch(color="#E8E8E8", label="Not implemented yet | 尚未实施 "),
        mpatches.Patch(color="white", label="Not implemented yet | 尚未实施 "),
        mpatches.Patch(color="0.7",     label="Partially implemented | 部分实施"),
        mpatches.Patch(color="0.3",     label="Broadly implemented | 广泛实施"),
        mpatches.Patch(color="0.0",     label="Fully implemented | 全面实施"),
    ]

    optional_map = {
        "Not relevant | 不相关": ("#d9c7a1", "Not relevant | 不相关"),
        "Don't know | 不知道":   ("#FFF064", "Don't know | 不知道"),
    }

    available = set(df["CURRENT IMPLEMENTATION LEVEL | 当前实施水平"].unique())
    optional_legend = [
        mpatches.Patch(color=color, label=label)
        for key, (color, label) in optional_map.items()
        if key in available
    ]

    legend_handles = base_legend + optional_legend

    fontP = font_manager.FontProperties(family='SimHei')  # optional: size=7

    leg = ax.legend(
        handles=legend_handles,
        title="Maturity level | 成熟度水平",
        title_fontsize=9,          
        fontsize=7,                
        #prop=fontP,               
        loc="lower center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=3,
        frameon=True,
        fancybox=True,
        framealpha=0.9,
        borderpad=1.2,
    )
    
    #leg.get_title().set_fontproperties(fontP)
    #leg.get_frame().set_edgecolor("gray")

    leg.get_frame().set_linewidth(0.8)

    st.pyplot(fig)#, use_container_width=True)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=600, bbox_inches="tight", pad_inches=0.05)
    buf.seek(0)

    st.download_button(
        label="💾 Download figure",
        data=buf,
        file_name="maturity_results.png",
        mime="image/png"
    )
    fig.savefig("maturity_results_local.png", dpi=600, bbox_inches="tight", pad_inches=0.05)

def plot_gap(df1):

    dim_map = dict(zip(df1["INDICATOR | 指标"], df1["DIMENSION | 维度"]))
    cats = df1["INDICATOR | 指标"].unique().tolist()
    fig, ax, angles, sector_w = polar_base(cats, dim_map)

    df1["RESPONSE_NUMBER"] = (df1["RESPONSE_NUMBER"].fillna(-1).astype(int)
                             )
    
    for i, cat in enumerate(cats):
        th = angles[i]
        for level in range(1,5):
            vals = df1.loc[(df1["INDICATOR | 指标"]==cat) & (df1["LEVEL"]==level), "DIFF"].values
            val = int(vals[0]) if len(vals) else 0
            if val == 3: color = "#745995" 
            elif val == 2: color = "#AE9CC4"
            elif val == 1: color = "#E4DFEC"
            else:          color = 'white'
            ax.bar(th, 1, width=sector_w, bottom=level-1, align="edge",
                   color=color, edgecolor="black", linewidth=0.5)
        _draw_questions(ax, df1, cat, th, sector_w)
 
    legend = [
        mpatches.Patch(color="white",   label="No action required | 无需采取任何行动"),
        mpatches.Patch(color="#E4DFEC", label="Limited action required | 仅需采取有限行动"),
        mpatches.Patch(color="#AE9CC4", label="Significant action required | 需要采取重大行动"),
        mpatches.Patch(color="#745995", label="Extensive action required | 需要采取广泛行动"),
    ]

    leg = ax.legend(
        handles=legend,
        title="Action category | 行动类别",
        title_fontsize=9,
        fontsize=7,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=2,
        frameon=True,
        fancybox=True,
        framealpha=0.9,
        borderpad=1.2,
        edgecolor="gray",
    )
    leg.get_frame().set_linewidth(0.8)

    st.pyplot(fig, dpi=600)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=600, bbox_inches="tight", pad_inches=0.05)
    buf.seek(0)

    st.download_button(
        label="💾 Download figure",
        data=buf,
        file_name="gap_analysis.png",
        mime="image/png"
    )
    fig.savefig("gap_analysis_local.png", dpi=600, bbox_inches="tight", pad_inches=0.05)