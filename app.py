import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="NorthSnack Supply Chain Analytics",page_icon="📦",layout="wide",initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container{padding:1.5rem 2rem}
    .kpi{background:white;border-radius:12px;padding:16px 20px;border:1px solid #E8E8E8;box-shadow:0 1px 4px rgba(0,0,0,0.05)}
    .kpi-label{font-size:12px;color:#888;margin-bottom:4px;font-weight:500}
    .kpi-value{font-size:26px;font-weight:700;color:#111}
    .kpi-note{font-size:11px;color:#888;margin-top:3px}
    .kpi-red .kpi-value{color:#C0392B}
    .kpi-green .kpi-value{color:#0A7540}
    .kpi-amber .kpi-value{color:#B7791F}
    .finding{background:#F0FBF6;border-left:3px solid #27AE60;border-radius:0 8px 8px 0;padding:11px 15px;font-size:13px;color:#1A5C35;margin:10px 0;line-height:1.6}
    .alert{background:#FDF2F2;border-left:3px solid #C0392B;border-radius:0 8px 8px 0;padding:11px 15px;font-size:13px;color:#7B1818;margin:10px 0;line-height:1.6}
    .warning{background:#FEF9EC;border-left:3px solid #F39C12;border-radius:0 8px 8px 0;padding:11px 15px;font-size:13px;color:#7D5A00;margin:10px 0;line-height:1.6}
    .section-title{font-size:15px;font-weight:600;color:#111;margin:18px 0 10px 0;padding-bottom:6px;border-bottom:1.5px solid #EBEBEB}
    footer{visibility:hidden}
</style>
""",unsafe_allow_html=True)

@st.cache_data
def load():
    base=Path(__file__).parent
    sales=pd.read_csv(base/"sales-data.csv")
    summary=pd.read_csv(base/"sku-summary.csv")
    reorder=pd.read_csv(base/"reorder-model.csv")
    return sales,summary,reorder

sales,sku_summary,reorder=load()

SKU_COLORS={"NS-CHIP-001":"#E1306C","NS-BAR-002":"#4285F4","NS-MIX-003":"#27AE60"}
SKU_NAMES={"NS-CHIP-001":"Chips","NS-BAR-002":"Granola Bar","NS-MIX-003":"Trail Mix"}

st.markdown("## NorthSnack Foods — Supply Chain Analytics")
st.markdown("**January 2023 to December 2024** &nbsp;|&nbsp; 3 SKUs &nbsp;|&nbsp; 104 weeks of sales data")
st.divider()

tab1,tab2,tab3,tab4=st.tabs(["  Demand and Stockouts  ","  Forecast vs Actuals  ","  Reorder Model  ","  Lost Revenue Analysis  "])

with tab1:
    total_lost=sku_summary["Total Lost Revenue CAD"].sum()
    total_rev=sku_summary["Total Revenue CAD"].sum()
    total_stockout_wks=sku_summary["Stockout Weeks"].sum()
    worst_sku=sku_summary.loc[sku_summary["Stockout Rate %"].idxmax(),"SKU ID"]

    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.markdown(f"""<div class="kpi kpi-red">
            <div class="kpi-label">Total lost revenue</div>
            <div class="kpi-value">${total_lost:,.0f}</div>
            <div class="kpi-note">2 years across 3 SKUs</div>
        </div>""",unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi kpi-amber">
            <div class="kpi-label">Lost as % of potential</div>
            <div class="kpi-value">{round(total_lost/(total_rev+total_lost)*100,1)}%</div>
            <div class="kpi-note">Opportunity cost of stockouts</div>
        </div>""",unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi kpi-red">
            <div class="kpi-label">Total stockout weeks</div>
            <div class="kpi-value">{total_stockout_wks}</div>
            <div class="kpi-note">Across all 3 SKUs</div>
        </div>""",unsafe_allow_html=True)
    with col4:
        worst_rate=sku_summary.loc[sku_summary["SKU ID"]==worst_sku,"Stockout Rate %"].values[0]
        st.markdown(f"""<div class="kpi kpi-red">
            <div class="kpi-label">Highest stockout rate</div>
            <div class="kpi-value">{worst_rate}%</div>
            <div class="kpi-note">{SKU_NAMES.get(worst_sku,worst_sku)} — weeks out of stock</div>
        </div>""",unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="alert"><strong>The pattern:</strong> Stockouts cluster around promotion weeks and seasonal peaks — exactly when demand is highest and inventory buffers are lowest. Trail Mix shows the most severe stockout pattern, peaking in late summer (weeks 35 to 42) when outdoor snack demand spikes.</div>',unsafe_allow_html=True)

    selected_skus=st.multiselect("Filter SKU",sales["SKU ID"].unique().tolist(),default=sales["SKU ID"].unique().tolist(),key="sku_filter1")
    filtered=sales[sales["SKU ID"].isin(selected_skus)]

    col1,col2=st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Weekly demand vs actual sales by SKU</div>',unsafe_allow_html=True)
        fig=go.Figure()
        for sku in selected_skus:
            d=filtered[filtered["SKU ID"]==sku]
            fig.add_trace(go.Scatter(x=d["Week Start Date"],y=d["Actual Demand Units"],name=f"{SKU_NAMES.get(sku,sku)} Demand",line=dict(color=SKU_COLORS.get(sku,"#888"),width=1.5,dash="dot")))
            fig.add_trace(go.Scatter(x=d["Week Start Date"],y=d["Actual Sales Units"],name=f"{SKU_NAMES.get(sku,sku)} Sales",line=dict(color=SKU_COLORS.get(sku,"#888"),width=2),fill="tonexty",fillcolor=SKU_COLORS.get(sku,"#888").replace("E1","F4")+"22"))
        fig.update_layout(height=320,plot_bgcolor="white",yaxis=dict(title="Units",gridcolor="#F1F1F1"),xaxis=dict(title=""),legend=dict(orientation="h",y=1.15,font=dict(size=10)),margin=dict(t=10,b=20))
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Stockout weeks highlighted on timeline</div>',unsafe_allow_html=True)
        fig2=go.Figure()
        for sku in selected_skus:
            d=filtered[filtered["SKU ID"]==sku]
            stockout_d=d[d["Stockout"]=="Yes"]
            normal_d=d[d["Stockout"]=="No"]
            fig2.add_trace(go.Scatter(x=normal_d["Week Start Date"],y=normal_d["Actual Sales Units"],name=f"{SKU_NAMES.get(sku,sku)} Normal",line=dict(color=SKU_COLORS.get(sku,"#888"),width=2),mode="lines"))
            if len(stockout_d)>0:
                fig2.add_trace(go.Scatter(x=stockout_d["Week Start Date"],y=stockout_d["Actual Sales Units"],name=f"{SKU_NAMES.get(sku,sku)} Stockout",mode="markers",marker=dict(color="#C0392B",size=8,symbol="x")))
        fig2.update_layout(height=320,plot_bgcolor="white",yaxis=dict(title="Sales Units",gridcolor="#F1F1F1"),xaxis=dict(title=""),legend=dict(orientation="h",y=1.15,font=dict(size=10)),margin=dict(t=10,b=20))
        st.plotly_chart(fig2,use_container_width=True)

    st.markdown('<div class="section-title">SKU performance summary</div>',unsafe_allow_html=True)
    disp=sku_summary.copy()
    for col in ["Total Revenue CAD","Total Lost Revenue CAD","Total Gross Profit CAD"]:
        disp[col]=disp[col].apply(lambda x:f"${x:,.0f}")
    st.dataframe(disp,use_container_width=True,hide_index=True)

with tab2:
    st.markdown('<div class="section-title">Forecast vs actual sales — 4-week moving average</div>',unsafe_allow_html=True)
    st.markdown('<div class="finding">The 4-week moving average forecast is shown against actual demand. Gaps between the forecast line and actual demand identify where the planning model underestimated need — these weeks correspond closely to stockout events.</div>',unsafe_allow_html=True)

    sku_select=st.selectbox("Select SKU",sales["SKU ID"].unique().tolist(),key="sku_forecast")
    sku_data=sales[sales["SKU ID"]==sku_select].copy()

    fig_fc=go.Figure()
    fig_fc.add_trace(go.Scatter(x=sku_data["Week Start Date"],y=sku_data["Actual Demand Units"],name="Actual Demand",line=dict(color="#111",width=2)))
    fig_fc.add_trace(go.Scatter(x=sku_data["Week Start Date"],y=sku_data["4 Week Moving Average"],name="4-Week Moving Average",line=dict(color="#4285F4",width=2,dash="dash")))

    stockout_weeks=sku_data[sku_data["Stockout"]=="Yes"]
    for _,row in stockout_weeks.iterrows():
        fig_fc.add_vrect(x0=row["Week Start Date"],x1=row["Week Start Date"],fillcolor="#C0392B",opacity=0.15,line_width=0)
    promo_weeks=sku_data[sku_data["Is Promotion Week"]=="Yes"]
    for _,row in promo_weeks.iterrows():
        fig_fc.add_vrect(x0=row["Week Start Date"],x1=row["Week Start Date"],fillcolor="#F39C12",opacity=0.15,line_width=0)

    fig_fc.update_layout(height=360,plot_bgcolor="white",yaxis=dict(title="Units",gridcolor="#F1F1F1"),xaxis=dict(title=""),legend=dict(orientation="h",y=1.1),margin=dict(t=10,b=20))
    st.plotly_chart(fig_fc,use_container_width=True)
    st.caption("Red shading = stockout week. Orange shading = promotion week.")

    col1,col2=st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Demand by week of year — seasonality pattern</div>',unsafe_allow_html=True)
        weekly_avg=sku_data.groupby("Week Number")["Actual Demand Units"].mean().reset_index()
        fig_seas=px.line(weekly_avg,x="Week Number",y="Actual Demand Units",markers=True,color_discrete_sequence=[SKU_COLORS.get(sku_select,"#888")])
        fig_seas.update_layout(height=280,plot_bgcolor="white",yaxis=dict(title="Avg Weekly Units",gridcolor="#F1F1F1"),xaxis=dict(title="Week of Year"),margin=dict(t=10,b=20))
        st.plotly_chart(fig_seas,use_container_width=True)
    with col2:
        st.markdown('<div class="section-title">Promotion week vs normal week demand</div>',unsafe_allow_html=True)
        promo_comp=sku_data.groupby("Is Promotion Week")["Actual Demand Units"].mean().reset_index()
        promo_comp["Label"]=promo_comp["Is Promotion Week"].map({"Yes":"Promotion Week","No":"Normal Week"})
        fig_promo=px.bar(promo_comp,x="Label",y="Actual Demand Units",color="Label",color_discrete_map={"Promotion Week":"#F39C12","Normal Week":"#94A3B8"},text="Actual Demand Units")
        fig_promo.update_traces(texttemplate="%{text:.0f}",textposition="outside")
        fig_promo.update_layout(height=280,plot_bgcolor="white",yaxis=dict(title="Avg Units",gridcolor="#F1F1F1"),xaxis=dict(title=""),showlegend=False,margin=dict(t=10,b=20))
        st.plotly_chart(fig_promo,use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">Recommended reorder model — safety stock and reorder points</div>',unsafe_allow_html=True)
    st.markdown('<div class="warning">The recommended reorder points and safety stock levels are calculated using a 95% service level Z-score model based on actual demand variability and supplier lead times. Implementing these recommendations would eliminate the majority of stockout events.</div>',unsafe_allow_html=True)

    st.dataframe(reorder,use_container_width=True,hide_index=True)

    col1,col2=st.columns(2)
    with col1:
        st.markdown('<div class="section-title">EOQ by SKU — economic order quantity</div>',unsafe_allow_html=True)
        fig_eoq=px.bar(reorder,x="SKU Name",y="EOQ Units",color="SKU ID",color_discrete_map=SKU_COLORS,text="EOQ Units")
        fig_eoq.update_traces(texttemplate="%{text:,}",textposition="outside")
        fig_eoq.update_layout(height=300,plot_bgcolor="white",yaxis=dict(title="Units per Order",gridcolor="#F1F1F1"),xaxis=dict(title=""),showlegend=False,margin=dict(t=10,b=60))
        st.plotly_chart(fig_eoq,use_container_width=True)
    with col2:
        st.markdown('<div class="section-title">Safety stock vs reorder point by SKU</div>',unsafe_allow_html=True)
        fig_rop=go.Figure()
        fig_rop.add_trace(go.Bar(name="Recommended Reorder Point",x=reorder["SKU ID"],y=reorder["Recommended Reorder Point"],marker_color="#4285F4"))
        fig_rop.add_trace(go.Bar(name="Recommended Safety Stock",x=reorder["SKU ID"],y=reorder["Recommended Safety Stock"],marker_color="#F39C12"))
        fig_rop.update_layout(barmode="group",height=300,plot_bgcolor="white",yaxis=dict(title="Units",gridcolor="#F1F1F1"),xaxis=dict(title=""),legend=dict(orientation="h",y=1.1),margin=dict(t=10,b=20))
        st.plotly_chart(fig_rop,use_container_width=True)

with tab4:
    st.markdown('<div class="section-title">Lost revenue by SKU — the cost of running out</div>',unsafe_allow_html=True)

    col1,col2,col3=st.columns(3)
    for i,(col,(_,row)) in enumerate(zip([col1,col2,col3],sku_summary.iterrows())):
        with col:
            pct=round(row["Total Lost Revenue CAD"]/(row["Total Revenue CAD"]+row["Total Lost Revenue CAD"])*100,1)
            st.markdown(f"""<div class="kpi kpi-red">
                <div class="kpi-label">{SKU_NAMES.get(row['SKU ID'],row['SKU ID'])}</div>
                <div class="kpi-value">${row['Total Lost Revenue CAD']:,.0f}</div>
                <div class="kpi-note">{pct}% of potential revenue lost to stockouts</div>
            </div>""",unsafe_allow_html=True)

    st.markdown("")
    col1,col2=st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Lost revenue by month</div>',unsafe_allow_html=True)
        monthly_lost=sales.groupby(["Month","SKU ID"])["Lost Revenue CAD"].sum().reset_index()
        fig_lost=px.bar(monthly_lost,x="Month",y="Lost Revenue CAD",color="SKU ID",color_discrete_map=SKU_COLORS,barmode="stack")
        fig_lost.update_layout(height=320,plot_bgcolor="white",yaxis=dict(title="Lost Revenue (CAD)",gridcolor="#F1F1F1",tickformat="$,.0f"),xaxis=dict(title="",tickangle=45),legend=dict(orientation="h",y=1.1),margin=dict(t=10,b=80))
        st.plotly_chart(fig_lost,use_container_width=True)
    with col2:
        st.markdown('<div class="section-title">Stockout weeks vs promotion weeks correlation</div>',unsafe_allow_html=True)
        overlap=sales.groupby(["SKU ID","Is Promotion Week","Stockout"]).size().reset_index(name="Count")
        fig_overlap=px.bar(overlap,x="SKU ID",y="Count",color="Stockout",facet_col="Is Promotion Week",barmode="stack",color_discrete_map={"Yes":"#C0392B","No":"#27AE60"})
        fig_overlap.update_layout(height=320,plot_bgcolor="white",yaxis=dict(gridcolor="#F1F1F1"),margin=dict(t=40,b=20))
        st.plotly_chart(fig_overlap,use_container_width=True)

st.divider()
st.markdown("**Data note:** All sales data is synthetic and generated for portfolio purposes. NorthSnack Foods is a fictional company. Demand patterns are modelled on real CPG seasonal and promotional dynamics. Prepared by Simran Saran as part of The Case Files portfolio series.")
