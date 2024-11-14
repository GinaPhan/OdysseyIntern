import pandas as pd
import numpy as np
from scipy import stats
from config import SCORE_CONFIGS, METRIC_COLS, BBV_RISK_CATEGORIES

def load_data():
    """Load and preprocess the COMS data"""
    df = pd.read_excel("Evaluating Outcomes.xlsx")
    df['ServiceContactDate'] = pd.to_datetime(df['ServiceContactDate'], format='%d/%m/%Y', dayfirst=True)
    # Sort by date and client ID for consistent analysis
    df = df.sort_values(['ClientID', 'ServiceContactDate'])
    return df

def get_latest_records(df, group_col='ClientID'):
    """Get the latest record for each group"""
    return df.loc[df.groupby(group_col)['ServiceContactDate'].idxmax()]

def calculate_overview_metrics(df):
    """Calculate main overview metrics"""
    latest_records = get_latest_records(df)
    return {
        'total_clients': df['ClientID'].nunique(),
        'total_episodes': df['TreatmentEpisodeID'].nunique(),
        'unique_drugs': df['SDSDrugOfConcernName'].nunique(),
        'active_cases': len(latest_records[latest_records['StageOfTreatment'].str.contains('Treatment', na=False)]),
        'avg_episodes_per_client': df['TreatmentEpisodeID'].nunique() / df['ClientID'].nunique()
    }

def calculate_drug_metrics(df, drug_name):
    """Calculate comprehensive metrics for a specific drug"""
    drug_data = df[df['SDSDrugOfConcernName'] == drug_name]
    latest_records = get_latest_records(drug_data)
    
    total_clients = drug_data['ClientID'].nunique()
    treatment_clients = len(latest_records[latest_records['StageOfTreatment'].str.contains('Treatment', na=False)])
    
    return {
        'total_clients': total_clients,
        'total_episodes': drug_data['TreatmentEpisodeID'].nunique(),
        'active_cases': treatment_clients,
        'completion_rate': (treatment_clients / total_clients * 100) if total_clients > 0 else 0,
        'avg_episodes': drug_data['TreatmentEpisodeID'].nunique() / total_clients if total_clients > 0 else 0,
        'avg_severity': drug_data['SDSTotalScore'].mean(),
        'avg_distress': drug_data['K10TotalScore'].mean(),
        'avg_qol': drug_data['WHO8TotalScore'].mean(),
        'high_risk_pct': (drug_data['SDSTotalScore'] > 10).mean() * 100,
        'severe_distress_pct': (drug_data['K10TotalScore'] > 30).mean() * 100,
        'good_qol_pct': (drug_data['WHO8TotalScore'] > 30).mean() * 100
    }

def calculate_monthly_trends(df, selected_drug=None):
    """Calculate monthly trends for visualization"""
    if selected_drug:
        data = df[df['SDSDrugOfConcernName'] == selected_drug]
    else:
        data = df
    
    # Client volume trend
    monthly_volume = data.groupby(
        data['ServiceContactDate'].dt.strftime('%Y-%m')
    )['ClientID'].nunique()
    
    # Score trends
    monthly_scores = data.groupby(
        data['ServiceContactDate'].dt.strftime('%Y-%m')
    )[['SDSTotalScore', 'K10TotalScore', 'WHO8TotalScore']].mean()
    
    # Treatment stage progression
    monthly_stages = data.groupby(
        [data['ServiceContactDate'].dt.strftime('%Y-%m'), 'StageOfTreatment']
    ).size().unstack(fill_value=0)
    
    # Risk categories over time
    data['BBV_Risk'] = data[['BBVQ1', 'BBVQ2', 'BBVQ3', 'BBVQ4']].mean(axis=1)
    data['Risk_Category'] = pd.cut(
        data['BBV_Risk'],
        bins=[0, 2, 4, 6],
        labels=['Low', 'Medium', 'High']
    )
    monthly_risk = data.groupby(
        [data['ServiceContactDate'].dt.strftime('%Y-%m'), 'Risk_Category']
    ).size().unstack(fill_value=0)
    
    return monthly_volume, monthly_scores, monthly_stages, monthly_risk

