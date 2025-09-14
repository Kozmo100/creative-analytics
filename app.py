import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="Creative Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("🎬 Creative Performance Analytics")
st.markdown("### Transform your video ad data into actionable insights")

# Initialize session state for sample data
if 'use_sample' not in st.session_state:
    st.session_state.use_sample = False
if 'sample_df' not in st.session_state:
    st.session_state.sample_df = None

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Upload Your Data")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your Facebook, Google, or TikTok Ads export"
    )
    
    # Sample data button in sidebar
    if st.button("📊 Or Use Sample Data", type="secondary"):
        st.session_state.use_sample = True
        # Create sample data
        sample_data = {
            'Ad name': ['Creative A', 'Creative B', 'Creative C', 'Creative D', 'Creative E'],
            'Impressions': [10000, 15000, 8000, 12000, 20000],
            'Three-second video views': [500, 900, 200, 800, 1500],
            'ThruPlay Actions': [150, 400, 50, 350, 800],
            'Link Clicks': [100, 200, 30, 150, 400],
            'Cost (EUR)': [50, 75, 40, 60, 100],
            'ROAS': [2.5, 3.2, 1.1, 2.8, 4.5]
        }
        st.session_state.sample_df = pd.DataFrame(sample_data)
    
    # Clear data button
    if st.session_state.use_sample or uploaded_file:
        if st.button("🔄 Clear Data"):
            st.session_state.use_sample = False
            st.session_state.sample_df = None
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 How to use:")
    st.markdown("""
    1. Upload your CSV file OR
    2. Click 'Use Sample Data' to try the app
    3. View instant insights
    4. Download the report
    """)

# Determine which data to use
df = None
data_source = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    data_source = "uploaded"
elif st.session_state.use_sample and st.session_state.sample_df is not None:
    df = st.session_state.sample_df.copy()
    data_source = "sample"

