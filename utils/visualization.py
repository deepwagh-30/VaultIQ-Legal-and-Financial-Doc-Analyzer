# utils/visualization.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords

# Download required NLTK resources
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def create_visualizations(text, financial_results, legal_results):
    """Create visualizations based on the document analysis"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Create word cloud
        generate_word_cloud(text)
        
    with col2:
        # Create risk heatmap
        create_risk_heatmap(legal_results)
    
    # Create financial charts if metrics are available
    if financial_results["metrics"]:
        create_financial_charts(financial_results)
    
    # Generate entity relationship graph
    if legal_results["contract_info"]["parties"]:
        create_entity_relationship_graph(legal_results)

def generate_word_cloud(text):
    """Generate and display a word cloud from the document text"""
    stop_words = set(stopwords.words('english'))
    
    # Add custom stop words relevant to legal/financial documents
    custom_stop_words = {
        'shall', 'will', 'may', 'must', 'the', 'and', 'this', 'that',
        'section', 'article', 'agreement', 'contract', 'page', 'date'
    }
    stop_words.update(custom_stop_words)
    
    # Process text to remove stop words
    words = text.lower().split()
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
    processed_text = ' '.join(filtered_words)
    
    # Generate word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        contour_width=1,
        contour_color='steelblue',
        max_words=100
    ).generate(processed_text)
    
    # Display the word cloud using matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(plt)
    st.caption("Word Cloud: Key terms frequency in document")

def create_risk_heatmap(legal_results):
    """Create a heatmap of risk categories found in the document"""
    risk_categories = list(legal_results["risk_clauses"].keys())
    
    # Convert risk levels to numeric values for the heatmap
    risk_values = []
    risk_levels = {'Low': 1, 'Medium': 2, 'High': 3, 'Not Found': 0}
    
    for category in risk_categories:
        if legal_results["risk_clauses"][category]["found"]:
            level = legal_results["risk_clauses"][category]["risk_level"]
            risk_values.append(risk_levels.get(level, 0))
        else:
            risk_values.append(risk_levels['Not Found'])
    
    # Create a DataFrame for the heatmap
    df = pd.DataFrame({
        'Category': risk_categories,
        'Risk Level': risk_values
    })
    
    # Create color scale
    colors = ['#e0f7fa', '#80deea', '#ffab91', '#ff7043']
    
    # Create the heatmap with Plotly
    fig = go.Figure(data=go.Heatmap(
        z=[risk_values],
        y=['Risk Assessment'],
        x=risk_categories,
        colorscale=[
            [0, '#e0f7fa'],  # Not Found - Light Blue
            [0.33, '#81c784'],  # Low - Green
            [0.66, '#ffb74d'],  # Medium - Orange
            [1, '#e57373']   # High - Red
        ],
        showscale=False
    ))
    
    fig.update_layout(
        title='Risk Assessment by Category',
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_financial_charts(financial_results):
    """Create charts for financial metrics"""
    st.subheader("Financial Metrics Visualization")
    
    # Extract financial metrics
    metrics = financial_results["metrics"]
    
    # Create bar chart for financial metrics
    if metrics:
        df = pd.DataFrame({
            'Metric': list(metrics.keys()),
            'Value': [float(str(v).replace(',', '').replace('$', '')) if v and isinstance(v, (str, int, float)) else 0 
                     for v in metrics.values()]
        })
        
        fig = px.bar(
            df, 
            x='Metric', 
            y='Value', 
            title='Key Financial Metrics',
            color='Value',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        
        fig.update_layout(
            xaxis_title='',
            yaxis_title='Value ($)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # If trend data exists, show it
    if financial_results.get("trends") and any(financial_results["trends"].values()):
        create_trend_chart(financial_results["trends"])

def create_trend_chart(trends):
    """Create a line chart for financial trends over time"""
    # Convert trend data to DataFrame
    periods = []
    metrics = {}
    
    for metric, trend_data in trends.items():
        if trend_data:
            for period, value in trend_data.items():
                if period not in periods:
                    periods.append(period)
                if metric not in metrics:
                    metrics[metric] = {}
                metrics[metric][period] = value
    
    # Create DataFrame for plotting
    df_list = []
    for metric, values in metrics.items():
        for period, value in values.items():
            df_list.append({
                'Metric': metric,
                'Period': period,
                'Value': float(str(value).replace(',', '').replace('$', '')) if value else 0
            })
    
    if df_list:
        df = pd.DataFrame(df_list)
        
        fig = px.line(
            df, 
            x='Period', 
            y='Value', 
            color='Metric',
            title='Financial Metrics Over Time',
            markers=True
        )
        
        fig.update_layout(
            xaxis_title='Time Period',
            yaxis_title='Value ($)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def create_entity_relationship_graph(legal_results):
    """Create a network graph of entities and their relationships"""
    parties = legal_results["contract_info"]["parties"]
    
    if len(parties) < 2:
        return
    
    # Create relationships between parties (assuming all parties are related)
    edges = []
    for i in range(len(parties)):
        for j in range(i+1, len(parties)):
            edges.append((parties[i], parties[j]))
    
    # Create a DataFrame for edges
    edge_df = pd.DataFrame(edges, columns=['source', 'target'])
    
    # Create a Plotly figure
    fig = go.Figure()
    
    # Create the nodes
    node_x = []
    node_y = []
    for i, party in enumerate(parties):
        angle = 2 * np.pi * i / len(parties)
        node_x.append(np.cos(angle))
        node_y.append(np.sin(angle))
    
    # Add nodes to the figure
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=parties,
        textposition="top center",
        marker=dict(
            size=30,
            color='royalblue',
            line=dict(width=2, color='darkblue')
        ),
        name='Entities'
    ))
    
    # Add edges to the figure
    for i, row in edge_df.iterrows():
        source_idx = parties.index(row['source'])
        target_idx = parties.index(row['target'])
        
        fig.add_trace(go.Scatter(
            x=[node_x[source_idx], node_x[target_idx]],
            y=[node_y[source_idx], node_y[target_idx]],
            mode='lines',
            line=dict(width=2, color='gray'),
            showlegend=False
        ))
    
    fig.update_layout(
        title='Contract Parties Relationship',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)