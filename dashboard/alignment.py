import io
import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.constants import DIM_COLORS, RESPONSE_TO_NUMBER, LEVEL_MAP_ORD

def compute_question_gaps(df1: pd.DataFrame) -> pd.DataFrame:
    """Compute DIFF per assessment question using RESPONSE_TO_NUMBER mapping."""
    COL_IND   = "INDICATOR | 指标"
    COL_NUM   = "NUMBER | 编号"
    COL_QTXT  = "ASSESSMENT QUESTION | 评估问题 "
    COL_CURR  = "CURRENT IMPLEMENTATION LEVEL | 当前实施水平"
    COL_TARG  = "TARGET IMPLEMENTATION LEVEL | 目标实施层级"

    keep_cols = [c for c in [COL_IND, COL_NUM, COL_QTXT, COL_CURR, COL_TARG, "LEVEL"] if c in df1.columns]
    q = df1[keep_cols].copy()

    if "LEVEL" not in q.columns:
        num_int = pd.to_numeric(q[COL_NUM].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
        q["LEVEL"] = ((num_int - 1) % 4 + 1).astype("Int64")

    mapper = RESPONSE_TO_NUMBER if "RESPONSE_TO_NUMBER" in globals() else {
        "Not implemented yet | 尚未实施": 1,
        "Partially implemented | 部分实施": 2,
        "Broadly implemented | 广泛实施": 3,
        "Fully implemented | 全面实施": 4,
        "Don't know | 不知道": 0,
        "Not relevant | 不相关": 0,
    }
    q["RESPONSE_NUMBER"] = q[COL_CURR].map(mapper)
    q["TARGET_NUMBER"]   = q[COL_TARG].map(mapper)

    q["DIFF"] = (
        pd.to_numeric(q["TARGET_NUMBER"], errors="coerce").fillna(0)
        - pd.to_numeric(q["RESPONSE_NUMBER"], errors="coerce").fillna(0)
    )

    q = q.dropna(subset=[COL_NUM])
    q["_NUM_SORT"] = pd.to_numeric(q[COL_NUM].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    q = (q.sort_values(["INDICATOR | 指标", "_NUM_SORT"])
          .drop(columns="_NUM_SORT")
          .reset_index(drop=True))
    return q

def _pct_to_frac(x):
    """Accept Series or DataFrame; convert '42%' -> 0.42 else numeric."""
    if isinstance(x, pd.DataFrame):
        return x.apply(_pct_to_frac)
    s = x.astype(str)
    if s.str.contains('%', na=False).any():
        return pd.to_numeric(s.str.replace('%', '', regex=False), errors='coerce') / 100.0
    return pd.to_numeric(s, errors='coerce')

def select_goal_columns(df: pd.DataFrame) -> list[str]:
    """Choose goal columns by position (6..10, 0-based 5:10), skip empty/Goal*-headers/empty columns."""
    raw_cols = list(df.columns[5:10])
    if not raw_cols:
        return []
    candidates = []
    for col in raw_cols:
        name = str(col).strip()
        if not name:
            continue
        if re.match(r"^\s*goal\b", name, flags=re.IGNORECASE):
            continue
        s = df[col]
        nonempty = s.notna() & (s.astype(str).str.strip() != "")
        if not nonempty.any():
            continue
        candidates.append(col)
    if not candidates:
        return []
    return st.multiselect("Filter strategic goal:", options=candidates, default=candidates)

def show_alignment_scatter(df_1: pd.DataFrame, df_3: pd.DataFrame) -> None:
    df = df_3.copy()

    COL_IND    = "INDICATOR | 指标"
    COL_DIM    = "DIMENSION | 维度"
    COL_UTIL   = "TOTAL UTILITY | 总效用值"
    COL_GAP    = "MATURITY GAP | 成熟度差距"
    COL_IMPACT = "TOTAL IMPACT | 总影响度 "
    COL_QTXT   = "ASSESSMENT QUESTION | 评估问题 "

    selected_goals = select_goal_columns(df)
    st.subheader("Impact of indicators on strategic goal(s)")

    if COL_QTXT not in df.columns and df_1 is not None and COL_QTXT in df_1.columns:
        look_q = (df_1[[COL_IND, COL_QTXT]]
                  .dropna(subset=[COL_IND, COL_QTXT])
                  .drop_duplicates(subset=[COL_IND]))
        q_map = dict(zip(
            look_q[COL_IND].astype(str).str.strip(),
            look_q[COL_QTXT].astype(str).str.strip()
        ))
        df[COL_QTXT] = df[COL_IND].astype(str).str.strip().map(q_map)

    df["MATURITY_GAP_FRAC"] = _pct_to_frac(df[COL_GAP]) if COL_GAP in df.columns else np.nan
    df["TOTAL_IMPACT_NUM"]  = pd.to_numeric(df[COL_IMPACT], errors="coerce") if COL_IMPACT in df.columns else np.nan
    df["TOTAL_UTILITY_NUM"] = pd.to_numeric(df[COL_UTIL], errors="coerce") if COL_UTIL in df.columns else np.nan

    if selected_goals:
        goals_vals = _pct_to_frac(df[selected_goals])
        df["TOTAL_UTILITY_NUM"] = goals_vals.sum(axis=1, min_count=1)
    else:
        goals_vals = pd.DataFrame(index=df.index)

    df["_X"] = df["TOTAL_UTILITY_NUM"].astype(float)
    df["_Y"] = df["MATURITY_GAP_FRAC"].astype(float)
    if df["_X"].notna().sum() == 0 or df["_Y"].notna().sum() == 0:
        st.info("No data to plot (check selected goals or input data).")
        return

    coords   = df[["_X", "_Y"]].round(5)
    dup_idx  = coords.groupby(["_X", "_Y"]).cumcount()
    grp_size = coords.groupby(["_X", "_Y"])["_X"].transform("size").clip(lower=1)
    x_span = (df["_X"].max() - df["_X"].min()) or 1.0
    y_span = (df["_Y"].max() - df["_Y"].min()) or 1.0
    r_x, r_y = x_span * 0.012, y_span * 0.02
    angle    = (dup_idx / grp_size) * 2 * np.pi
    df["_XJ"] = df["_X"] + r_x * np.cos(angle)
    df["_YJ"] = df["_Y"] + r_y * np.sin(angle)

    fig = go.Figure()

    df_sorted = df.sort_values("TOTAL_IMPACT_NUM", ascending=False).reset_index(drop=True)
    df_sorted["Priority"] = df_sorted.index + 1

    for _, row in df_sorted.iterrows():
        indicator = str(row.get(COL_IND, ""))
        dim       = "" if COL_DIM not in df.columns or pd.isna(row.get(COL_DIM)) else str(row[COL_DIM])
        color     = DIM_COLORS.get(dim, "#139e8b")
        xj, yj    = float(row["_XJ"]), float(row["_YJ"])
        xo, yo    = float(row["_X"]),  float(row["_Y"])
        impact    = float(row["TOTAL_IMPACT_NUM"]) if pd.notna(row["TOTAL_IMPACT_NUM"]) else np.nan
        prio      = int(row["Priority"])   # neue Reihenfolge


        fig.add_vline(x=float(df["_X"].median()), line_width=1, line_dash="dot", line_color="rgba(0,0,0,0.9)")
        fig.add_hline(y=float(df["_Y"].median()), line_width=1, line_dash="dot", line_color="rgba(0,0,0,0.9)")

        fig.add_trace(go.Scatter(
            x=[xj], y=[yj],
            mode="markers+text",
            text=[f"<b>{prio}</b>"],                   # fett
            textposition="middle center",
            textfont=dict(family="Arial", size=16, color="black"),  # Arial
            name=f"{prio}. {indicator}",   # Legende auch sortiert
            showlegend=True,
            marker=dict(size=28, color=color, #opacity=0,
                        line=dict(width=1.5, color="rgba(0,0,0,0.45)")),
            customdata=[[indicator, dim, xo, yo, impact]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "Total Utility: %{customdata[2]:.2f}<br>"
                "Maturity Gap: %{customdata[3]:.0%}<br>"
                "Total Impact: %{customdata[4]:.2f}"
                "<extra></extra>"
            )
        ))


    fig.update_layout(
        height=700,
        margin=dict(l=70, r=30, t=20, b=130),  # b erhöht, damit die Legende unten Platz hat
        font=dict(color="black"),
        xaxis=dict(
            title=dict(text="<b>Total Utility | 总效用值</b>", font=dict(size=20, color="black")),
            tickfont=dict(size=18, color="black"),
            zeroline=False, showline=True, linewidth=1.2, linecolor="rgba(0,0,0,0.35)",
            gridcolor="rgba(0,0,0,0.07)"
        ),
        yaxis=dict(
            title=dict(
                text="<b>Maturity Gap | 成熟度差距</b>",
                font=dict(size=20, color="black"),
                standoff=30          # Abstand (px) zwischen Achsentitel und Ticks/Achse
            ),
            tickformat=".0%",
            tickfont=dict(size=18, color="black"),
            automargin=True,         # sorgt für ausreichenden Außenrand
            zeroline=False, showline=True, linewidth=1.2, linecolor="rgba(0,0,0,0.35)",
            gridcolor="rgba(0,0,0,0.07)"
        ),

        legend=dict(
            #title=dict(text="Indicators"),
            orientation="h",
            x=0, xanchor="left",
            y=-0.18, yanchor="top",
            entrywidth=1/3,              # 3 Spalten (jede Legendenkachel = 1/3 Breite)
            entrywidthmode="fraction",   # "fraction" statt Pixel
            font=dict(size=16, color="black"),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
       # margin=dict(b=150),
        hoverlabel=dict(font=dict(size=16, color="black"), bgcolor="white")
    )

    st.plotly_chart(fig, use_container_width=True)

    fig.write_image(
    "alignment_scatter.png",
    format="png",
    width=1600,    # Breite in Pixel
    height=900,   # Höhe in Pixel
    scale=3        # Multiplikator für DPI (3x = sehr scharf)
    )





    qg = compute_question_gaps(df_1)

    qg = qg[qg["DIFF"] > 0].copy()

    if selected_goals:
        goals_contrib = _pct_to_frac(df[selected_goals])
        indicator_goal_mask = (goals_contrib > 0).any(axis=1)
        df_goal_ok = df.loc[indicator_goal_mask, [COL_IND]].drop_duplicates()
    else:
        df_goal_ok = df[[COL_IND]].drop_duplicates()

    df_imp = df[[COL_IND, "TOTAL_IMPACT_NUM"]].drop_duplicates()
    qlist = (
        qg.merge(df_imp, on=COL_IND, how="left")
          .merge(df_goal_ok.assign(_GOAL_OK=True), on=COL_IND, how="left")
    )
    if selected_goals:
        qlist = qlist[qlist["_GOAL_OK"] == True]
    qlist = qlist[qlist["TOTAL_IMPACT_NUM"] > 0]
# Using LEVEL_MAP_ORD from dashboard.constants
    LEVEL_MAP_INV = {v: k for k, v in LEVEL_MAP_ORD.items()}

    table = (
        qlist[["ASSESSMENT QUESTION | 评估问题 ", "TOTAL_IMPACT_NUM", "LEVEL"]]
        .rename(columns={
            "ASSESSMENT QUESTION | 评估问题 ": "Measure",
            "TOTAL_IMPACT_NUM": "Total Impact"
        })
        .dropna(subset=["Measure"])
    )
    from dashboard.constants import LEVEL_MAP_ORD as _LMO
    _INV = {v:k for k,v in _LMO.items()}
    table["Maturity Level"] = table["LEVEL"].map(_INV)
    table = table.sort_values(["Total Impact"], ascending=[False], kind="mergesort").reset_index(drop=True)
    table.insert(0, "Priority", range(1, len(table) + 1))

    st.subheader("Prioritized measures to engange the strategic goal(s)")

    if len(table):
        st.markdown(
            """
            <style>
            .impact-table { width: 100%; border-collapse: collapse; }
            .impact-table th, .impact-table td {
                border-bottom: 1px solid rgba(0,0,0,0.1);
                padding: 0.5rem 0.75rem;
                text-align: left;
                vertical-align: top;
            }
            .impact-table th {
                font-weight: 700;
                background-color: rgba(0,0,0,0.03);
            }
            .impact-prio  { width: 5rem;  white-space: nowrap; }
            .impact-qtxt  { white-space: normal; word-break: break-word; line-height: 1.4; }
            .impact-level { width: 12rem; white-space: nowrap; }
            .impact-val   { width: 8rem;  text-align: right; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        rows_html = []
        for _, r in table.iterrows():
            prio   = r["Priority"]
            qtxt   = str(r["Measure"]).replace("\n", "<br>")
            mlev   = r["Maturity Level"]
            impact = f"{r['Total Impact']:.2f}"
            rows_html.append(
                f"<tr>"
                f"<td class='impact-prio'>{prio}</td>"
                f"<td class='impact-qtxt'>{qtxt}</td>"
                f"<td class='impact-level'>{mlev}</td>"
                f"<td class='impact-val'>{impact}</td>"
                f"</tr>"
            )

        html_table = (
            "<table class='impact-table'>"
            "<tr><th>Priority</th><th>Measure</th><th>Maturity Level</th><th>Total Impact</th></tr>"
            + "".join(rows_html)
            + "</table>"
        )
        st.markdown(html_table, unsafe_allow_html=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            table.to_excel(writer, index=False, sheet_name="Priorities")
        st.download_button(
            label="💾 Download as Excel",
            data=buffer.getvalue(),
            file_name="priorities.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.caption("No suitable measures found.")
