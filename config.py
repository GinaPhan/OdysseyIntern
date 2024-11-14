import plotly.express as px

# Page configuration
PAGE_CONFIG = {
    "page_title": "COMS Analysis Dashboard",
    "layout": "wide"
}

# Color schemes
COLOR_SCHEMES = {
    'categorical': px.colors.qualitative.Set2,
    'sequential_red': px.colors.sequential.Reds,
    'sequential_blue': px.colors.sequential.Blues,
    'sequential_green': px.colors.sequential.Greens,
    'diverging': px.colors.diverging.RdBu,
    'categorical_bold': px.colors.qualitative.Bold
}

# Score configurations
SCORE_CONFIGS = {
    'SDS': {
        'name': 'Severity of Dependence',
        'max_score': 15,
        'high_risk_threshold': 10,
        'questions': [f'SDSQ{i}' for i in range(1, 6)],
        'higher_is_better': False,
        'color_scheme': 'sequential_red',
        'question_text': [
            'Do you think your use is out of control?',
            'Does missing a dose make you anxious?',
            'Do you worry about your use?',
            'Do you wish you could stop?',
            'How difficult would you find it to stop or go without?'
        ]
    },
    'K10': {
        'name': "Kessler's Psychological Distress",
        'max_score': 50,
        'categories': {
            'Low': (0, 20),
            'Mild': (20, 25),
            'Moderate': (25, 30),
            'Severe': (30, 50)
        },
        'questions': [f'K10Q{i}' for i in range(1, 11)],
        'higher_is_better': False,
        'color_scheme': 'sequential_blue'
    },
    'WHO8': {
        'name': 'Quality of Life',
        'max_score': 40,
        'good_threshold': 30,
        'questions': [f'WHO8Q{i}' for i in range(1, 9)],
        'higher_is_better': True,
        'color_scheme': 'sequential_green',
        'question_text': [
            'How would you rate your quality of life?',
            'How satisfied are you with your health?',
            'Do you have enough energy for everyday life?',
            'How satisfied are you with your ability to perform daily activities?',
            'How satisfied are you with yourself?',
            'How satisfied are you with your personal relationships?',
            'Have you enough money to meet your needs?',
            'How satisfied are you with the conditions of your living place?'
        ]
    }
}

# Chart dimensions
CHART_HEIGHT = {
    'small': 300,
    'medium': 400,
    'large': 500
}

# Column names mapping
METRIC_COLS = {
    'SDS': 'SDSTotalScore',
    'K10': 'K10TotalScore',
    'WHO8': 'WHO8TotalScore'
}

# Score descriptions for insights
SCORE_DESCRIPTIONS = {
    'SDS': """
    The Severity of Dependence Scale (SDS) measures psychological dependence.
    • Score range: 0-15
    • Higher scores indicate greater severity
    • High risk threshold: >10
    """,
    'K10': """
    The Kessler Psychological Distress Scale (K10) measures psychological distress.
    • Score range: 10-50
    • Categories:
      - Low: <20
      - Mild: 20-24
      - Moderate: 25-29
      - Severe: 30+
    """,
    'WHO8': """
    The WHO8 EUROHIS Quality of Life scale measures wellbeing.
    • Score range: 8-40
    • Higher scores indicate better quality of life
    • Good threshold: >30
    """
}

# BBV Risk categories
BBV_RISK_CATEGORIES = {
    'Low': (0, 2),
    'Medium': (2, 4),
    'High': (4, 6)
}