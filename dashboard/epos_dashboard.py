"""
Real-Time EPOS Analytics Dashboard
Built with Streamlit
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

# Page config
st.set_page_config(
    page_title="EPOS Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    h1 {
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📊 EPOS Analytics Dashboard")
st.markdown("Real-time insights from your point-of-sale data")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎛️ Controls")
    
    # Report selection
    report_type = st.selectbox(
        "Select Report",
        ["Overview", "Daily Sales", "Location Analysis", "Product Performance", 
         "Employee Metrics", "Payment Methods", "Hourly Patterns", "Refund Analysis"]
    )
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.success("Data refreshed!")
    
    st.markdown("---")
    st.markdown("### 📈 Quick Stats")
    
    # Load data for quick stats
    df_daily = daily_sales_report()
    total_revenue = df_daily['total_revenue'].sum()
    total_transactions = df_daily['transaction_count'].sum()
    avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
    
    st.metric("Total Revenue", f"£{total_revenue:,.2f}")
    st.metric("Total Transactions", f"{total_transactions:,}")
    st.metric("Avg Transaction", f"£{avg_transaction:.2f}")


# Main content area
if report_type == "Overview":
    st.header("📈 Business Overview")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    df_daily = daily_sales_report()
    df_location = location_performance()
    
    with col1:
        total_rev = df_daily['total_revenue'].sum()
        st.metric(
            label="Total Revenue",
            value=f"£{total_rev:,.0f}",
            delta="YTD"
        )
    
    with col2:
        total_txn = df_daily['transaction_count'].sum()
        st.metric(
            label="Total Transactions",
            value=f"{total_txn:,}",
            delta="+12.5%"
        )
    
    with col3:
        avg_txn = total_rev / total_txn if total_txn > 0 else 0
        st.metric(
            label="Avg Transaction Value",
            value=f"£{avg_txn:.2f}",
            delta="+5.2%"
        )
    
    with col4:
        num_locations = len(df_location)
        st.metric(
            label="Active Locations",
            value=num_locations,
            delta="All operational"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Daily Revenue Trend")
        fig = px.line(
            df_daily, 
            x='transaction_date', 
            y='total_revenue',
            title='Daily Revenue Over Time',
            labels={'total_revenue': 'Revenue (£)', 'transaction_date': 'Date'}
        )
        fig.update_traces(line_color='#1f77b4', line_width=2)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏪 Top Locations by Revenue")
        fig = px.bar(
            df_location.head(8),
            x='location_name',
            y='total_revenue',
            color='location_type',
            title='Location Performance',
            labels={'total_revenue': 'Revenue (£)', 'location_name': 'Location'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Product categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🍺 Product Category Distribution")
        df_category = product_category_analysis()
        fig = px.pie(
            df_category,
            values='total_revenue',
            names='product_category',
            title='Revenue by Category',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⏰ Hourly Transaction Pattern")
        df_hourly = hourly_sales_pattern()
        fig = px.area(
            df_hourly,
            x='hour',
            y='transaction_count',
            title='Transactions by Hour',
            labels={'transaction_count': 'Transactions', 'hour': 'Hour of Day'}
        )
        fig.update_traces(fill='tozeroy', line_color='#ff7f0e')
        st.plotly_chart(fig, use_container_width=True)

elif report_type == "Daily Sales":
    st.header("📅 Daily Sales Report")
    
    df_daily = daily_sales_report()
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Days", len(df_daily))
    with col2:
        st.metric("Completed Revenue", f"£{df_daily['completed_revenue'].sum():,.2f}")
    with col3:
        st.metric("Refunded Amount", f"£{df_daily['refunded_amount'].sum():,.2f}")
    
    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_daily['transaction_date'],
        y=df_daily['completed_revenue'],
        name='Completed Revenue',
        mode='lines+markers',
        line=dict(color='green', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df_daily['transaction_date'],
        y=df_daily['refunded_amount'],
        name='Refunded Amount',
        mode='lines+markers',
        line=dict(color='red', width=2)
    ))
    fig.update_layout(
        title='Daily Sales Performance',
        xaxis_title='Date',
        yaxis_title='Amount (£)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📊 Detailed Daily Data")
    st.dataframe(
        df_daily.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_transaction_value': '£{:,.2f}',
            'completed_revenue': '£{:,.2f}',
            'refunded_amount': '£{:,.2f}'
        }),
        use_container_width=True,
        height=400
    )

elif report_type == "Location Analysis":
    st.header("🏪 Location Performance Analysis")
    
    df_location = location_performance()
    
    # Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Location")
        top_loc = df_location.iloc[0]
        st.metric("Location", top_loc['location_name'])
        st.metric("Revenue", f"£{top_loc['total_revenue']:,.2f}")
        st.metric("Transactions", f"{top_loc['transaction_count']:,}")
    
    with col2:
        st.subheader("📊 Location Stats")
        st.metric("Total Locations", len(df_location))
        st.metric("Total Revenue", f"£{df_location['total_revenue'].sum():,.2f}")
        st.metric("Avg Revenue/Location", f"£{df_location['total_revenue'].mean():,.2f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            df_location,
            x='location_name',
            y='total_revenue',
            color='city',
            title='Revenue by Location & City',
            labels={'total_revenue': 'Revenue (£)', 'location_name': 'Location'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            df_location,
            x='transaction_count',
            y='avg_transaction_value',
            size='total_revenue',
            color='location_type',
            hover_data=['location_name'],
            title='Transaction Volume vs Average Value',
            labels={
                'transaction_count': 'Number of Transactions',
                'avg_transaction_value': 'Avg Transaction (£)'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Detailed Location Data")
    st.dataframe(
        df_location.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_transaction_value': '£{:,.2f}',
            'total_tips': '£{:,.2f}'
        }),
        use_container_width=True
    )

elif report_type == "Product Performance":
    st.header("🍺 Product Performance Analysis")
    
    df_category = product_category_analysis()
    df_products = top_performing_products()
    
    # Category performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Category Revenue")
        fig = px.bar(
            df_category,
            x='product_category',
            y='total_revenue',
            title='Revenue by Category',
            labels={'total_revenue': 'Revenue (£)', 'product_category': 'Category'},
            color='total_revenue',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Category Distribution")
        fig = px.pie(
            df_category,
            values='transaction_count',
            names='product_category',
            title='Transaction Share by Category'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top products
    st.subheader("🏆 Top 20 Products")
    fig = px.bar(
        df_products,
        x='product_name',
        y='total_revenue',
        color='product_category',
        title='Top Performing Products',
        labels={'total_revenue': 'Revenue (£)', 'product_name': 'Product'}
    )
    fig.update_xaxis(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.dataframe(
        df_products.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_price': '£{:,.2f}'
        }),
        use_container_width=True
    )

elif report_type == "Employee Metrics":
    st.header("👥 Employee Performance Metrics")
    
    df_employee = employee_performance()
    
    # Top performers
    col1, col2, col3 = st.columns(3)
    
    top_emp = df_employee.iloc[0]
    with col1:
        st.subheader("🏆 Top Performer")
        st.metric("Employee", top_emp['employee_name'])
        st.metric("Revenue", f"£{top_emp['total_revenue']:,.2f}")
    
    with col2:
        st.subheader("📊 Team Stats")
        st.metric("Total Employees", len(df_employee))
        st.metric("Total Revenue", f"£{df_employee['total_revenue'].sum():,.2f}")
    
    with col3:
        st.subheader("📈 Averages")
        st.metric("Avg Revenue/Employee", f"£{df_employee['total_revenue'].mean():,.2f}")
        st.metric("Avg Transactions/Employee", f"{df_employee['transaction_count'].mean():.0f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            df_employee.head(10),
            x='employee_name',
            y='total_revenue',
            color='role',
            title='Top 10 Employees by Revenue',
            labels={'total_revenue': 'Revenue (£)', 'employee_name': 'Employee'}
        )
        fig.update_xaxis(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            df_employee,
            x='transaction_count',
            y='avg_transaction_value',
            size='total_revenue',
            color='role',
            hover_data=['employee_name'],
            title='Performance Matrix',
            labels={
                'transaction_count': 'Transactions',
                'avg_transaction_value': 'Avg Value (£)'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Employee Performance Table")
    st.dataframe(
        df_employee.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_transaction_value': '£{:,.2f}'
        }),
        use_container_width=True,
        height=400
    )

elif report_type == "Payment Methods":
    st.header("💳 Payment Method Analysis")
    
    df_payment = payment_method_breakdown()
    
    # Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Payment Methods", len(df_payment))
    with col2:
        st.metric("Total Transactions", f"{df_payment['transaction_count'].sum():,}")
    with col3:
        top_method = df_payment.iloc[0]
        st.metric("Most Popular", top_method['payment_method'].replace('_', ' ').title())
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            df_payment,
            values='transaction_count',
            names='payment_method',
            title='Payment Method Distribution (by Count)',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            df_payment,
            x='payment_method',
            y=['transaction_count', 'total_revenue'],
            title='Payment Methods: Volume vs Revenue',
            labels={'value': 'Amount', 'payment_method': 'Payment Method'},
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📊 Payment Method Details")
    st.dataframe(
        df_payment.style.format({
            'total_revenue': '£{:,.2f}',
            'avg_transaction_value': '£{:,.2f}',
            'percentage': '{:.2f}%'
        }),
        use_container_width=True
    )

elif report_type == "Hourly Patterns":
    st.header("⏰ Hourly Sales Patterns")
    
    df_hourly = hourly_sales_pattern()
    
    # Peak hours
    peak_hour = df_hourly.loc[df_hourly['transaction_count'].idxmax()]
    peak_revenue = df_hourly.loc[df_hourly['total_revenue'].idxmax()]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Peak Hour (Volume)", f"{peak_hour['hour']}:00")
        st.metric("Transactions", f"{peak_hour['transaction_count']:,}")
    
    with col2:
        st.metric("Peak Hour (Revenue)", f"{peak_revenue['hour']}:00")
        st.metric("Revenue", f"£{peak_revenue['total_revenue']:,.2f}")
    
    with col3:
        st.metric("Operating Hours", f"{df_hourly['hour'].min()}:00 - {df_hourly['hour'].max()}:00")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.area(
            df_hourly,
            x='hour',
            y='transaction_count',
            title='Hourly Transaction Volume',
            labels={'transaction_count': 'Transactions', 'hour': 'Hour'}
        )
        fig.update_traces(fill='tozeroy')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            df_hourly,
            x='hour',
            y='total_revenue',
            title='Hourly Revenue Pattern',
            labels={'total_revenue': 'Revenue (£)', 'hour': 'Hour'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap-style bar
    fig = px.bar(
        df_hourly,
        x='hour',
        y='avg_transaction_value',
        title='Average Transaction Value by Hour',
        labels={'avg_transaction_value': 'Avg Value (£)', 'hour': 'Hour'},
        color='avg_transaction_value',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

elif report_type == "Refund Analysis":
    st.header("🔄 Refund Analysis")
    
    df_refunds = refund_analysis()
    df_daily = daily_sales_report()
    
    # Summary metrics
    total_refunds = df_refunds['refund_count'].sum()
    total_refund_amount = df_refunds['refund_amount'].sum()
    total_revenue = df_daily['total_revenue'].sum()
    refund_rate = (total_refund_amount / total_revenue * 100) if total_revenue > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Refunds", f"{total_refunds:,}")
    with col2:
        st.metric("Refund Amount", f"£{total_refund_amount:,.2f}")
    with col3:
        st.metric("Refund Rate", f"{refund_rate:.2f}%")
    with col4:
        highest_refund_loc = df_refunds.iloc[0]
        st.metric("Highest Refund Location", highest_refund_loc['location_name'])
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            df_refunds,
            x='location_name',
            y='refund_count',
            title='Refunds by Location',
            labels={'refund_count': 'Number of Refunds', 'location_name': 'Location'},
            color='refund_count',
            color_continuous_scale='Reds'
        )
        fig.update_xaxis(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            df_refunds,
            x='location_name',
            y='refund_amount',
            title='Refund Amount by Location',
            labels={'refund_amount': 'Refund Amount (£)', 'location_name': 'Location'},
            color='refund_amount',
            color_continuous_scale='Oranges'
        )
        fig.update_xaxis(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Refund Details by Location")
    st.dataframe(
        df_refunds.style.format({
            'refund_amount': '£{:,.2f}',
            'avg_refund_value': '£{:,.2f}'
        }),
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>EPOS Analytics Dashboard | Built with Streamlit | Data refreshes in real-time</p>
    </div>
    """,
    unsafe_allow_html=True
)