import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

from config import PAGE_CONFIG, COLOR_SCHEMES, SCORE_CONFIGS, CHART_HEIGHT, METRIC_COLS, SCORE_DESCRIPTIONS
from utils import (load_data, calculate_statistics, calculate_client_metrics, 
                  calculate_overview_metrics, calculate_drug_metrics,
                  calculate_monthly_trends, display_comparison_metric,
                  get_latest_records, analyze_client_progress)

# Set page configuration
st.set_page_config(**PAGE_CONFIG)

def show_overview_page(df):
    """Display the overview page with general insights"""
    st.title("COMS Analysis Dashboard")
    
    # Calculate overview metrics
    metrics = calculate_overview_metrics(df)
    
    # Display key metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Clients", f"{metrics['total_clients']:,}")
    col2.metric("Treatment Episodes", f"{metrics['total_episodes']:,}")
    col3.metric("Active Cases", f"{metrics['active_cases']:,}")
    col4.metric("Avg Episodes/Client", f"{metrics['avg_episodes_per_client']:.1f}")
    
    # Drug Distribution Analysis
    st.markdown("### Drug Distribution Analysis")
    
    # Calculate drug metrics
    drug_metrics = df.groupby('SDSDrugOfConcernName').agg({
        'ClientID': 'nunique',
        'SDSTotalScore': 'mean',
        'K10TotalScore': 'mean',
        'WHO8TotalScore': 'mean'
    }).reset_index()
    drug_metrics['Percentage'] = (drug_metrics['ClientID'] / metrics['total_clients'] * 100).round(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Treemap
        fig = px.treemap(
            drug_metrics,
            path=[px.Constant("All Drugs"), 'SDSDrugOfConcernName'],
            values='ClientID',
            color='SDSTotalScore',
            custom_data=['ClientID', 'Percentage', 'SDSTotalScore', 'K10TotalScore', 'WHO8TotalScore'],
            color_continuous_scale=COLOR_SCHEMES['diverging'],
            title="Drug Distribution and Severity Scores"
        )
        fig.update_traces(
            hovertemplate="<b>%{label}</b><br>" +
            "Clients: %{customdata[0]}<br>" +
            "Percentage: %{customdata[1]:.1f}%<br>" +
            "SDS Score: %{customdata[2]:.1f}<br>" +
            "K10 Score: %{customdata[3]:.1f}<br>" +
            "WHO8 Score: %{customdata[4]:.1f}<br>"
        )
        fig.update_layout(height=CHART_HEIGHT['large'])
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Drug ranking bar chart
        fig = px.bar(
            drug_metrics.sort_values('ClientID', ascending=True),
            y='SDSDrugOfConcernName',
            x='ClientID',
            orientation='h',
            title="Drug Rankings by Client Count",
            text='Percentage',
            color='SDSTotalScore',
            color_continuous_scale=COLOR_SCHEMES['diverging']
        )
        fig.update_layout(
            height=CHART_HEIGHT['large'],
            yaxis_title="Drug Type",
            xaxis_title="Number of Clients"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Time series analyses
    st.markdown("### Trend Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 drugs trend
        top_drugs = df['SDSDrugOfConcernName'].value_counts().nlargest(5).index
        df_top = df[df['SDSDrugOfConcernName'].isin(top_drugs)]
        
        monthly_data = df_top.groupby([
            df_top['ServiceContactDate'].dt.strftime('%Y-%m'),
            'SDSDrugOfConcernName']
        )['ClientID'].nunique().unstack(fill_value=0)
        
        fig = go.Figure()
        for i, drug in enumerate(monthly_data.columns):
            fig.add_trace(go.Scatter(
                x=monthly_data.index,
                y=monthly_data[drug],
                name=drug,
                line=dict(color=COLOR_SCHEMES['categorical'][i]),
                mode='lines+markers'
            ))
        
        fig.update_layout(
            height=CHART_HEIGHT['large'],
            title="Top 5 Drugs Trend Over Time",
            xaxis_title="Month",
            yaxis_title="Number of Clients",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly average scores trend
        monthly_scores = df.groupby(df['ServiceContactDate'].dt.strftime('%Y-%m'))[
            ['SDSTotalScore', 'K10TotalScore', 'WHO8TotalScore']
        ].mean()
        
        fig = go.Figure()
        for i, (col, name) in enumerate(zip(
            ['SDSTotalScore', 'K10TotalScore', 'WHO8TotalScore'],
            ['Severity', 'Distress', 'Quality of Life']
        )):
            fig.add_trace(go.Scatter(
                x=monthly_scores.index,
                y=monthly_scores[col],
                name=name,
                line=dict(color=COLOR_SCHEMES['categorical'][i]),
                mode='lines+markers'
            ))
        
        fig.update_layout(
            height=CHART_HEIGHT['large'],
            title="Average Scores Over Time",
            xaxis_title="Month",
            yaxis_title="Score",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Treatment Stage Analysis
    st.markdown("### Treatment Stage Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Treatment stage distribution
        stage_dist = df['StageOfTreatment'].value_counts()
        fig = px.pie(
            values=stage_dist.values,
            names=stage_dist.index,
            title="Distribution of Treatment Stages",
            color_discrete_sequence=COLOR_SCHEMES['categorical_bold']
        )
        fig.update_layout(height=CHART_HEIGHT['medium'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Score comparison by stage
        stage_scores = df.groupby('StageOfTreatment')[
            ['SDSTotalScore', 'K10TotalScore', 'WHO8TotalScore']
        ].mean().round(2)
        
        fig = go.Figure()
        for i, (col, name) in enumerate(zip(
            ['SDSTotalScore', 'K10TotalScore', 'WHO8TotalScore'],
            ['Severity', 'Distress', 'Quality of Life']
        )):
            fig.add_trace(go.Bar(
                name=name,
                x=stage_scores.index,
                y=stage_scores[col],
                text=stage_scores[col],
                textposition='auto'
            ))
        
        fig.update_layout(
            height=CHART_HEIGHT['medium'],
            title="Average Scores by Treatment Stage",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_drug_comparison_page(df):
    """Display the drug comparison page"""
    st.title("Drug Comparison Analysis")
    
    # Drug selection
    selected_drug = st.selectbox(
        "Select drug to analyze:",
        df['SDSDrugOfConcernName'].unique()
    )
    
    # Filter data
    drug_data = df[df['SDSDrugOfConcernName'] == selected_drug]
    other_data = df[df['SDSDrugOfConcernName'] != selected_drug]
    
    # Drug overview metrics
    st.markdown("### Drug Overview")
    metrics = calculate_drug_metrics(df, selected_drug)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Clients", f"{metrics['total_clients']:,}")
    col2.metric("Treatment Episodes", f"{metrics['total_episodes']:,}")
    col3.metric("Active Cases", f"{metrics['active_cases']:,}")
    col4.metric("Completion Rate", f"{metrics['completion_rate']:.1f}%")
    
    # Detailed metrics with color coding
    st.markdown("### Risk Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(display_comparison_metric(
            "High Severity Cases",
            metrics['high_risk_pct'],
            (other_data['SDSTotalScore'] > 10).mean() * 100,
            higher_is_better=False
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(display_comparison_metric(
            "Severe Distress Cases",
            metrics['severe_distress_pct'],
            (other_data['K10TotalScore'] > 30).mean() * 100,
            higher_is_better=False
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(display_comparison_metric(
            "Good Quality of Life",
            metrics['good_qol_pct'],
            (other_data['WHO8TotalScore'] > 30).mean() * 100,
            higher_is_better=True
        ), unsafe_allow_html=True)
    
    # Time series analysis
    st.markdown("### Trends Over Time")
    col1, col2 = st.columns(2)
    
    with col1:
        # Client volume trend
        monthly_volume, _, _, _ = calculate_monthly_trends(drug_data)
        other_monthly, _, _, _ = calculate_monthly_trends(other_data)
        other_monthly = other_monthly / (len(df['SDSDrugOfConcernName'].unique()) - 1)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_volume.index,
            y=monthly_volume.values,
            name=selected_drug,
            line=dict(color=COLOR_SCHEMES['categorical'][0]),
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=other_monthly.index,
            y=other_monthly.values,
            name='Avg Other Drugs',
            line=dict(color=COLOR_SCHEMES['categorical'][1], dash='dash'),
            mode='lines'
        ))
        
        fig.update_layout(
            height=CHART_HEIGHT['large'],
            title="Client Volume Comparison",
            xaxis_title="Month",
            yaxis_title="Number of Clients"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Treatment stage progression
        _, _, monthly_stages, _ = calculate_monthly_trends(drug_data)
        if not monthly_stages.empty:
            fig = px.area(
                monthly_stages,
                title="Treatment Stage Progression",
                labels={'value': 'Number of Clients'},
                color_discrete_sequence=COLOR_SCHEMES['categorical']
            )
            fig.update_layout(height=CHART_HEIGHT['large'])
            st.plotly_chart(fig, use_container_width=True)
    
    # Score distributions
    st.markdown("### Score Distributions")
    fig = make_subplots(rows=1, cols=3, subplot_titles=[config['name'] for config in SCORE_CONFIGS.values()])
    
    for i, (score_type, config) in enumerate(SCORE_CONFIGS.items(), 1):
        metric_col = METRIC_COLS[score_type]
        
        fig.add_trace(
            go.Violin(
                y=drug_data[metric_col],
                name=selected_drug,
                side='positive',
                line_color=COLOR_SCHEMES['categorical'][0],
                showlegend=i==1
            ),
            row=1, col=i
        )
        
        fig.add_trace(
            go.Violin(
                y=other_data[metric_col],
                name='Other Drugs',
                side='negative',
                line_color=COLOR_SCHEMES['categorical'][1],
                showlegend=i==1
            ),
            row=1, col=i
        )
    
    fig.update_layout(height=CHART_HEIGHT['large'], showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Question-level analysis
    st.markdown("### Question-Level Analysis")
    tabs = st.tabs([config['name'] for config in SCORE_CONFIGS.values()])
    
    for tab, (score_type, config) in zip(tabs, SCORE_CONFIGS.items()):
        with tab:
            question_cols = config['questions']
            
            # Calculate average responses
            drug_responses = drug_data[question_cols].mean()
            other_responses = other_data[question_cols].mean()
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name=selected_drug,
                x=question_cols,
                y=drug_responses,
                text=drug_responses.round(2),
                textposition='auto'
            ))
            
            fig.add_trace(go.Bar(
                name='Other Drugs',
                x=question_cols,
                y=other_responses,
                text=other_responses.round(2),
                textposition='auto'
            ))
            
            fig.update_layout(
                barmode='group',
                height=CHART_HEIGHT['medium'],
                title=f"Average Responses by Question - {config['name']}"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # BBV Risk Analysis
    st.markdown("### BBV Risk Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk distribution
        drug_data['BBV_Risk'] = drug_data[['BBVQ1', 'BBVQ2', 'BBVQ3', 'BBVQ4']].mean(axis=1)
        other_data['BBV_Risk'] = other_data[['BBVQ1', 'BBVQ2', 'BBVQ3', 'BBVQ4']].mean(axis=1)
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=drug_data['BBV_Risk'],
            name=selected_drug,
            nbinsx=20,
            opacity=0.75
        ))
        fig.add_trace(go.Histogram(
            x=other_data['BBV_Risk'],
            name='Other Drugs',
            nbinsx=20,
            opacity=0.75
        ))
        
        fig.update_layout(
            barmode='overlay',
            height=CHART_HEIGHT['medium'],
            title="BBV Risk Score Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk categories comparison
        drug_data['Risk_Category'] = pd.cut(
            drug_data['BBV_Risk'],
            bins=[0, 2, 4, 6],
            labels=['Low', 'Medium', 'High']
        )
        other_data['Risk_Category'] = pd.cut(
            other_data['BBV_Risk'],
            bins=[0, 2, 4, 6],
            labels=['Low', 'Medium', 'High']
        )
        
        drug_risk_dist = drug_data['Risk_Category'].value_counts(normalize=True) * 100
        other_risk_dist = other_data['Risk_Category'].value_counts(normalize=True) * 100
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Low', 'Medium', 'High'],
            y=drug_risk_dist,
            name=selected_drug,
            text=drug_risk_dist.round(1),
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            x=['Low', 'Medium', 'High'],
            y=other_risk_dist,
            name='Other Drugs',
            text=other_risk_dist.round(1),
            textposition='auto'
        ))
        
        fig.update_layout(
            barmode='group',
            height=CHART_HEIGHT['medium'],
            title="Risk Category Distribution (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_client_comparison_page(df):
    """Display the client comparison page"""
    st.title("Individual Client Analysis")
    
    # Client selection
    selected_client = st.selectbox(
        "Select client ID:",
        df['ClientID'].unique()
    )
    
    # Filter and sort data
    client_data = df[df['ClientID'] == selected_client].sort_values('ServiceContactDate')
    other_data = df[df['ClientID'] != selected_client]
    
    if len(client_data) == 0:
        st.error("No data found for selected client")
        return
    
    # Get latest record for current status
    latest_record = client_data.iloc[-1]
    
    # Client overview
    st.markdown("### Client Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    treatment_duration = (client_data['ServiceContactDate'].max() - 
                        client_data['ServiceContactDate'].min()).days
    
    with col1:
        st.metric("Drug of Concern", latest_record['SDSDrugOfConcernName'])
    with col2:
        st.metric("Current Stage", latest_record['StageOfTreatment'])
    with col3:
        st.metric("Total Episodes", len(client_data))
    with col4:
        st.metric("Days in Treatment", f"{treatment_duration}")
    
    # Current Status vs Population
    st.markdown("### Current Status")
    metrics_html = []
    
    for score_type, config in SCORE_CONFIGS.items():
        metric_col = METRIC_COLS[score_type]
        metrics_html.append(
            display_comparison_metric(
                config['name'],
                latest_record[metric_col],
                other_data[metric_col].mean(),
                higher_is_better=config['higher_is_better']
            )
        )
    
    st.markdown("\n".join(metrics_html), unsafe_allow_html=True)
    
    # Score breakdown
    st.markdown("### Score Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        # SDS Question breakdown
        sds_scores = pd.DataFrame({
            'Question': [f'Q{i}' for i in range(1, 6)],
            'Score': [latest_record[f'SDSQ{i}'] for i in range(1, 6)],
            'Pop_Avg': [other_data[f'SDSQ{i}'].mean() for i in range(1, 6)]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Client',
            x=sds_scores['Question'],
            y=sds_scores['Score'],
            text=sds_scores['Score'],
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name='Population Average',
            x=sds_scores['Question'],
            y=sds_scores['Pop_Avg'],
            text=sds_scores['Pop_Avg'].round(2),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="SDS Question Breakdown",
            height=CHART_HEIGHT['medium'],
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # K10 Question breakdown
        k10_scores = pd.DataFrame({
            'Question': [f'Q{i}' for i in range(1, 11)],
            'Score': [latest_record[f'K10Q{i}'] for i in range(1, 11)],
            'Pop_Avg': [other_data[f'K10Q{i}'].mean() for i in range(1, 11)]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Client',
            x=k10_scores['Question'],
            y=k10_scores['Score'],
            text=k10_scores['Score'],
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name='Population Average',
            x=k10_scores['Question'],
            y=k10_scores['Pop_Avg'],
            text=k10_scores['Pop_Avg'].round(2),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="K10 Question Breakdown",
            height=CHART_HEIGHT['medium'],
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # WHO8 Analysis
    st.markdown("### Quality of Life Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # WHO8 radar chart
        who8_scores = [latest_record[f'WHO8Q{i}'] for i in range(1, 9)]
        who8_pop_avg = [other_data[f'WHO8Q{i}'].mean() for i in range(1, 9)]
        who8_labels = [f'Q{i}' for i in range(1, 9)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=who8_scores,
            theta=who8_labels,
            fill='toself',
            name='Client'
        ))
        fig.add_trace(go.Scatterpolar(
            r=who8_pop_avg,
            theta=who8_labels,
            fill='toself',
            name='Population Average'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=True,
            title="WHO8 Score Breakdown"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # BBV Risk Analysis
        bbv_scores = [latest_record[f'BBVQ{i}'] for i in range(1, 5)]
        bbv_pop_avg = [other_data[f'BBVQ{i}'].mean() for i in range(1, 5)]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Client',
            x=['Q1', 'Q2', 'Q3', 'Q4'],
            y=bbv_scores,
            text=bbv_scores,
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name='Population Average',
            x=['Q1', 'Q2', 'Q3', 'Q4'],
            y=bbv_pop_avg,
            text=[f"{x:.2f}" for x in bbv_pop_avg],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="BBV Risk Scores",
            height=CHART_HEIGHT['medium'],
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Progress Analysis
    if len(client_data) > 1:
        st.markdown("### Progress Over Time")
        
        # Score progress
        fig = go.Figure()
        for score_type, config in SCORE_CONFIGS.items():
            metric_col = METRIC_COLS[score_type]
            fig.add_trace(go.Scatter(
                x=client_data['ServiceContactDate'],
                y=client_data[metric_col],
                name=config['name'],
                mode='lines+markers'
            ))
        
        fig.update_layout(
            height=CHART_HEIGHT['medium'],
            title="Score Progress Over Time",
            xaxis_title="Date",
            yaxis_title="Score"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Progress summary
        progress = analyze_client_progress(client_data)
        
        col1, col2, col3 = st.columns(3)
        for i, (score_type, data) in enumerate(progress.items()):
            col = [col1, col2, col3][i]
            with col:
                # Adjust delta color based on metric type and change direction
                if score_type == 'WHO8':  # Quality of Life
                    # For WHO8, improvement is when score increases
                    delta_color = "normal" if data['change'] > 0 else "inverse"
                else:  # SDS and K10
                    # For SDS and K10, improvement is when score decreases
                    delta_color = "normal" if data['change'] < 0 else "inverse"
                
                col.metric(
                    SCORE_CONFIGS[score_type]['name'],
                    f"{data['current_score']:.1f}",
                    f"{data['change']:+.1f} ({data['pct_change']:+.1f}%)",
                    delta_color=delta_color
                )

def main():
    """Main application entry point"""
    try:
        # Load data
        df = load_data()
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Select Analysis Type",
            ["Overview", "Drug Comparison", "Client Comparison"]
        )
        
        # Add date filter in sidebar
        st.sidebar.markdown("### Date Range Filter")
        date_range = st.sidebar.date_input(
            "Select date range",
            value=(df['ServiceContactDate'].min().date(), 
                  df['ServiceContactDate'].max().date()),
            min_value=df['ServiceContactDate'].min().date(),
            max_value=df['ServiceContactDate'].max().date()
        )
        
        # Filter data based on date range
        if len(date_range) == 2:
            mask = (df['ServiceContactDate'].dt.date >= date_range[0]) & \
                  (df['ServiceContactDate'].dt.date <= date_range[1])
            df = df[mask]
        
        # Add data quality checks in sidebar
        if st.sidebar.checkbox("Show Data Quality Info"):
            st.sidebar.markdown("### Data Quality")
            missing_data = df.isnull().sum()
            if missing_data.any():
                st.sidebar.warning("Missing values detected")
                st.sidebar.write(missing_data[missing_data > 0])
            else:
                st.sidebar.success("No missing values found")
        
        # Display selected page
        if page == "Overview":
            show_overview_page(df)
        elif page == "Drug Comparison":
            show_drug_comparison_page(df)
        else:
            show_client_comparison_page(df)
            
        # Add footer with additional information
        st.sidebar.markdown("---")
        st.sidebar.markdown("### About the Metrics")
        for score_type, description in SCORE_DESCRIPTIONS.items():
            if st.sidebar.checkbox(f"About {score_type}"):
                st.sidebar.markdown(description)
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Error details:", e.__class__.__name__)
        
        # Show detailed error information in expandable section
        with st.expander("Show Debug Information"):
            st.write("Exception details:", str(e))
            st.write("\nDataFrame Info:")
            if 'df' in locals():
                st.write(df.info())
            st.write("\nPlease check your data and try again")

if __name__ == "__main__":
    main()