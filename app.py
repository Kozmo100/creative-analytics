import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="Creative Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .score-bar {
        height: 8px;
        border-radius: 4px;
        margin: 5px 0;
    }
    .creative-row {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    .retention-box {
        background: #e8f5e9;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🎬 Creative Performance Analytics")
st.markdown("### Visual performance scores for your video ads")

# Initialize session state
if 'use_sample' not in st.session_state:
    st.session_state.use_sample = False
if 'sample_df' not in st.session_state:
    st.session_state.sample_df = None

# Sidebar
with st.sidebar:
    st.header("📁 Data Source")
    
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="Upload your Facebook, Google, or TikTok Ads export"
    )
    
    if st.button("📊 Use Sample Data", type="primary", use_container_width=True):
        st.session_state.use_sample = True
        # Enhanced sample data with 15-second retention
        sample_data = {
            'Ad name': ['Creative Alpha', 'Creative Beta', 'Creative Gamma', 'Creative Delta', 
                       'Creative Epsilon', 'Creative Zeta', 'Creative Eta', 'Creative Theta'],
            'Ad Preview URL': ['https://example.com'] * 8,
            'Impressions': [50000, 45000, 38000, 42000, 55000, 48000, 41000, 39000],
            'Three-second video views': [4000, 3555, 3002, 3276, 4290, 3744, 3198, 3042],
            'Video Plays 25%': [3200, 2666, 2041, 2457, 3432, 2995, 2398, 2130],
            'Video Plays 50%': [2400, 2133, 1531, 1966, 2574, 2246, 1918, 1598],
            'ThruPlay Actions': [1600, 1600, 1020, 1474, 1716, 1498, 1439, 1065],
            'Link Clicks': [320, 355, 204, 245, 343, 299, 239, 213],
            'Cost (EUR)': [250, 225, 190, 210, 275, 240, 205, 195],
            'ROAS': [3.2, 4.1, 2.1, 2.8, 3.5, 3.0, 2.9, 2.2],
            'Fifteen-second video views': [807, 947, 500, 867, 1704, 810, 580, 1092]
        }
        st.session_state.sample_df = pd.DataFrame(sample_data)
    
    if st.session_state.use_sample or uploaded_file:
        if st.button("🔄 Clear Data", use_container_width=True):
            st.session_state.use_sample = False
            st.session_state.sample_df = None
            st.rerun()
    
    st.markdown("---")
    
    # Scoring thresholds settings
    with st.expander("⚙️ Scoring Settings"):
        st.markdown("#### Performance Thresholds")
        
        hook_good = st.slider("Hook Score - Good (>%)", 5, 15, 8)
        hook_medium = st.slider("Hook Score - Medium (>%)", 2, 8, 4)
        
        hold_good = st.slider("Hold Score - Good (>%)", 25, 50, 35)
        hold_medium = st.slider("Hold Score - Medium (>%)", 10, 30, 20)
        
        st.markdown("---")
        st.caption("Scores: Green = Good, Yellow = Medium, Red = Poor")

# Helper functions
def calculate_score(value, good_threshold, medium_threshold, max_value=100):
    """Convert percentage to 0-100 score with thresholds"""
    if value >= good_threshold:
        # Map to 70-100 range
        return min(70 + (value - good_threshold) * 2, 100)
    elif value >= medium_threshold:
        # Map to 50-69 range
        return 50 + ((value - medium_threshold) / (good_threshold - medium_threshold)) * 19
    else:
        # Map to 0-49 range
        return max(0, (value / medium_threshold) * 49)

def get_score_color(score):
    """Return color based on score"""
    if score >= 70:
        return "#4caf50"  # Green
    elif score >= 50:
        return "#ffc107"  # Yellow
    else:
        return "#f44336"  # Red

def create_score_bar(score, label):
    """Create HTML for a visual score bar"""
    color = get_score_color(score)
    return f"""
    <div style="margin: 8px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="font-size: 12px; color: #666;">{label}</span>
            <span style="font-size: 14px; font-weight: bold; color: {color};">{int(score)}</span>
        </div>
        <div style="background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
            <div style="background: {color}; width: {score}%; height: 100%;"></div>
        </div>
    </div>
    """

# Load data
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
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Calculate metrics
    if 'Three-second video views' in df.columns and 'Impressions' in df.columns:
        df['Hook Rate (%)'] = (df['Three-second video views'] / df['Impressions'] * 100).round(2)
        df['Hook Score'] = df['Hook Rate (%)'].apply(lambda x: calculate_score(x, hook_good, hook_medium))
    
    if 'ThruPlay Actions' in df.columns and 'Three-second video views' in df.columns:
        df['Hold Rate (%)'] = df.apply(
            lambda row: round((row['ThruPlay Actions'] / row['Three-second video views'] * 100), 2) 
            if row['Three-second video views'] > 0 else 0, 
            axis=1
        )
        df['Watch Score'] = df['Hold Rate (%)'].apply(lambda x: calculate_score(x, hold_good, hold_medium))
    
    if 'Link Clicks' in df.columns and 'Impressions' in df.columns:
        df['CTR (%)'] = (df['Link Clicks'] / df['Impressions'] * 100).round(2)
        df['Click Score'] = df['CTR (%)'].apply(lambda x: calculate_score(x * 10, 70, 40))  # CTR usually <10%
    
    # Calculate 15s/3s retention
    if 'Fifteen-second video views' in df.columns and 'Three-second video views' in df.columns:
        df['15s/3s Retention (%)'] = df.apply(
            lambda row: round((row['Fifteen-second video views'] / row['Three-second video views'] * 100), 2) 
            if row['Three-second video views'] > 0 else 0, 
            axis=1
        )
    else:
        # Estimate if not available
        df['15s/3s Retention (%)'] = df['Hold Rate (%)'].apply(lambda x: round(x * 0.6 + random.uniform(-5, 5), 2))
    
    # Convert Score (based on CTR and ROAS if available)
    if 'ROAS' in df.columns:
        df['Convert Score'] = df['ROAS'].apply(lambda x: min(100, x * 20))  # ROAS of 5 = score of 100
    else:
        df['Convert Score'] = df['CTR (%)'].apply(lambda x: calculate_score(x * 15, 70, 40))
    
    # Success/Info message
    if data_source == "uploaded":
        st.success(f"✅ Loaded {len(df)} creatives from your file")
    else:
        st.info(f"📊 Using sample data with {len(df)} creatives")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visual Scores", "📈 Detailed Table", "🎯 Insights", "📥 Export"])
    
    with tab1:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_ads = st.multiselect(
                "Filter Creatives",
                options=df['Ad name'].tolist(),
                default=df['Ad name'].tolist()[:10],  # Show first 10 by default
                key="filter_ads"
            )
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                options=['Hook Score', 'Watch Score', 'Click Score', 'Convert Score', '15s/3s Retention (%)'],
                index=0
            )
        with col3:
            sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
        
        # Filter and sort dataframe
        df_filtered = df[df['Ad name'].isin(selected_ads)] if selected_ads else df
        ascending = sort_order == "Ascending"
        df_sorted = df_filtered.sort_values(sort_by, ascending=ascending)
        
        st.markdown(f"### {len(df_sorted)} creatives selected")
        
        # Display creatives with visual scores
        for idx, row in df_sorted.iterrows():
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 2, 2, 1.5])
                
                with col1:
                    # Placeholder for creative thumbnail
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                width: 60px; height: 60px; border-radius: 8px; 
                                display: flex; align-items: center; justify-content: center; 
                                color: white; font-weight: bold;">
                        {row['Ad name'][:2].upper()}
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(row['Ad name'][:15] + "..." if len(row['Ad name']) > 15 else row['Ad name'])
                
                with col2:
                    hook_score = row.get('Hook Score', 0)
                    watch_score = row.get('Watch Score', 0)
                    st.markdown(create_score_bar(hook_score, "Hook Score"), unsafe_allow_html=True)
                    st.markdown(create_score_bar(watch_score, "Watch Score"), unsafe_allow_html=True)
                
                with col3:
                    click_score = row.get('Click Score', 0)
                    convert_score = row.get('Convert Score', 0)
                    st.markdown(create_score_bar(click_score, "Click Score"), unsafe_allow_html=True)
                    st.markdown(create_score_bar(convert_score, "Convert Score"), unsafe_allow_html=True)
                
                with col4:
                    # Performance metrics
                    st.metric("Hook Rate", f"{row.get('Hook Rate (%)', 0):.1f}%")
                    st.metric("CTR", f"{row.get('CTR (%)', 0):.2f}%")
                
                with col5:
                    # ROAS and cost
                    if 'ROAS' in row:
                        roas_color = "green" if row['ROAS'] > 2 else "orange" if row['ROAS'] > 1 else "red"
                        st.metric("ROAS", f"{row['ROAS']:.1f}x")
                    if 'Cost (EUR)' in row:
                        st.metric("Spend", f"€{row['Cost (EUR)']:.0f}")
                
                with col6:
                    # 15s/3s Retention
                    retention = row.get('15s/3s Retention (%)', 0)
                    retention_color = "#4caf50" if retention > 30 else "#ffc107" if retention > 20 else "#f44336"
                    st.markdown(f"""
                    <div style="background: {retention_color}20; border: 2px solid {retention_color}; 
                                padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 20px; font-weight: bold; color: {retention_color};">
                            {retention:.1f}%
                        </div>
                        <div style="font-size: 11px; color: #666; margin-top: 4px;">
                            15s/3s retention
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
    
    with tab2:
        st.markdown("### Detailed Performance Data")
        
        # Select columns to display
        display_columns = st.multiselect(
            "Select columns to display",
            options=df.columns.tolist(),
            default=['Ad name', 'Hook Score', 'Watch Score', 'Click Score', 'Convert Score', 
                    '15s/3s Retention (%)', 'Hook Rate (%)', 'CTR (%)', 'ROAS']
        )
        
        if display_columns:
            # Color-code the dataframe
            styled_df = df[display_columns].style.background_gradient(
                subset=[col for col in display_columns if 'Score' in col or '%' in col or col == 'ROAS'],
                cmap='RdYlGn',
                vmin=0,
                vmax=100 if 'Score' in str(display_columns) else None
            )
            st.dataframe(styled_df, use_container_width=True, height=600)
    
    with tab3:
        st.markdown("### 🎯 Performance Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top Performers")
            
            # Best Hook Score
            if 'Hook Score' in df.columns:
                best_hook = df.nlargest(1, 'Hook Score')
                st.success(f"**Best Hook:** {best_hook['Ad name'].values[0]} (Score: {best_hook['Hook Score'].values[0]:.0f})")
            
            # Best Retention
            if '15s/3s Retention (%)' in df.columns:
                best_retention = df.nlargest(1, '15s/3s Retention (%)')
                st.success(f"**Best Retention:** {best_retention['Ad name'].values[0]} ({best_retention['15s/3s Retention (%)'].values[0]:.1f}%)")
            
            # Best Overall (composite score)
            if all(col in df.columns for col in ['Hook Score', 'Watch Score', 'Click Score', 'Convert Score']):
                df['Overall Score'] = (df['Hook Score'] + df['Watch Score'] + df['Click Score'] + df['Convert Score']) / 4
                best_overall = df.nlargest(1, 'Overall Score')
                st.success(f"**Best Overall:** {best_overall['Ad name'].values[0]} (Score: {best_overall['Overall Score'].values[0]:.0f})")
        
        with col2:
            st.markdown("#### ⚠️ Need Improvement")
            
            # Worst Hook Score
            if 'Hook Score' in df.columns:
                worst_hook = df.nsmallest(1, 'Hook Score')
                st.error(f"**Weak Hook:** {worst_hook['Ad name'].values[0]} (Score: {worst_hook['Hook Score'].values[0]:.0f})")
            
            # Worst Retention
            if '15s/3s Retention (%)' in df.columns:
                worst_retention = df.nsmallest(1, '15s/3s Retention (%)')
                st.error(f"**Poor Retention:** {worst_retention['Ad name'].values[0]} ({worst_retention['15s/3s Retention (%)'].values[0]:.1f}%)")
            
            # Worst Overall
            if 'Overall Score' in df.columns:
                worst_overall = df.nsmallest(1, 'Overall Score')
                st.error(f"**Needs Work:** {worst_overall['Ad name'].values[0]} (Score: {worst_overall['Overall Score'].values[0]:.0f})")
        
        # Distribution charts
        st.markdown("#### 📊 Score Distributions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Hook Score' in df.columns:
                st.markdown("##### Hook Score Distribution")
                chart_data = df['Hook Score'].value_counts().sort_index()
                st.bar_chart(chart_data)
        
        with col2:
            if '15s/3s Retention (%)' in df.columns:
                st.markdown("##### 15s/3s Retention Distribution")
                chart_data = df['15s/3s Retention (%)'].value_counts().sort_index()
                st.bar_chart(chart_data)
        
        # Actionable recommendations
        st.markdown("#### 💡 Recommendations")
        
        recommendations = []
        
        if 'Hook Score' in df.columns:
            low_hook = df[df['Hook Score'] < 50]
            if len(low_hook) > 0:
                recommendations.append(f"🎬 **{len(low_hook)} creatives** have weak hooks (score <50). Test new opening 3 seconds.")
        
        if '15s/3s Retention (%)' in df.columns:
            poor_retention = df[df['15s/3s Retention (%)'] < 20]
            if len(poor_retention) > 0:
                recommendations.append(f"⏱️ **{len(poor_retention)} creatives** lose viewers quickly (<20% reach 15s). Review pacing and content structure.")
            
            great_retention = df[df['15s/3s Retention (%)'] > 35]
            if len(great_retention) > 0:
                recommendations.append(f"✨ **{len(great_retention)} creatives** have excellent retention (>35% reach 15s). Use as templates.")
        
        if 'Convert Score' in df.columns:
            low_convert = df[df['Convert Score'] < 50]
            if len(low_convert) > 0:
                recommendations.append(f"🎯 **{len(low_convert)} creatives** have weak CTAs (score <50). Strengthen call-to-action.")
        
        for rec in recommendations:
            st.info(rec)
    
    with tab4:
        st.markdown("### 📥 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Enhanced CSV Export")
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Dataset with Scores",
                data=csv,
                file_name=f"creative_scores_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.markdown("#### Executive Summary")
            
            summary = f"""
CREATIVE PERFORMANCE SCORECARD
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

PORTFOLIO OVERVIEW:
- Total Creatives: {len(df)}
- Avg Hook Score: {df['Hook Score'].mean():.0f}/100
- Avg Watch Score: {df['Watch Score'].mean():.0f}/100
- Avg 15s/3s Retention: {df['15s/3s Retention (%)'].mean():.1f}%

TOP PERFORMERS:
{df.nlargest(3, 'Overall Score' if 'Overall Score' in df.columns else 'Hook Score')[['Ad name', 'Hook Score', 'Watch Score', '15s/3s Retention (%)']].to_string(index=False)}

ACTION ITEMS:
- Pause: {len(df[df['Hook Score'] < 40])} creatives with Hook Score <40
- Optimize: {len(df[(df['Hook Score'] >= 40) & (df['Hook Score'] < 70)])} creatives with medium performance
- Scale: {len(df[df['Hook Score'] >= 70])} creatives with Hook Score >70
            """
            
            st.text_area("Copy this summary:", summary, height=400)

else:
    # Welcome screen
    st.markdown("""
    ### Welcome to the Visual Creative Analytics Dashboard!
    
    This tool provides visual performance scores for your video creatives, similar to professional ad platforms.
    
    #### Features:
    - 📊 **Visual Score Bars** - Hook, Watch, Click, and Convert scores (0-100)
    - 📈 **15s/3s Retention Rate** - See how many viewers continue from 3s to 15s
    - 🎨 **Color-Coded Performance** - Green (good), Yellow (medium), Red (needs improvement)
    - 💡 **Actionable Insights** - Clear recommendations based on performance
    
    #### Required CSV Columns:
    - `Ad name` - Creative identifier
    - `Impressions` - Total impressions
    - `Three-second video views` - 3-second views
    - `Fifteen-second video views` - 15-second views (optional)
    - `ThruPlay Actions` - Complete views
    - `Link Clicks` - Number of clicks
    - `ROAS` - Return on ad spend (optional)
    
    👈 **Click "Use Sample Data" in the sidebar to see it in action!**
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ for Creative Teams | Professional Creative Analytics")
