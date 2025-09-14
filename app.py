import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Creative Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("🎬 Creative Performance Analytics")
st.markdown("### Transform your video ad data into actionable insights")

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Upload Your Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your Facebook, Google, or TikTok Ads export"
    )
    
    st.markdown("---")
    st.markdown("### 📖 How to use:")
    st.markdown("""
    1. Export your ad data from your platform
    2. Upload the CSV file
    3. View instant insights
    4. Download the report
    """)

# Main content
if uploaded_file is not None:
    # Read the CSV
    df = pd.read_csv(uploaded_file)
    
    # Show success message
    st.success(f"✅ Successfully loaded {len(df)} creatives!")
    
    # Calculate metrics (with error handling)
    try:
        # Clean column names (remove spaces, make lowercase)
        df.columns = df.columns.str.strip()
        
        # Calculate Hook Rate
        if 'Three-second video views' in df.columns and 'Impressions' in df.columns:
            df['Hook Rate (%)'] = (df['Three-second video views'] / df['Impressions'] * 100).round(2)
        
        # Calculate Hold Rate
        if 'ThruPlay Actions' in df.columns and 'Three-second video views' in df.columns:
            df['Hold Rate (%)'] = (df['ThruPlay Actions'] / df['Three-second video views'] * 100).round(2)
        
        # Calculate Convert Score
        if 'Link Clicks' in df.columns and 'Impressions' in df.columns:
            df['Convert Score (%)'] = (df['Link Clicks'] / df['Impressions'] * 100).round(2)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Performance Table", "🎯 Insights", "📥 Export"])
        
        with tab1:
            # Create metrics cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_hook = df['Hook Rate (%)'].mean() if 'Hook Rate (%)' in df.columns else 0
                st.metric("Avg Hook Rate", f"{avg_hook:.1f}%")
            
            with col2:
                avg_hold = df['Hold Rate (%)'].mean() if 'Hold Rate (%)' in df.columns else 0
                st.metric("Avg Hold Rate", f"{avg_hold:.1f}%")
            
            with col3:
                avg_convert = df['Convert Score (%)'].mean() if 'Convert Score (%)' in df.columns else 0
                st.metric("Avg Convert Score", f"{avg_convert:.1f}%")
            
            with col4:
                avg_roas = df['ROAS'].mean() if 'ROAS' in df.columns else 0
                st.metric("Avg ROAS", f"{avg_roas:.2f}x")
            
            # Create charts
            st.markdown("### 📊 Performance Distribution")
            
            if 'Hook Rate (%)' in df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_hook = px.histogram(df, x='Hook Rate (%)', 
                                           title="Hook Rate Distribution",
                                           color_discrete_sequence=['#1f77b4'])
                    st.plotly_chart(fig_hook, use_container_width=True)
                
                with col2:
                    if 'Hold Rate (%)' in df.columns:
                        fig_hold = px.histogram(df, x='Hold Rate (%)', 
                                               title="Hold Rate Distribution",
                                               color_discrete_sequence=['#ff7f0e'])
                        st.plotly_chart(fig_hold, use_container_width=True)
        
        with tab2:
            st.markdown("### 🎬 Creative Performance Details")
            
            # Add filters
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Hook Rate (%)' in df.columns:
                    min_hook = st.slider("Minimum Hook Rate (%)", 0.0, 100.0, 0.0)
                    df_filtered = df[df['Hook Rate (%)'] >= min_hook]
                else:
                    df_filtered = df
            
            # Show the data table
            display_cols = ['Ad name', 'Hook Rate (%)', 'Hold Rate (%)', 
                           'Convert Score (%)', 'ROAS', 'Cost (EUR)']
            display_cols = [col for col in display_cols if col in df_filtered.columns]
            
            st.dataframe(
                df_filtered[display_cols],
                use_container_width=True,
                hide_index=True
            )
        
        with tab3:
            st.markdown("### 💡 Key Insights")
            
            # Find best and worst performers
            if 'Hook Rate (%)' in df.columns:
                best_hook = df.nlargest(1, 'Hook Rate (%)')['Ad name'].values[0]
                worst_hook = df.nsmallest(1, 'Hook Rate (%)')['Ad name'].values[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"🏆 **Best Hook:** {best_hook}")
                with col2:
                    st.error(f"⚠️ **Needs Improvement:** {worst_hook}")
            
            # Insights based on data
            st.markdown("### 📝 Recommendations")
            
            if 'Hook Rate (%)' in df.columns:
                low_hook = df[df['Hook Rate (%)'] < 3]
                if len(low_hook) > 0:
                    st.warning(f"⚠️ {len(low_hook)} creatives have Hook Rate below 3% - consider testing new opening sequences")
            
            if 'Hold Rate (%)' in df.columns:
                high_hold = df[df['Hold Rate (%)'] > 30]
                if len(high_hold) > 0:
                    st.success(f"✅ {len(high_hold)} creatives have excellent Hold Rates (>30%) - analyze these for best practices")
        
        with tab4:
            st.markdown("### 📥 Download Processed Data")
            
            # Add download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Enhanced CSV",
                data=csv,
                file_name=f"creative_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.info("Please make sure your CSV has the correct column names")
        st.dataframe(df.head())

else:
    # Welcome screen when no file is uploaded
    st.markdown("""
    ### 👋 Welcome to Creative Analytics Dashboard!
    
    This tool helps you understand your video ad performance without needing technical expertise.
    
    #### What you'll get:
    - **Hook Rate**: How well your video captures attention (first 3 seconds)
    - **Hold Rate**: How well you maintain viewer engagement
    - **Convert Score**: How effective your CTA is
    - **Visual insights**: Charts and recommendations
    
    #### Required CSV columns:
    - `Ad name`
    - `Impressions`
    - `Three-second video views`
    - `ThruPlay Actions`
    - `Link Clicks`
    - `Cost (EUR)`
    - `ROAS`
    
    👈 **Upload your CSV file in the sidebar to get started!**
    """)
    
    # Sample data for testing
    if st.button("📊 Load Sample Data"):
        sample_data = {
            'Ad name': ['Creative A', 'Creative B', 'Creative C', 'Creative D', 'Creative E'],
            'Impressions': [10000, 15000, 8000, 12000, 20000],
            'Three-second video views': [500, 900, 200, 800, 1500],
            'ThruPlay Actions': [150, 400, 50, 350, 800],
            'Link Clicks': [100, 200, 30, 150, 400],
            'Cost (EUR)': [50, 75, 40, 60, 100],
            'ROAS': [2.5, 3.2, 1.1, 2.8, 4.5]
        }
        df = pd.DataFrame(sample_data)
        st.session_state['sample_loaded'] = True
        st.rerun()

# Footer
st.markdown("---")
st.markdown("Built with ❤️ for Creative Teams | [Report Issues](mailto:your-email@example.com)")
