import html
import streamlit as st

def render_questions_table(df):

    """Render NUMBER + ASSESSMENT QUESTION mit sauber ausgerichteten Trennlinien (CSS Grid, unique classes)."""
    cols = [c for c in ["NUMBER | 编号", "ASSESSMENT QUESTION | 评估问题 "] if c in df.columns]
    view = df[cols].dropna(subset=["NUMBER | 编号"]).sort_values(
        ["NUMBER | 编号"], ignore_index=True
    )

    if view.empty:
        st.info("No questions match the current filters.")
        return

    st.markdown(
        """
        <style>
        :root { --qt-num-w: 6rem; --qt-gap: .75rem; }
        .qtbl { width: 100%; }
        .qtbl-header,
        .qtbl-row {
          display: grid;
          grid-template-columns: var(--qt-num-w) 1fr;
          column-gap: var(--qt-gap);
        }
        .qtbl-header {
          font-weight: 700;
          padding: .25rem 0 .5rem;
          border-bottom: 1px solid rgba(0,0,0,.08);
        }
        .qtbl-row {
          padding: .75rem 0;
          border-bottom: 1px solid rgba(0,0,0,.06);
        }
        .qtbl-num  { white-space: nowrap; font-weight: 600; }
        .qtbl-qtxt { white-space: normal; overflow-wrap: anywhere; word-break: break-word; line-height: 1.45; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="qtbl"><div class="qtbl-header"><div>NUMBER</div><div>ASSESSMENT QUESTION</div></div>',
        unsafe_allow_html=True,
    )

    html_rows = []
    for _, r in view.iterrows():
        num = html.escape(str(r.get("NUMBER | 编号", "")))
        q   = html.escape(str(r.get("ASSESSMENT QUESTION | 评估问题 ", "")))
        html_rows.append(f'<div class="qtbl-row"><div class="qtbl-num">{num}</div><div class="qtbl-qtxt">{q}</div></div>')

    st.markdown("".join(html_rows) + "</div>", unsafe_allow_html=True)
