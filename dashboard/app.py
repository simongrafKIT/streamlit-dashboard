from pathlib import Path
import sys
import matplotlib as plt
from matplotlib import rcParams
import streamlit as st
from matplotlib.font_manager import fontManager
from pathlib import Path

rcParams['font.sans-serif'] = ['SimHei']   
rcParams['axes.unicode_minus'] = False     

# rcParams["font.family"] = "sans-serif"
# rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]
# rcParams["axes.unicode_minus"] = False

_pkg_dir = Path(__file__).resolve().parent        
_parent  = _pkg_dir.parent                        
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

# font_file = Path(__file__).parent / "fonts" / "NotoSansSC-VariableFont_wght.ttf"
# fontManager.addfont(str(font_file))
# plt.rcParams["font.family"] = "Noto Sans SC"
# plt.rcParams["axes.unicode_minus"] = False


from dashboard.data_io import load_data
from dashboard.plots import plot_maturity, plot_gap
from dashboard.ui import file_uploader_left, pills_filters, gap_filters, dim_ind_filters
from dashboard.tab_questions import render_questions_table
from dashboard.alignment import show_alignment_scatter

st.set_page_config(page_title="Lean & Digital Transformation Dashboard", layout="wide")
st.title("Dashboard for Lean and Digital Transformation")

col_left, col_right = st.columns([1, 5])

with col_left:
    file_obj = file_uploader_left()

with col_right:
    if not file_obj:
        st.info("Please upload an Excel file to start.")
    else:
        df_1, df_3 = load_data(file_obj)

        tab1, tab2, tab3, tab4 = st.tabs([
            "Assessment Results", "Gap Analysis", "Priorization of Measures", "All Questions"
        ])

        with tab1:
            df1_f = pills_filters(df_1, key_prefix="t1")
            plot_maturity(df1_f)

        with tab2:
            df1_gap = gap_filters(df_1, key_prefix="t2gap") 
            plot_gap(df1_gap)             

        with tab3:
            show_alignment_scatter(df_1, df_3)
            
        with tab4:
            dfq = dim_ind_filters(df_1, key_prefix="t4")
            render_questions_table(dfq)
