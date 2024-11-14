# COMS Analysis Dashboard

A comprehensive dashboard for analyzing Client Outcomes Management System (COMS) data in the AOD sector.

## Overview

This dashboard analyzes three key assessment components:
1. Severity of Dependence Scale (SDS)
2. Kessler's Psychological Distress Scale (K10)
3. WHO8 EUROHIS Quality of Life Scale

## Features

### Overview Page
- Key metrics including total clients, treatment episodes, and active cases
- Drug distribution analysis with interactive treemaps and bar charts
- Trend analysis showing drug usage patterns over time
- Treatment stage analysis with distribution visualizations

### Drug Comparison Page
- Detailed analysis of specific drugs compared to overall population
- Risk analysis with color-coded metrics
- Time series analysis of client volumes and treatment stages
- Score distributions with violin plots
- Question-level analysis for each assessment tool
- BBV Risk analysis

### Client Comparison Page
- Individual client progress tracking
- Score comparisons against population averages
- Detailed breakdown of assessment responses
- Progress visualization over time
- BBV risk factor analysis

## Technical Architecture

### Files Structure
- `main.py`: Core application logic and UI components
- `config.py`: Configuration settings and constants
- `utils.py`: Helper functions and data processing utilities

### Key Components

#### Configuration (`config.py`)
- Page settings
- Color schemes
- Score configurations
- Chart dimensions
- Metric column mappings
- Score descriptions

#### Utilities (`utils.py`)
- Data loading and preprocessing
- Statistical calculations
- Metric computations
- Progress analysis
- Visualization helpers

#### Main Application (`main.py`)
- Page routing
- Data visualization
- Interactive components
- Error handling

## Scoring System

### SDS (Severity of Dependence)
- Maximum score: 15
- Scoring: 0-3 per question
- High risk threshold: 10

### K10 (Psychological Distress)
- Maximum score: 50
- Categories:
  - Low: <20
  - Mild: 20-24
  - Moderate: 25-29
  - Severe: 30+

### WHO8 (Quality of Life)
- Maximum score: 40
- Scoring: 1-5 per question
- Good threshold: >30

## Dependencies
- Streamlit: Web application framework
- Plotly: Interactive visualizations
- Pandas: Data manipulation
- NumPy: Numerical operations
- SciPy: Statistical calculations

## Usage

1. Place the dataset "Evaluating Outcomes.xlsx" in the same directory
2. Install required dependencies
3. Run the application:
```bash
streamlit run main.py
```

## Data Handling
- Automatic data preprocessing
- Date range filtering
- Data quality checks
- Missing value handling
- Statistical analysis

## Visualization Features
- Interactive charts
- Color-coded metrics
- Comparative analysis
- Time series tracking
- Risk assessment visualizations

## Error Handling
- Comprehensive error catching
- Detailed error reporting
- Data validation
- Graceful fallbacks