# Main content
if df is not None:
    # Show success message
    if data_source == "uploaded":
        st.success(f"✅ Successfully loaded {len(df)} creatives from your file!")
    else:
        st.info(f"📊 Using sample data with {len(df)} creatives for demonstration")
    
    # Calculate metrics (with error handling)
    try:
        # Clean column names (remove spaces)
        df.columns = df.columns.str.strip()
        
        # Calculate Hook Rate
        if 'Three-second video views' in df.columns and 'Impressions' in df.columns:
            df['Hook Rate (%)'] = (df['Three-second video views'] / df['Impressions'] * 100).round(2)
        
        # Calculate Hold Rate  
        if 'ThruPlay Actions' in df.columns and 'Three-second video views' in df.columns:
            # Avoid division by zero
            df['Hold Rate (%)'] = df.apply(
                lambda row: round((row['ThruPlay Actions'] / row['Three-second video views'] * 100), 2) 
                if row['Three-second video views'] > 0 else 0, 
                axis=1
            )
        
        # Calculate Convert Score
        if 'Link Clicks' in df.columns and 'Impressions' in df.columns:
            df['Convert Score (%)'] = (df['Link Clicks'] / df['Impressions'] * 100).round(2)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Performance Table", "🎯 Insights", "📥 Export"])
        
        with tab1:
            st.markdown("### Key Metrics")
            
            # Create metrics cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_hook = df['Hook Rate (%)'].mean() if 'Hook Rate (%)' in df.columns else 0
                st.metric(
                    "Avg Hook Rate", 
                    f"{avg_hook:.1f}%",
                    help="Average first 3-second view rate"
                )
            
            with col2:
                avg_hold = df['Hold Rate (%)'].mean() if 'Hold Rate (%)' in df.columns else 0
                st.metric(
                    "Avg Hold Rate", 
                    f"{avg_hold:.1f}%",
                    help="Average completion rate after hook"
                )
            
            with col3:
                avg_convert = df['Convert Score (%)'].mean() if 'Convert Score (%)' in df.columns else 0
                st.metric(
                    "Avg Convert Score", 
                    f"{avg_convert:.1f}%",
                    help="Average click-through rate"
                )
            
            with col4:
                avg_roas = df['ROAS'].mean() if 'ROAS' in df.columns else 0
                st.metric(
                    "Avg ROAS", 
                    f"{avg_roas:.2f}x",
                    help="Average Return on Ad Spend"
                )
            
            # Performance Overview
            st.markdown("### Performance by Creative")
            
            if 'Hook Rate (%)' in df.columns:
                # Sort by Hook Rate for better visualization
                df_sorted = df.sort_values('Hook Rate (%)', ascending=True)
                
                # Create two columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Hook Rate by Creative")
                    # Create a color-coded bar chart
                    chart_data = df_sorted[['Ad name', 'Hook Rate (%)']].set_index('Ad name')
                    st.bar_chart(chart_data, height=400)
                
                with col2:
                    if 'Hold Rate (%)' in df.columns:
                        st.markdown("#### Hold Rate by Creative")
                        df_sorted = df.sort_values('Hold Rate (%)', ascending=True)
                        chart_data = df_sorted[['Ad name', 'Hold Rate (%)']].set_index('Ad name')
                        st.bar_chart(chart_data, height=400)
            
            # Additional metrics if ROAS exists
            if 'ROAS' in df.columns:
                st.markdown("### ROAS Performance")
                chart_data = df.sort_values('ROAS', ascending=True)[['Ad name', 'ROAS']].set_index('Ad name')
                st.bar_chart(chart_data, height=300)
        
        with tab2:
            st.markdown("### 🎬 Creative Performance Details")
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'Hook Rate (%)' in df.columns:
                    min_hook = st.slider("Min Hook Rate (%)", 0.0, float(df['Hook Rate (%)'].max()), 0.0)
                    df_filtered = df[df['Hook Rate (%)'] >= min_hook]
                else:
                    df_filtered = df
            
            with col2:
                if 'ROAS' in df.columns:
                    min_roas = st.slider("Min ROAS", 0.0, float(df['ROAS'].max()), 0.0)
                    df_filtered = df_filtered[df_filtered['ROAS'] >= min_roas]
            
            with col3:
                st.metric("Filtered Creatives", len(df_filtered))
            
            # Show the data table with color coding
            st.markdown("#### Performance Table")
            
            # Define which columns to display
            display_cols = ['Ad name', 'Hook Rate (%)', 'Hold Rate (%)', 
                           'Convert Score (%)', 'ROAS', 'Cost (EUR)']
            display_cols = [col for col in display_cols if col in df_filtered.columns]
            
            # Display the dataframe with formatting
            st.dataframe(
                df_filtered[display_cols].style.background_gradient(
                    subset=['Hook Rate (%)', 'Hold Rate (%)', 'ROAS'],
                    cmap='RdYlGn'
                ) if 'Hook Rate (%)' in display_cols else df_filtered[display_cols],
                use_container_width=True,
                hide_index=True,
                height=400
            )
        
        with tab3:
            st.markdown("### 💡 Key Insights & Recommendations")
            
            # Performance Summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top Performers")
                if 'Hook Rate (%)' in df.columns and len(df) > 0:
                    best_hook = df.nlargest(1, 'Hook Rate (%)')
                    st.success(f"**Best Hook Rate:** {best_hook['Ad name'].values[0]} ({best_hook['Hook Rate (%)'].values[0]}%)")
                
                if 'Hold Rate (%)' in df.columns and len(df) > 0:
                    best_hold = df.nlargest(1, 'Hold Rate (%)')
                    st.success(f"**Best Hold Rate:** {best_hold['Ad name'].values[0]} ({best_hold['Hold Rate (%)'].values[0]}%)")
                
                if 'ROAS' in df.columns and len(df) > 0:
                    best_roas = df.nlargest(1, 'ROAS')
                    st.success(f"**Best ROAS:** {best_roas['Ad name'].values[0]} ({best_roas['ROAS'].values[0]}x)")
            
            with col2:
                st.markdown("#### ⚠️ Need Attention")
                if 'Hook Rate (%)' in df.columns and len(df) > 0:
                    worst_hook = df.nsmallest(1, 'Hook Rate (%)')
                    st.warning(f"**Lowest Hook Rate:** {worst_hook['Ad name'].values[0]} ({worst_hook['Hook Rate (%)'].values[0]}%)")
                
                if 'Hold Rate (%)' in df.columns and len(df) > 0:
                    worst_hold = df.nsmallest(1, 'Hold Rate (%)')
                    st.warning(f"**Lowest Hold Rate:** {worst_hold['Ad name'].values[0]} ({worst_hold['Hold Rate (%)'].values[0]}%)")
                
                if 'ROAS' in df.columns and len(df) > 0:
                    worst_roas = df.nsmallest(1, 'ROAS')
                    st.warning(f"**Lowest ROAS:** {worst_roas['Ad name'].values[0]} ({worst_roas['ROAS'].values[0]}x)")
            
            # Actionable Recommendations
            st.markdown("#### 📝 Actionable Recommendations")
            
            recommendations = []
            
            if 'Hook Rate (%)' in df.columns:
                low_hook = df[df['Hook Rate (%)'] < 3]
                if len(low_hook) > 0:
                    recommendations.append(f"🎬 **{len(low_hook)} creatives** have Hook Rate below 3%. Test new opening 3 seconds for these ads.")
                
                high_hook = df[df['Hook Rate (%)'] > 7]
                if len(high_hook) > 0:
                    recommendations.append(f"✨ **{len(high_hook)} creatives** have exceptional Hook Rates (>7%). Use these openings as templates.")
            
            if 'Hold Rate (%)' in df.columns:
                low_hold = df[df['Hold Rate (%)'] < 15]
                if len(low_hold) > 0:
                    recommendations.append(f"📉 **{len(low_hold)} creatives** have Hold Rate below 15%. Review middle content for engagement issues.")
                
                high_hold = df[df['Hold Rate (%)'] > 30]
                if len(high_hold) > 0:
                    recommendations.append(f"🎯 **{len(high_hold)} creatives** have excellent Hold Rates (>30%). Analyze for best practices.")
            
            if 'ROAS' in df.columns:
                profitable = df[df['ROAS'] > 2]
                if len(profitable) > 0:
                    recommendations.append(f"💰 **{len(profitable)} creatives** are highly profitable (ROAS > 2x). Increase budget allocation.")
                
                unprofitable = df[df['ROAS'] < 1]
                if len(unprofitable) > 0:
                    recommendations.append(f"⚠️ **{len(unprofitable)} creatives** are unprofitable (ROAS < 1x). Consider pausing or reworking.")
            
            for rec in recommendations:
                st.info(rec)
        
        with tab4:
            st.markdown("### 📥 Export Your Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Download Enhanced CSV")
                st.markdown("Includes all calculated metrics")
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"creative_analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                st.markdown("#### Copy Summary Report")
                
                summary = f"""
CREATIVE PERFORMANCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

OVERVIEW:
- Total Creatives: {len(df)}
- Avg Hook Rate: {df['Hook Rate (%)'].mean():.1f}%
- Avg Hold Rate: {df['Hold Rate (%)'].mean() if 'Hold Rate (%)' in df.columns else 0:.1f}%
- Avg ROAS: {df['ROAS'].mean() if 'ROAS' in df.columns else 0:.2f}x

TOP PERFORMERS:
{df.nlargest(3, 'Hook Rate (%)')[['Ad name', 'Hook Rate (%)']].to_string() if 'Hook Rate (%)' in df.columns else 'N/A'}

NEEDS IMPROVEMENT:
{df.nsmallest(3, 'Hook Rate (%)')[['Ad name', 'Hook Rate (%)']].to_string() if 'Hook Rate (%)' in df.columns else 'N/A'}
                """
                
                st.text_area("Summary Report", summary, height=300)
    
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.info("Showing raw data - please check column names match requirements")
        st.dataframe(df.head())

else:
    # Welcome screen when no data is loaded
    st.markdown("""
    ### 👋 Welcome to Creative Analytics Dashboard!
    
    This tool helps you understand your video ad performance without needing technical expertise.
    
    #### What you'll get:
    - **Hook Rate**: How well your video captures attention (first 3 seconds)
    - **Hold Rate**: How well you maintain viewer engagement  
    - **Convert Score**: How effective your CTA is
    - **Visual insights**: Charts and recommendations
    
    #### To get started:
    1. **Upload your CSV** file in the sidebar, OR
    2. **Click "Or Use Sample Data"** in the sidebar to try the app
    
    #### Required CSV columns:
    - `Ad name` - Name of your creative
    - `Impressions` - Total views
    - `Three-second video views` - 3-second video views
    - `ThruPlay Actions` - Complete views
    - `Link Clicks` - Number of clicks
    - `Cost (EUR)` - Ad spend
    - `ROAS` - Return on ad spend
    
    👈 **Check the sidebar to begin!**
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ for Creative Teams | Made with Streamlit")
