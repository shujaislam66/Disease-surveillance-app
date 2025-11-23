import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="GB Disease Surveillance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    .footer {
        text-align: center;
        padding: 10px;
        font-size: 12px;
        color: #666;
        margin-top: 20px;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("""
<div class="main-header">
    <h1>🏥 Gilgit-Baltistan Disease Surveillance</h1>
    <p>Epidemiology Program - Real-time Monitoring Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Upload XLSX File", type=['xlsx', 'xls'])
if uploaded_file:
    # Load data
    df = pd.read_excel(uploaded_file, header=1)
   
    # Column mapping
    district_col = 'District'
    sex_col = 'Sex'
    epi_col = 'Epi linked(Msl/Rub/No)'
    age_col = 'Age in month'
    date_col = 'D/ rash onset'
    final_class_col = 'Final classification'
    complications_col = 'Complications'
    lab_result_col = 'Lab Result Measles'
   
    # Clean data
    df_clean = df[[district_col, sex_col, epi_col, age_col]].dropna(subset=[district_col, sex_col])
    df_clean = df_clean[df_clean[district_col].notna()]
    df_clean = df_clean[df_clean[district_col] != '']
   
    # Key Metrics Row
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        st.metric("Total Cases", len(df_clean))
    with col2:
        st.metric("Districts", df_clean[district_col].nunique())
    with col3:
        st.metric("Male %", f"{(df_clean[sex_col] == 'Male').sum() / len(df_clean) * 100:.1f}%")
   
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["📈 Overview", "🏥 Clinical Data", "🗺️ District Map", "🗺️ Geographic", "👥 Demographics", "🔗 Epidemiology", "📄 Reports"]
    )
   
    # TAB 1: OVERVIEW
    with tab1:
        st.subheader("📊 Disease Case Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cases", len(df_clean))
        with col2:
            st.metric("Cases/District", f"{len(df_clean) / df_clean[district_col].nunique():.1f}")
        with col3:
            male_count = (df_clean[sex_col] == 'Male').sum()
            st.metric("Males", male_count)
        with col4:
            female_count = (df_clean[sex_col] == 'Female').sum()
            st.metric("Females", female_count)
        # Gender Distribution Pie Chart
        st.subheader("MALE/FEMALE")
        gender_counts = df_clean[sex_col].value_counts()
        fig_gender = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            color_discrete_map={'Male': '#1f77b4', 'Female': '#ff7f0e'},
            hole=0
        )
        fig_gender.update_traces(textinfo='label+percent', textfont=dict(size=14))
        st.plotly_chart(fig_gender, use_container_width=True, key='gender_pie_chart')

    # TAB 2: CLINICAL DATA
    with tab2:
        st.subheader("🏥 Clinical Data Analysis")
        col1, col2 = st.columns(2)
        # Final Classification
        with col1:
            st.subheader("Final classification")
            if final_class_col in df.columns:
                final_class = df[final_class_col].value_counts()
                fig_final = px.bar(
                    x=final_class.index,
                    y=final_class.values,
                    color=final_class.index,
                    text=final_class.values,
                    labels={'x': 'Final Classification', 'y': 'Count of Epid number'}
                )
                fig_final.update_traces(textposition='auto', textfont=dict(size=12))
                fig_final.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_final, use_container_width=True, key='final_class_chart')
        # Lab Result - Positive/Negative
        with col2:
            st.subheader("Lab Result Measles")
            if lab_result_col in df.columns:
                lab_result = df[lab_result_col].value_counts()
                colors_lab = {'Positive': '#2ecc71', 'Negative': '#e74c3c'}
                fig_lab = px.bar(
                    x=lab_result.index,
                    y=lab_result.values,
                    color=lab_result.index,
                    color_discrete_map=colors_lab,
                    text=lab_result.values,
                    labels={'x': 'Lab Result', 'y': 'Count of Epid number'}
                )
                fig_lab.update_traces(textposition='auto', textfont=dict(size=12))
                fig_lab.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_lab, use_container_width=True, key='lab_result_chart')
        # Age Wise Total Cases
        st.subheader("AGE WISE TOTAL CASES")
        df_age = df.copy()
        df_age[age_col] = pd.to_numeric(df_age[age_col], errors='coerce')
        def categorize_age(age):
            if pd.isna(age):
                return np.nan
            if age < 9:
                return '0 - 9 M'
            elif age < 24:
                return '9 - 24 M'
            elif age < 60:
                return '24 - 60 M'
            elif age < 120:
                return '60 - 120 M'
            elif age < 180:
                return '120 - 180 M'
            else:
                return '> 180 M'
        df_age['Age Category'] = df_age[age_col].apply(categorize_age)
        age_counts = df_age['Age Category'].value_counts().sort_index()
        fig_age = px.bar(
            x=age_counts.index,
            y=age_counts.values,
            color_discrete_sequence=['#3498db'],
            text=age_counts.values,
            labels={'x': 'Age Category', 'y': 'Count of Epid number'}
        )
        fig_age.update_traces(textposition='auto', textfont=dict(size=12))
        fig_age.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_age, use_container_width=True, key='age_wise_chart')
        # Complications
        st.subheader("Complications")
        if complications_col in df.columns:
            complications = df[complications_col].fillna('None').value_counts().head(10)
            fig_comp = px.bar(
                x=complications.index,
                y=complications.values,
                color_discrete_sequence=['#3498db'],
                text=complications.values,
                labels={'x': 'Complications Type', 'y': 'Count of Epid number'}
            )
            fig_comp.update_traces(textposition='auto', textfont=dict(size=11))
            fig_comp.update_layout(showlegend=False, height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_comp, use_container_width=True, key='complications_chart')

    # TAB 3: District Map
    with tab3:
        # District-wise lab results
        if lab_result_col in df.columns:
            dist_lab = pd.crosstab(df[district_col], df[lab_result_col])
            fig_dist_lab = px.bar(
                dist_lab,
                barmode='group',
                text_auto=True,
                labels={'value': 'Count of Epid number', 'index': 'Reporting district'}
            )
            fig_dist_lab.update_traces(textposition='auto', textfont=dict(size=10))
            fig_dist_lab.update_layout(height=500)
            st.plotly_chart(fig_dist_lab, use_container_width=True, key='district_lab_chart')

        # District-wise color-coded map
        st.subheader("🗺️ District Case Distribution (Color-Coded)")
        district_cases_sorted = df[district_col].value_counts().sort_values(ascending=True)

        fig_map = go.Figure(data=[
            go.Bar(
                y=district_cases_sorted.index,
                x=district_cases_sorted.values,
                orientation='h',
                marker=dict(
                    color=district_cases_sorted.values,
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="Cases")
                ),
                text=district_cases_sorted.values,
                textposition='auto'
            )
        ])

        fig_map.update_layout(
            title="Total Cases Distribution by District (Red=High Risk, Green=Low Risk)",
            xaxis_title="Number of Cases",
            yaxis_title="District",
            height=500
        )
        st.plotly_chart(fig_map, use_container_width=True, key='district_map_chart')

    # TAB 4: Geographic
    with tab4:
        # District-wise lab results
        if lab_result_col in df.columns:
            dist_lab = pd.crosstab(df[district_col], df[lab_result_col])
            fig_dist_lab = px.bar(
                dist_lab,
                barmode='group',
                text_auto=True,
                labels={'value': 'Count of Epid number', 'index': 'Reporting district'}
            )
            fig_dist_lab.update_traces(textposition='auto', textfont=dict(size=10))
            fig_dist_lab.update_layout(height=500)
            st.plotly_chart(fig_dist_lab, use_container_width=True, key='geo_district_lab_chart')

        # District wise color-coded map
        st.subheader("🗺️ District Case Distribution (Color-Coded)")
        district_cases_sorted = df[district_col].value_counts().sort_values(ascending=True)

        fig_map_geo = go.Figure(data=[
            go.Bar(
                y=district_cases_sorted.index,
                x=district_cases_sorted.values,
                orientation='h',
                marker=dict(
                    color=district_cases_sorted.values,
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="Cases")
                ),
                text=district_cases_sorted.values,
                textposition='auto'
            )
        ])

        fig_map_geo.update_layout(
            title="Total Cases Distribution by District (Red=High Risk, Green=Low Risk)",
            xaxis_title="Number of Cases",
            yaxis_title="District",
            height=500
        )
        st.plotly_chart(fig_map_geo, use_container_width=True, key='geo_district_map_chart')

    # TAB 5: Demographics
    with tab5:
        st.subheader("👥 Demographic Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Gender Distribution by Top Districts")
            top_districts = df[district_col].value_counts().head(10).index
            df_top = df[df[district_col].isin(top_districts)]
            gender_dist = pd.crosstab(df_top[district_col], df_top[sex_col])
            fig_gender_dist = px.bar(
                gender_dist,
                barmode='group',
                text_auto=True,
                labels={'value': 'Count', 'index': 'District'}
            )
            fig_gender_dist.update_traces(textposition='outside', textfont=dict(size=10))
            st.plotly_chart(fig_gender_dist, use_container_width=True, key='gender_dist_chart')
        with col2:
            st.subheader("Total Cases Vs Lab Positive measles")
            if lab_result_col in df.columns:
                try:
                    df['Month'] = pd.to_datetime(df[date_col]).dt.strftime('%b')
                    monthly_total = df.groupby('Month').size()
                    monthly_positive = df[df[lab_result_col] == 'Positive'].groupby('Month').size()
                    fig_monthly = go.Figure()
                    fig_monthly.add_trace(go.Bar(x=monthly_total.index, y=monthly_total.values,
                                               name='Total', marker_color='#3498db', text=monthly_total.values, textposition='auto'))
                    fig_monthly.add_trace(go.Bar(x=monthly_positive.index, y=monthly_positive.values,
                                               name='Positive', marker_color='#e67e22', text=monthly_positive.values, textposition='auto'))
                    fig_monthly.update_layout(barmode='group', height=400)
                    st.plotly_chart(fig_monthly, use_container_width=True, key='monthly_cases_chart')
                except:
                    st.info("Date data not available for monthly breakdown")

    # TAB 6: Epidemiology
    with tab6:
        st.subheader("🔗 Epidemiological Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("EPI-LINKED")
            epi_counts = df_clean[epi_col].value_counts()
            fig_epi = px.bar(
                x=epi_counts.index,
                y=epi_counts.values,
                color=epi_counts.index,
                color_discrete_map={'No': '#e74c3c', 'Yes': '#2ecc71'},
                text=epi_counts.values,
                labels={'x': 'Epi-Link Status', 'y': 'Count of Epid number'}
            )
            fig_epi.update_traces(textposition='auto', textfont=dict(size=12))
            st.plotly_chart(fig_epi, use_container_width=True, key='epi_link_chart')
        with col2:
            st.subheader("Epi-Link by Districts")
            if epi_col in df.columns:
                epi_dist = pd.crosstab(df[district_col], df[epi_col])
                fig_epi_dist = px.bar(
                    epi_dist,
                    barmode='group',
                    text_auto=True,
                    labels={'value': 'Count of Epid number', 'index': 'District'}
                )
                fig_epi_dist.update_traces(textposition='auto', textfont=dict(size=10))
                st.plotly_chart(fig_epi_dist, use_container_width=True, key='epi_dist_chart')

    # TAB 7: Reports
    with tab7:
        st.subheader("📄 Generate Reports")
        if st.button("📊 Generate Summary Report"):
            st.markdown("---")
            st.subheader("Disease Surveillance Summary Report")
            st.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Program:** Epidemiology Program, Gilgit-Baltistan")
            st.markdown("### Executive Summary")
            st.write(f"""
            - **Total Cases:** {len(df)}
            - **Districts Affected:** {df[district_col].nunique()}
            - **Male Cases:** {(df[sex_col] == 'Male').sum()} ({(df[sex_col] == 'Male').sum() / len(df) * 100:.1f}%)
            - **Female Cases:** {(df[sex_col] == 'Female').sum()} ({(df[sex_col] == 'Female').sum() / len(df) * 100:.1f}%)
            """)
            st.markdown("### Top 5 Affected Districts")
            top_5 = df[district_col].value_counts().head(5)
            for i, (district, cases) in enumerate(top_5.items(), 1):
                st.write(f"{i}. **{district}**: {cases} cases ({cases/len(df)*100:.1f}%)")
            st.markdown("### Epidemiological Link Status")
            if epi_col in df.columns:
                epi_summary = df[epi_col].value_counts()
                for status, count in epi_summary.items():
                    st.write(f"- **{status}:** {count} cases ({count/len(df)*100:.1f}%)")
        st.markdown("---")
        st.subheader("📥 Download Data")
        # Prepare download data
        download_df = df.copy()
        csv = download_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"disease_surveillance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("""
<div class="footer">
    <p>🏥 <strong>Developed by:</strong> Shuja ul Islam - Data Analyst (WHO)</p>
    <p>📍 Epidemiology Program, Gilgit-Baltistan Health Department</p>
    <p>© 2025 - Disease Surveillance Dashboard | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)

if not uploaded_file:
    st.info("👈 **Upload your XLSX file in the sidebar to start analyzing disease surveillance data**")
    st.markdown("---")
    st.subheader("📋 How to Use:")
    st.markdown("""
    1. **Upload File** - Click in sidebar to upload your disease surveillance XLSX file
    2. **View Dashboards** - Explore 7 different tabs with visualizations
    3. **Generate Reports** - Create summary reports for your boss
    4. **Download Data** - Export analyzed data as CSV
    """)