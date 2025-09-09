import streamlit as st
from dashboard.constants import RESPONSE_TO_NUMBER, LEVEL_MAP_ORD
import pandas as pd

def file_uploader_left():
    """Left column uploader + file picker."""
    uploaded_files = st.file_uploader(label="Upload Excel file", type=["xlsx"], accept_multiple_files=True, label_visibility="collapsed")
    if not uploaded_files:
        return None
    names = [f.name for f in uploaded_files]
    chosen = st.selectbox("Select a file:", names)
    return next(f for f in uploaded_files if f.name == chosen)

def pills_filters(df, key_prefix=""):
    out = df.copy().dropna(subset=["NUMBER | 编号"])

    responses  = out["CURRENT IMPLEMENTATION LEVEL | 当前实施水平"].dropna().unique().tolist()
    dimensions = out["DIMENSION | 维度"].dropna().unique().tolist()

    c1, c2 = st.columns(2)
    with c1:
        sel_resp = st.multiselect(
            "Filter implementation level:",
            options=responses,
            default=None,
            key=f"{key_prefix}_resp"
        )
    with c2:
        sel_dims = st.multiselect(
            "Filter dimensions:",
            options=dimensions,
            default=None,
            key=f"{key_prefix}_dims"
        )

    if sel_resp and len(sel_resp) < len(responses):
        out.loc[~out["CURRENT IMPLEMENTATION LEVEL | 当前实施水平"].isin(sel_resp), "CURRENT IMPLEMENTATION LEVEL | 当前实施水平"] = "None"

    if sel_dims and len(sel_dims) < len(dimensions):
        out = out[out["DIMENSION | 维度"].isin(sel_dims)]

    out["RESPONSE_NUMBER"] = out["CURRENT IMPLEMENTATION LEVEL | 当前实施水平"].map(RESPONSE_TO_NUMBER)
    return out

def gap_filters(df1, key_prefix="gap"):

    out = df1.copy()
    out = out.sort_values(by="NUMBER | 编号").reset_index(drop=True).dropna(subset=["NUMBER | 编号"])
    if "RESPONSE_NUMBER" not in out.columns:
        out["RESPONSE_NUMBER"] = out["CURRENT IMPLEMENTATION LEVEL | 当前实施水平"].map(RESPONSE_TO_NUMBER)

    if "TARGET_NUMBER" not in out.columns:
        out["TARGET_NUMBER"] = out["TARGET IMPLEMENTATION LEVEL | 目标实施层级"].map(RESPONSE_TO_NUMBER)

    out["DIFF"] = pd.to_numeric(out["TARGET_NUMBER"], errors="coerce").fillna(0) \
                - pd.to_numeric(out["RESPONSE_NUMBER"], errors="coerce").fillna(0)

    if "BUCKET" not in out.columns:
        def _bucket(row):
            val = row.get("DIFF")
            try:
                val = int(val)
            except Exception:
                val = -1
            if val == 1:
                return "Limited action required | 仅需采取有限行动"
            if val == 2:
                return "Significant action required | 需要采取重大行动"
            if val == 3:
                return "Extensive action required | 需要采取广泛行动"
            return "No action required | 无需采取任何行动"

        out["BUCKET"] = out.apply(_bucket, axis=1)

    buckets = [
        "No action required | 无需采取任何行动",
        "Limited action required | 仅需采取有限行动",
        "Significant action required | 需要采取重大行动",
        "Extensive action required | 需要采取广泛行动",
    ]
    dimensions = out["DIMENSION | 维度"].dropna().unique().tolist()

    c1, c2 = st.columns(2)
    with c1:
        sel_buckets = st.multiselect(
            "Show action categories:",
            options=buckets,
            default=None,
            key=f"{key_prefix}_buckets"
        )
    with c2:
        sel_dims = st.multiselect(
            "Filter dimensions:",
            options=dimensions,
            default=None,
            key=f"{key_prefix}_dims"
        )

    if sel_buckets and len(sel_buckets) < len(buckets):
        out.loc[~out["BUCKET"].isin(sel_buckets), "BUCKET"] = "HIDE"

    if sel_dims and len(sel_dims) < len(dimensions):
        out = out[out["DIMENSION | 维度"].isin(sel_dims)]

    return out

def dim_ind_filters(df, key_prefix=""):
    out = df.copy()

    dims_all = sorted(out["DIMENSION | 维度"].dropna().unique().tolist())

    c1, c2 = st.columns(2)
    with c1:
        sel_dims = st.multiselect(
            "Filter dimensions:",
            options=dims_all,
            default=None,
            key=f"{key_prefix}_dims"
        )

    inds_source = out[out["DIMENSION | 维度"].isin(sel_dims)] if sel_dims else out
    inds_all = sorted(inds_source["INDICATOR | 指标"].dropna().unique().tolist())

    with c2:
        sel_inds = st.multiselect(
            "Filter indicators:",
            options=inds_all,
            default=None,
            key=f"{key_prefix}_inds"
        )

    if sel_dims and len(sel_dims) < len(dims_all):
        out = out[out["DIMENSION | 维度"].isin(sel_dims)]
    if sel_inds and len(sel_inds) < len(inds_all):
        out = out[out["INDICATOR | 指标"].isin(sel_inds)]

    return out
