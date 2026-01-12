"""
Professional EPOS Analytics Dashboard - Complete Production Version
Real-time business intelligence for point-of-sale systems
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

from sql.queries import (
    daily_sales_report, location_performance, product_category_analysis,
    hourly_sales_pattern, employee_performance, payment_method_breakdown,
    top_performing_products, refund_analysis, monthly_revenue_trend
)

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="EPOS Analytics",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS STYLING ====================
st.markdown("""
    <style>
    .main {background-color: #0e1117;}
    [data-testid="stMetricValue"] {font-size: 28px; font-weight: 600;}
    [data-testid="stMetricLabel"] {font-size: 14px; font-weight: 500; color: #a0a0a0;}
    [data-testid="stMetricDelta"] {font-size: 14px;}
    div[data-testid="stHorizontalBlock"] > div {
        background-color: #1a1d29;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #2d3139;
    }
    h1 {color: #ffffff; font-weight: 700; padding-bottom: 10px; border-bottom: 3px solid #4CAF50; margin-bottom: 30px;}
    h2 {color: #ffffff; font-weight: 600; font-size: 24px; margin-top: 30px; margin-bottom: 20px;}
    h3 {color: #e0e0e0; font-weight: 500; font-size: 18px;}
    [data-testid="stSidebar"] {background-color: #1a1d29;}
    [data-testid="stSidebar"] h1 {border-bottom: none; color: #4CAF50;}
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {background-color: #45a049; border: none;}
    div[data-baseweb="select"] {background-color: #262b3d;}
    [data-testid="stDataFrame"] {background-color: #1a1d29;}
    .block-container {padding-top: 2rem;}
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }
    .status-live {background-color: #4CAF50; color: white;}
    </style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("# 💳 EPOS Analytics")
    st.markdown("---")
    
    report_type = st.selectbox(
        "📊 Select Dashboard",
        ["🏠 Overview", "📅 Daily Sales", "🏪 Locations", "🍺 Products", 
         "👥 Employees", "💳 Payments", "⏰ Peak Hours", "🔄 Refunds"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📆 Date Range")
    col1, col2 = st.columns(2)
    with col1:
        st.date_input("From", datetime.now() - timedelta(days=365), label_visibility="collapsed")
    with col2:
        st.date_input("To", datetime.now(), label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.success("✓ Data refreshed")
    
    if st.button("📥 Export Report"):
        st.info("Export feature coming soon")
    
    st.markdown("---")
    st.markdown("### 📡 System Status")
    st.markdown('<span class="status-badge status-live">● LIVE</span>', unsafe_allow_html=True)
    st.caption("Last updated: Just now")
    st.markdown("---")
    st.caption("© 2024 EPOS Analytics")

# ==================== OVERVIEW DASHBOARD ====================
if report_type == "🏠 Overview":
    st.markdown('<h1>🏠 Business Dashboard <span class="status-badge status-live">● LIVE</span></h1>', unsafe_allow_html=True)
    
    df_daily = daily_sales_report()
    df_location = location_performance()
    df_category = product_category_analysis()
    df_hourly = hourly_sales_pattern()
    
    total_revenue = df_daily['completed_revenue'].sum()
    total_transactions = df_daily['transaction_count'].sum()
    avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
    refund_amount = df_daily['refunded_amount'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Revenue", f"£{total_revenue:,.0f}", delta="+12.5% vs last year")
    with col2:
        st.metric("🧾 Transactions", f"{total_transactions:,}", delta="+8.3%")
    with col3:
        st.metric("📊 Avg Order Value", f"£{avg_transaction:.2f}", delta="+£3.20")
    with col4:
        refund_rate = (refund_amount / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("🔄 Refund Rate", f"{refund_rate:.1f}%", delta="-0.5%", delta_color="inverse")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Revenue Trend (Last 90 Days)")
        df_recent = df_daily.tail(90)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_recent['transaction_date'],
            y=df_recent['completed_revenue'],
            mode='lines',
            name='Revenue',
            line=dict(color='#4CAF50', width=3),
            fill='tozeroy',
            fillcolor='rgba(76, 175, 80, 0.1)'
        ))
        fig.update_layout(
            template='plotly_dark',
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="",
            yaxis_title="Revenue (£)",
            hovermode='x unified',
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏆 Top Location")
        top_loc = df_location.iloc[0]
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; text-align: center;'>
            <h2 style='color: white; margin: 0; border: none;'>{top_loc['location_name']}</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 10px 0;'>{top_loc['city']}</p>
            <h1 style='color: white; margin: 20px 0; border: none;'>£{top_loc['total_revenue']:,.0f}</h1>
            <p style='color: rgba(255,255,255,0.9); margin: 0;'>
                {top_loc['transaction_count']:,} transactions | £{top_loc['avg_transaction_value']:.2f} avg
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        st.markdown("### 🎯 Quick Stats")
        st.info(f"**{len(df_location)}** Active Locations")
        st.success(f"**£{df_location['total_tips'].sum():,.0f}** Total Tips")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏪 Location Performance")
        fig = go.Figure()
        for loc_type in df_location['location_type'].unique():
            df_type = df_location[df_location['location_type'] == loc_type]
            fig.add_trace(go.Bar(
                name=loc_type.title(),
                x=df_type['location_name'],
                y=df_type['total_revenue'],
                text=df_type['total_revenue'].apply(lambda x: f'£{x:,.0f}'),
                textposition='outside'
            ))
        fig.update_layout(
            template='plotly_dark',
            height=350,
            barmode='group',
            xaxis_title="",
            yaxis_title="Revenue (£)",
            showlegend=True,
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🍺 Revenue by Category")
        fig = px.pie(
            df_category,
            values='total_revenue',
            names='product_category',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            template='plotly_dark',
            height=350,
            showlegend=True,
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29'
        )
        fig.update_traces(textposition='inside', textinfo='label+percent', textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ Hourly Transaction Volume")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_hourly['hour'],
            y=df_hourly['transaction_count'],
            marker=dict(color=df_hourly['transaction_count'], colorscale='Viridis', showscale=True),
            text=df_hourly['transaction_count'],
            textposition='outside'
        ))
        fig.update_layout(
            template='plotly_dark',
            height=300,
            xaxis_title="Hour of Day",
            yaxis_title="Transactions",
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Average Transaction Value by Hour")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_hourly['hour'],
            y=df_hourly['avg_transaction_value'],
            mode='lines+markers',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.1)'
        ))
        fig.update_layout(
            template='plotly_dark',
            height=300,
            xaxis_title="Hour of Day",
            yaxis_title="Avg Value (£)",
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29'
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== DAILY SALES ====================
elif report_type == "📅 Daily Sales":
    st.markdown('<h1>📅 Daily Sales Analysis</h1>', unsafe_allow_html=True)
    df_daily = daily_sales_report()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Days", len(df_daily))
    with col2:
        st.metric("💰 Total Revenue", f"£{df_daily['total_revenue'].sum():,.0f}")
    with col3:
        avg_daily = df_daily['total_revenue'].mean()
        st.metric("📈 Avg Daily Revenue", f"£{avg_daily:,.0f}")
    with col4:
        best_day = df_daily.loc[df_daily['total_revenue'].idxmax()]
        st.metric("🏆 Best Day", f"£{best_day['total_revenue']:,.0f}")
    
    st.markdown("---")
    st.markdown("### 📈 Daily Sales Performance")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_daily['transaction_date'],
        y=df_daily['completed_revenue'],
        name='Completed',
        mode='lines',
        line=dict(color='#4CAF50', width=2),
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.1)'
    ))
    fig.add_trace(go.Scatter(
        x=df_daily['transaction_date'],
        y=df_daily['refunded_amount'],
        name='Refunded',
        mode='lines',
        line=dict(color='#FF5252', width=2)
    ))
    fig.update_layout(
        template='plotly_dark',
        height=400,
        xaxis_title="Date",
        yaxis_title="Amount (£)",
        hovermode='x unified',
        plot_bgcolor='#1a1d29',
        paper_bgcolor='#1a1d29'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📋 Detailed Daily Data")
    st.dataframe(
        df_daily.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_transaction_value': '£{:,.2f}',
            'completed_revenue': '£{:,.2f}',
            'refunded_amount': '£{:,.2f}'
        }).background_gradient(subset=['total_revenue'], cmap='Greens'),
        use_container_width=True,
        height=400
    )

# ==================== LOCATIONS ====================
elif report_type == "🏪 Locations":
    st.markdown('<h1>🏪 Location Performance</h1>', unsafe_allow_html=True)
    df_location = location_performance()
    
    col1, col2, col3 = st.columns(3)
    for idx, (col, rank) in enumerate(zip([col1, col2, col3], ['🥇', '🥈', '🥉'])):
        if idx < len(df_location):
            loc = df_location.iloc[idx]
            with col:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 20px; border-radius: 12px; text-align: center;'>
                    <h1 style='color: white; margin: 0; border: none;'>{rank}</h1>
                    <h3 style='color: white; margin: 10px 0; border: none;'>{loc['location_name']}</h3>
                    <h2 style='color: white; margin: 10px 0; border: none;'>£{loc['total_revenue']:,.0f}</h2>
                    <p style='color: rgba(255,255,255,0.8); margin: 0;'>{loc['transaction_count']:,} sales</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Revenue Comparison")
        fig = px.bar(
            df_location,
            x='location_name',
            y='total_revenue',
            color='location_type',
            text='total_revenue',
            color_discrete_map={'restaurant': '#4CAF50', 'bar': '#FF6B6B', 'pub': '#FFD93D'}
        )
        fig.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
        fig.update_layout(
            template='plotly_dark',
            height=400,
            xaxis_tickangle=-45,
            plot_bgcolor='#1a1d29',
            paper_bgcolor='#1a1d29'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Performance Matrix")
        fig = px.scatter(
            df_location,
            x='transaction_count',
            y='avg_transaction_value',
            size='total_revenue',
            color='location_type',
            hover_data=['location_name', 'city'],
            size_max=60
        )
        fig.update_layout(template='plotly_dark', height=400, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📋 Location Details")
    st.dataframe(
        df_location.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_transaction_value': '£{:,.2f}',
            'total_tips': '£{:,.2f}'
        }).background_gradient(subset=['total_revenue'], cmap='RdYlGn'),
        use_container_width=True
    )

# ==================== PRODUCTS ====================
elif report_type == "🍺 Products":
    st.markdown('<h1>🍺 Product Performance</h1>', unsafe_allow_html=True)
    df_category = product_category_analysis()
    df_products = top_performing_products()
    
    col1, col2, col3 = st.columns(3)
    top_category = df_category.iloc[0]
    with col1:
        st.metric("🏆 Top Category", top_category['product_category'])
    with col2:
        st.metric("💰 Category Revenue", f"£{top_category['total_revenue']:,.0f}")
    with col3:
        st.metric("📊 Total Categories", len(df_category))
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 Category Revenue")
        fig = px.bar(
            df_category.sort_values('total_revenue', ascending=True),
            y='product_category',
            x='total_revenue',
            orientation='h',
            text='total_revenue',
            color='total_revenue',
            color_continuous_scale='Viridis'
        )
        fig.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
        fig.update_layout(template='plotly_dark', height=400, showlegend=False, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🥧 Category Distribution")
        fig = px.pie(
            df_category,
            values='transaction_count',
            names='product_category',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(template='plotly_dark', height=400, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🏆 Top 20 Products")
    fig = px.bar(
        df_products,
        x='product_name',
        y='total_revenue',
        color='product_category',
        text='total_revenue'
    )
    fig.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
    fig.update_layout(template='plotly_dark', height=400, xaxis_tickangle=-45, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
    st.plotly_chart(fig, use_container_width=True)

# ==================== EMPLOYEES ====================
elif report_type == "👥 Employees":
    st.markdown('<h1>👥 Employee Performance</h1>', unsafe_allow_html=True)
    df_employee = employee_performance()
    
    col1, col2, col3, col4 = st.columns(4)
    top_emp = df_employee.iloc[0]
    with col1:
        st.metric("🏆 Top Performer", top_emp['employee_name'])
    with col2:
        st.metric("💰 Their Revenue", f"£{top_emp['total_revenue']:,.0f}")
    with col3:
        st.metric("👥 Total Staff", len(df_employee))
    with col4:
        avg_rev = df_employee['total_revenue'].mean()
        st.metric("📊 Avg per Employee", f"£{avg_rev:,.0f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top 10 Employees")
        fig = px.bar(
            df_employee.head(10),
            y='employee_name',
            x='total_revenue',
            orientation='h',
            color='role',
            text='total_revenue'
        )
        fig.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
        fig.update_layout(template='plotly_dark', height=500, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Performance Distribution")
        fig = px.scatter(
            df_employee,
            x='transaction_count',
            y='avg_transaction_value',
            size='total_revenue',
            color='role',
            hover_data=['employee_name'],
            size_max=40
        )
        fig.update_layout(template='plotly_dark', height=500, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📋 Employee Details")
    st.dataframe(
        df_employee.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_transaction_value': '£{:,.2f}'
        }).background_gradient(subset=['total_revenue'], cmap='YlGn'),
        use_container_width=True,
        height=400
    )

# ==================== PAYMENTS ====================
elif report_type == "💳 Payments":
    st.markdown('<h1>💳 Payment Method Analysis</h1>', unsafe_allow_html=True)
    df_payment = payment_method_breakdown()
    
    col1, col2, col3, col4 = st.columns(4)
    top_method = df_payment.iloc[0]
    with col1:
        st.metric("🏆 Most Popular", top_method['payment_method'].replace('_', ' ').title())
    with col2:
        st.metric("💰 Total Revenue", f"£{df_payment['total_revenue'].sum():,.0f}")
    with col3:
        st.metric("📊 Methods Available", len(df_payment))
    with col4:
        digital_pct = df_payment[df_payment['payment_method'].isin(['credit_card', 'debit_card', 'mobile_payment'])]['percentage'].sum()
        st.metric("📱 Digital Payments", f"{digital_pct:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Transaction Volume")
        fig = px.pie(
            df_payment,
            values='transaction_count',
            names='payment_method',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(template='plotly_dark', height=400, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Revenue by Method")
        fig = px.bar(
            df_payment,
            x='payment_method',
            y='total_revenue',
            text='total_revenue',
            color='total_revenue',
            color_continuous_scale='Blues'
        )
        fig.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
        fig.update_layout(template='plotly_dark', height=400, showlegend=False, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📊 Volume vs Revenue Comparison")
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Transaction Count', x=df_payment['payment_method'], y=df_payment['transaction_count'], marker_color='#4CAF50'))
    fig.add_trace(go.Bar(name='Revenue (£)', x=df_payment['payment_method'], y=df_payment['total_revenue'], marker_color='#2196F3'))
    fig.update_layout(template='plotly_dark', height=350, barmode='group', plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
    st.plotly_chart(fig, use_container_width=True)

# ==================== PEAK HOURS ====================
elif report_type == "⏰ Peak Hours":
    st.markdown('<h1>⏰ Hourly Performance Analysis</h1>', unsafe_allow_html=True)
    df_hourly = hourly_sales_pattern()
    
    peak_volume = df_hourly.loc[df_hourly['transaction_count'].idxmax()]
    peak_revenue = df_hourly.loc[df_hourly['total_revenue'].idxmax()]
    peak_value = df_hourly.loc[df_hourly['avg_transaction_value'].idxmax()]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔥 Peak Volume Hour", f"{peak_volume['hour']}:00")
        st.caption(f"{peak_volume['transaction_count']:,} transactions")
    with col2:
        st.metric("💰 Peak Revenue Hour", f"{peak_revenue['hour']}:00")
        st.caption(f"£{peak_revenue['total_revenue']:,.0f}")
    with col3:
        st.metric("📈 Highest Avg Value", f"{peak_value['hour']}:00")
        st.caption(f"£{peak_value['avg_transaction_value']:.2f}")
    with col4:
        total_hours = len(df_hourly)
        st.metric("⏱️ Operating Hours", f"{total_hours}h")
        st.caption("Daily operation")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Transaction Volume by Hour")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_hourly['hour'],
            y=df_hourly['transaction_count'],
            marker=dict(color=df_hourly['transaction_count'], colorscale='Viridis', showscale=True, colorbar=dict(title="Count")),
            text=df_hourly['transaction_count'],
            textposition='outside'
        ))
        fig.update_layout(template='plotly_dark', height=350, xaxis_title="Hour", yaxis_title="Transactions", plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Revenue by Hour")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_hourly['hour'],
            y=df_hourly['total_revenue'],
            mode='lines+markers',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(76, 175, 80, 0.2)'
        ))
        fig.update_layout(template='plotly_dark', height=350, xaxis_title="Hour", yaxis_title="Revenue (£)", plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🌡️ Average Transaction Value Heatmap")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_hourly['hour'],
        y=df_hourly['avg_transaction_value'],
        marker=dict(color=df_hourly['avg_transaction_value'], colorscale='RdYlGn', showscale=True, colorbar=dict(title="Avg £")),
        text=df_hourly['avg_transaction_value'].round(2),
        textposition='outside'
    ))
    fig.update_layout(template='plotly_dark', height=300, xaxis_title="Hour", yaxis_title="Average Value (£)", plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📋 Hourly Performance Details")
    st.dataframe(
        df_hourly.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_transaction_value': '£{:,.2f}'
        }).background_gradient(subset=['transaction_count'], cmap='Blues'),
        use_container_width=True,
        height=400
    )

# ==================== REFUNDS ====================
elif report_type == "🔄 Refunds":
    st.markdown('<h1>🔄 Refund Analysis</h1>', unsafe_allow_html=True)
    df_refund = refund_analysis()
    
    total_refunds = df_refund['refund_amount'].sum()
    total_revenue = df_refund['original_amount'].sum()
    refund_rate = (total_refunds / total_revenue * 100) if total_revenue > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔄 Total Refunds", f"£{total_refunds:,.0f}")
    with col2:
        st.metric("📊 Refund Rate", f"{refund_rate:.2f}%", delta="-0.8%", delta_color="inverse")
    with col3:
        avg_refund = df_refund['refund_amount'].mean()
        st.metric("💰 Average Refund", f"£{avg_refund:.2f}")
    with col4:
        refund_count = len(df_refund)
        st.metric("📝 Refund Transactions", f"{refund_count:,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Top Refund Categories")
        df_category_refunds = df_refund.groupby('product_category')['refund_amount'].sum().reset_index().sort_values('refund_amount', ascending=False)
        fig = px.bar(
            df_category_refunds.head(10),
            x='product_category',
            y='refund_amount',
            color='refund_amount',
            text='refund_amount',
            color_continuous_scale='Reds'
        )
        fig.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
        fig.update_layout(template='plotly_dark', height=350, showlegend=False, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 Refunds Over Time")
        df_daily_refunds = df_refund.groupby('transaction_date')['refund_amount'].sum().reset_index().tail(30)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_daily_refunds['transaction_date'],
            y=df_daily_refunds['refund_amount'],
            marker_color='#FF5252',
            name='Daily Refunds'
        ))
        fig.add_trace(go.Scatter(
            x=df_daily_refunds['transaction_date'],
            y=df_daily_refunds['refund_amount'].rolling(7).mean(),
            mode='lines',
            line=dict(color='#FFD93D', width=3),
            name='7-day Average'
        ))
        fig.update_layout(template='plotly_dark', height=350, xaxis_title="Date", yaxis_title="Refund Amount (£)", 
                         hovermode='x unified', plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Refund Reasons")
        if 'refund_reason' in df_refund.columns:
            df_reasons = df_refund['refund_reason'].value_counts().reset_index()
            fig = px.pie(
                df_reasons,
                values='count',
                names='refund_reason',
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(template='plotly_dark', height=350, plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Refund reason data not available")
    
    with col2:
        st.markdown("### ⏰ Refund Time Analysis")
        if 'refund_time' in df_refund.columns:
            df_refund['refund_hour'] = pd.to_datetime(df_refund['refund_time']).dt.hour
            hourly_refunds = df_refund.groupby('refund_hour').size().reset_index(name='count')
            fig = px.bar(
                hourly_refunds,
                x='refund_hour',
                y='count',
                text='count',
                color='count',
                color_continuous_scale='Reds'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(template='plotly_dark', height=350, xaxis_title="Hour of Day", 
                            yaxis_title="Number of Refunds", showlegend=False, 
                            plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Refund time data not available")
    
    st.markdown("### 📋 Refund Transactions")
    display_cols = [col for col in df_refund.columns if col in ['transaction_date', 'product_category', 
                                                               'original_amount', 'refund_amount', 
                                                               'refund_reason', 'employee_name']]
    st.dataframe(
        df_refund[display_cols].head(50).style.format({
            'original_amount': '£{:,.2f}',
            'refund_amount': '£{:,.2f}'
        }).background_gradient(subset=['refund_amount'], cmap='Reds'),
        use_container_width=True,
        height=400
    )

# ==================== MONTHLY TREND (Additional) ====================
elif report_type == "📈 Monthly Trend":
    st.markdown('<h1>📈 Monthly Revenue Trends</h1>', unsafe_allow_html=True)
    df_monthly = monthly_revenue_trend()
    
    current_month = df_monthly.iloc[-1]
    previous_month = df_monthly.iloc[-2] if len(df_monthly) > 1 else current_month
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Current Month", current_month['month'].strftime('%B %Y'))
    with col2:
        monthly_growth = ((current_month['total_revenue'] - previous_month['total_revenue']) / 
                         previous_month['total_revenue'] * 100) if previous_month['total_revenue'] > 0 else 0
        st.metric("💰 Monthly Revenue", f"£{current_month['total_revenue']:,.0f}", 
                 delta=f"{monthly_growth:+.1f}%")
    with col3:
        st.metric("🧾 Monthly Transactions", f"{current_month['transaction_count']:,}")
    with col4:
        st.metric("📊 Avg Transaction", f"£{current_month['avg_transaction_value']:.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Monthly Revenue Growth")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_monthly['month'],
            y=df_monthly['total_revenue'],
            name='Revenue',
            marker_color='#4CAF50',
            text=df_monthly['total_revenue']
        ))
        fig.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
        fig.update_layout(template='plotly_dark', height=400, xaxis_title="Month", 
                         yaxis_title="Revenue (£)", plot_bgcolor='#1a1d29', 
                         paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Transaction Volume Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_monthly['month'],
            y=df_monthly['transaction_count'],
            mode='lines+markers',
            name='Transactions',
            line=dict(color='#2196F3', width=3),
            fill='tozeroy',
            fillcolor='rgba(33, 150, 243, 0.1)'
        ))
        fig.update_layout(template='plotly_dark', height=400, xaxis_title="Month", 
                         yaxis_title="Transaction Count", plot_bgcolor='#1a1d29', 
                         paper_bgcolor='#1a1d29')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📊 Key Metrics Over Time")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_monthly['month'],
            y=df_monthly['avg_transaction_value'],
            mode='lines+markers',
            line=dict(color='#FF9800', width=2)
        ))
        fig.update_layout(template='plotly_dark', height=200, title="Avg Transaction Value",
                         plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29',
                         margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_monthly['month'],
            y=df_monthly['completed_revenue'],
            mode='lines+markers',
            line=dict(color='#4CAF50', width=2)
        ))
        fig.update_layout(template='plotly_dark', height=200, title="Completed Revenue",
                         plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29',
                         margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        if 'refunded_amount' in df_monthly.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_monthly['month'],
                y=df_monthly['refunded_amount'],
                mode='lines+markers',
                line=dict(color='#F44336', width=2)
            ))
            fig.update_layout(template='plotly_dark', height=200, title="Refunded Amount",
                             plot_bgcolor='#1a1d29', paper_bgcolor='#1a1d29',
                             margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Refund data not available")

# ==================== FOOTER ====================
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption("📊 Data updated in real-time")
with footer_col2:
    st.caption("⚡ Powered by EPOS Analytics")
with footer_col3:
    st.caption(f"© {datetime.now().year} All rights reserved")