def calculate_statistics(group1, group2):
    """Calculate statistical comparison between two groups"""
    if len(group1) < 2 or len(group2) < 2:
        return {
            'mean_diff': np.nan,
            'significance': 'Insufficient data',
            'p_value': np.nan,
            'effect_size': np.nan,
            'mean1': np.nan,
            'mean2': np.nan
        }
    
    try:
        # Remove NaN values
        group1 = group1.dropna()
        group2 = group2.dropna()
        
        if len(group1) < 2 or len(group2) < 2:
            return {
                'mean_diff': np.nan,
                'significance': 'Insufficient data after removing NaN values',
                'p_value': np.nan,
                'effect_size': np.nan,
                'mean1': np.nan,
                'mean2': np.nan
            }
        
        mean1 = group1.mean()
        mean2 = group2.mean()
        mean_diff = mean1 - mean2
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(group1, group2)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(group1) - 1) * group1.var() + 
                            (len(group2) - 1) * group2.var()) / 
                           (len(group1) + len(group2) - 2))
        
        effect_size = mean_diff / pooled_std if pooled_std != 0 else 0
        
        return {
            'mean_diff': mean_diff,
            'significance': 'Significant' if p_value < 0.05 else 'Not significant',
            'p_value': p_value,
            'effect_size': effect_size,
            'mean1': mean1,
            'mean2': mean2
        }
    except Exception as e:
        return {
            'mean_diff': np.nan,
            'significance': f'Error in calculation: {str(e)}',
            'p_value': np.nan,
            'effect_size': np.nan,
            'mean1': np.nan,
            'mean2': np.nan
        }

def calculate_client_metrics(client_score, population_scores):
    """Calculate metrics comparing a client score to population distribution"""
    try:
        clean_scores = population_scores.dropna()
        
        if len(clean_scores) < 2:
            return {
                'client_score': client_score,
                'pop_mean': np.nan,
                'pop_std': np.nan,
                'percentile': np.nan,
                'z_score': np.nan
            }
        
        pop_mean = clean_scores.mean()
        pop_std = clean_scores.std()
        
        # Calculate percentile and z-score
        percentile = stats.percentileofscore(clean_scores, client_score)
        z_score = (client_score - pop_mean) / pop_std if pop_std != 0 else 0
        
        return {
            'client_score': client_score,
            'pop_mean': pop_mean,
            'pop_std': pop_std,
            'percentile': percentile,
            'z_score': z_score
        }
    except Exception as e:
        return {
            'client_score': client_score,
            'pop_mean': np.nan,
            'pop_std': np.nan,
            'percentile': np.nan,
            'z_score': np.nan
        }

def analyze_client_progress(client_data):
    """Analyze client progress over time"""
    first_record = client_data.iloc[0]
    latest_record = client_data.iloc[-1]
    
    progress = {}
    for score_type, config in SCORE_CONFIGS.items():
        col = METRIC_COLS[score_type]
        initial_score = first_record[col]
        current_score = latest_record[col]
        change = current_score - initial_score
        
        # Determine if change is improvement based on score type
        is_improvement = (change < 0) if not config['higher_is_better'] else (change > 0)
        
        progress[score_type] = {
            'initial_score': initial_score,
            'current_score': current_score,
            'change': change,
            'pct_change': (change / initial_score * 100) if initial_score != 0 else np.nan,
            'is_improvement': is_improvement
        }
    
    return progress

def display_comparison_metric(label, value, comparison_value, format='.1f', higher_is_better=False):
    """Create HTML for displaying comparison metrics with colors"""
    if pd.isna(value) or pd.isna(comparison_value):
        return f"""
        <div style="margin-bottom: 10px; padding: 10px; border-radius: 5px; background-color: rgba(0,0,0,0.05);">
            <span style="font-size: 1.1em; font-weight: bold;">{label}</span><br/>
            <span style="font-size: 1.2em;">Insufficient data</span>
        </div>
        """
    
    diff = value - comparison_value
    diff_pct = (diff / comparison_value * 100)
    
    # Determine if the difference is "good" or "bad"
    if higher_is_better:
        color = "green" if diff > 0 else "red"
        arrow = "↑" if diff > 0 else "↓"
    else:
        color = "red" if diff > 0 else "green"
        arrow = "↑" if diff > 0 else "↓"
    
    return f"""
    <div style="margin-bottom: 10px; padding: 10px; border-radius: 5px; background-color: rgba(0,0,0,0.05);">
        <span style="font-size: 1.1em; font-weight: bold;">{label}</span><br/>
        <span style="font-size: 1.2em;">{value:{format}}</span>
        <span style="color: {color}; margin-left: 10px; font-weight: bold;">
            {arrow} {abs(diff):{format}} ({abs(diff_pct):.1f}%)
        </span>
    </div>
    """