import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Creative Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Motion-like styling
st.markdown("""
<style>
    /* Modern, clean design inspired by Motion */
    .main {
        background-color: #fafbfc;
    }
    
    .performance-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border: 1px solid #e1e4e8;
    }
    
    .metric-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
        margin-right: 8px;
    }
    
    .score-excellent {
        background: #e3fcef;
        color: #006644;
    }
    
    .score-good {
        background: #fffae6;
        color: #7a4100;
    }
    
    .score-poor {
        background: #ffebe9;
        color: #cf222e;
    }
    
    .retention-chart {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e1e4e8;
    }
    
    .insight-pill {
        background: #f6f8fa;
        border: 1px solid #d1d5da;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    
    .benchmark-indicator {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .above-benchmark {
        background: #e3fcef;
        color: #006644;
    }
    
    .below-benchmark {
        background: #ffebe9;
        color: #cf222e;
    }
    
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        font-weight: 600;
        color: #24292e;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: white;
        padding: 0 20px;
        border-radius: 12px 12px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 0;
        color: #586069;
        border-bottom: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #24292e;
        border-bottom: 2px solid #0969da;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'benchmarks' not in st.session_state:
    st.session_state.benchmarks = {
        'thumb_stop_rate': 25,  # Industry average
        'hook_rate': 8,
        'hold_rate': 35,
        'ctr': 1.5,
        'retention_15s': 25,
        'avg_watch_time': 12
    }

# Header
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("🎯 Creative Intelligence Platform")
    st.caption("Turn creative data into competitive advantage")
with col2:
    st.markdown("<div style='text-align: right; padding-top: 20px;'>", unsafe_allow_html=True)
    if st.button("📊 Industry Benchmarks", use_container_width=True):
        st.info("Comparing against industry averages")
    st.markdown("</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div style='text-align: right; padding-top: 20px;'>", unsafe_allow_html=True)
    if st.button("💡 Get Insights", type="primary", use_container_width=True):
        st.success("AI insights generated")
    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📁 Data Source")
    
    uploaded_file = st.file_uploader(
        "Upload your creative data",
        type=['csv'],
        help="Accepts exports from Meta, Google, TikTok"
    )
    
    if st.button("🎬 Load Demo Data", type="primary", use_container_width=True):
        # Create comprehensive demo data
        np.random.seed(42)
        demo_data = {
            'Creative Name': [f'Creative_{i+1}' for i in range(15)],
            'Platform': np.random.choice(['Facebook', 'TikTok', 'YouTube'], 15),
            'Campaign': np.random.choice(['Summer_Launch', 'Brand_Awareness', 'Performance_Q4'], 15),
            'Impressions': np.random.randint(10000, 100000, 15),
            'Three-second video views': np.random.randint(500, 8000, 15),
            'Video Plays 25%': np.random.randint(400, 6000, 15),
            'Video Plays 50%': np.random.randint(300, 4000, 15),
            'Video Plays 75%': np.random.randint(200, 2000, 15),
            'Video Plays 95%': np.random.randint(100, 1000, 15),
            'ThruPlay Actions': np.random.randint(100, 1500, 15),
            'Link Clicks': np.random.randint(50, 1000, 15),
            'Fifteen-second video views': np.random.randint(300, 3000, 15),
            'Avg Watch Time (s)': np.random.uniform(5, 25, 15),
            'Cost': np.random.uniform(50, 500, 15),
            'Conversions': np.random.randint(0, 50, 15),
            'Revenue': np.random.uniform(0, 2000, 15)
        }
        st.session_state.df = pd.DataFrame(demo_data)
        st.success("✅ Demo data loaded!")
    
    if st.session_state.df is not None:
        st.markdown("---")
        st.markdown("### 🎯 Filters")
        
        df = st.session_state.df
        
        # Platform filter
        platforms = st.multiselect(
            "Platform",
            options=df['Platform'].unique() if 'Platform' in df.columns else [],
            default=df['Platform'].unique() if 'Platform' in df.columns else []
        )
        
        # Date range (simulated)
        date_range = st.select_slider(
            "Time Period",
            options=["Last 7 days", "Last 14 days", "Last 30 days", "Last 90 days"],
            value="Last 30 days"
        )
        
        # Performance filter
        performance_filter = st.radio(
            "Performance",
            ["All Creatives", "Top Performers", "Need Optimization", "Underperforming"],
            index=0
        )
    
    st.markdown("---")
    st.markdown("### ⚙️ Benchmark Settings")
    
    with st.expander("Customize Industry Benchmarks"):
        st.session_state.benchmarks['thumb_stop_rate'] = st.slider(
            "Thumb-stop Rate (%)", 10, 50, 25
        )
        st.session_state.benchmarks['hook_rate'] = st.slider(
            "Hook Rate (%)", 3, 15, 8
        )
        st.session_state.benchmarks['hold_rate'] = st.slider(
            "Hold Rate (%)", 20, 50, 35
        )
        st.session_state.benchmarks['ctr'] = st.slider(
            "CTR (%)", 0.5, 3.0, 1.5, step=0.1
        )

# Helper functions
def calculate_motion_scores(df):
    """Calculate Motion-style performance scores"""
    
    # Thumb-stop Score (First 3 seconds)
    if 'Three-second video views' in df.columns and 'Impressions' in df.columns:
        df['Thumb-stop Rate (%)'] = (df['Three-second video views'] / df['Impressions'] * 100).round(2)
        df['Thumb-stop Score'] = df['Thumb-stop Rate (%)'].apply(
            lambda x: min(100, (x / st.session_state.benchmarks['thumb_stop_rate']) * 50)
        )
    
    # Hook Score (3s views / impressions, but weighted)
    df['Hook Rate (%)'] = df['Thumb-stop Rate (%)'] if 'Thumb-stop Rate (%)' in df.columns else 0
    df['Hook Score'] = df['Hook Rate (%)'].apply(
        lambda x: min(100, (x / st.session_state.benchmarks['hook_rate']) * 50)
    )
    
    # Hold Score (Retention through video)
    if 'ThruPlay Actions' in df.columns and 'Three-second video views' in df.columns:
        df['Hold Rate (%)'] = df.apply(
            lambda row: round((row['ThruPlay Actions'] / row['Three-second video views'] * 100), 2) 
            if row['Three-second video views'] > 0 else 0, axis=1
        )
        df['Hold Score'] = df['Hold Rate (%)'].apply(
            lambda x: min(100, (x / st.session_state.benchmarks['hold_rate']) * 50)
        )
    
    # Click Score (CTR-based)
    if 'Link Clicks' in df.columns and 'Impressions' in df.columns:
        df['CTR (%)'] = (df['Link Clicks'] / df['Impressions'] * 100).round(3)
        df['Click Score'] = df['CTR (%)'].apply(
            lambda x: min(100, (x / st.session_state.benchmarks['ctr']) * 50)
        )
    
    # Overall Performance Score (Motion-style composite)
    score_columns = ['Thumb-stop Score', 'Hook Score', 'Hold Score', 'Click Score']
    available_scores = [col for col in score_columns if col in df.columns]
    if available_scores:
        df['Overall Score'] = df[available_scores].mean(axis=1).round(0)
    
    # Performance Tier
    def get_tier(score):
        if score >= 80: return "🏆 Excellent"
        elif score >= 60: return "✅ Good"
        elif score >= 40: return "⚠️ Average"
        else: return "🔴 Poor"
    
    if 'Overall Score' in df.columns:
        df['Performance Tier'] = df['Overall Score'].apply(get_tier)
    
    return df

def generate_retention_curve(row):
    """Generate retention curve data points"""
    points = []
    
    # Create retention points
    if 'Impressions' in row:
        total = row['Impressions']
        points.append({'time': 0, 'retention': 100})
        
        if 'Three-second video views' in row:
            points.append({'time': 3, 'retention': (row['Three-second video views'] / total * 100)})
        
        if 'Video Plays 25%' in row:
            points.append({'time': 7.5, 'retention': (row['Video Plays 25%'] / total * 100)})
        
        if 'Fifteen-second video views' in row:
            points.append({'time': 15, 'retention': (row['Fifteen-second video views'] / total * 100)})
        
        if 'Video Plays 50%' in row:
            points.append({'time': 15, 'retention': (row['Video Plays 50%'] / total * 100)})
        
        if 'Video Plays 75%' in row:
            points.append({'time': 22.5, 'retention': (row['Video Plays 75%'] / total * 100)})
        
        if 'ThruPlay Actions' in row:
            points.append({'time': 30, 'retention': (row['ThruPlay Actions'] / total * 100)})
    
    return points

def generate_insights(row):
    """Generate Motion-style actionable insights"""
    insights = []
    
    # Thumb-stop insights
    if 'Thumb-stop Rate (%)' in row:
        rate = row['Thumb-stop Rate (%)']
        benchmark = st.session_state.benchmarks['thumb_stop_rate']
        if rate < benchmark * 0.7:
            insights.append({
                'type': 'critical',
                'message': f'⚠️ Thumb-stop rate ({rate:.1f}%) is significantly below benchmark ({benchmark}%). Consider a more engaging first frame.'
            })
        elif rate > benchmark * 1.3:
            insights.append({
                'type': 'success',
                'message': f'🎯 Excellent thumb-stop rate ({rate:.1f}%)! This opening is {((rate/benchmark - 1) * 100):.0f}% above benchmark.'
            })
    
    # Hold rate insights
    if 'Hold Rate (%)' in row:
        hold = row['Hold Rate (%)']
        if hold < 20:
            insights.append({
                'type': 'warning',
                'message': f'📉 Low hold rate ({hold:.1f}%). The content loses viewers quickly after the hook. Review pacing between 3-15 seconds.'
            })
        elif hold > 40:
            insights.append({
                'type': 'success',
                'message': f'💪 Strong hold rate ({hold:.1f}%). This creative maintains attention exceptionally well.'
            })
    
    # CTR insights
    if 'CTR (%)' in row:
        ctr = row['CTR (%)']
        if ctr < 0.5:
            insights.append({
                'type': 'warning',
                'message': f'🔗 Low CTR ({ctr:.2f}%). The CTA may need to be stronger or appear earlier.'
            })
    
    # Average watch time insights
    if 'Avg Watch Time (s)' in row:
        awt = row['Avg Watch Time (s)']
        if awt < 5:
            insights.append({
                'type': 'critical',
                'message': f'⏱️ Very low average watch time ({awt:.1f}s). This creative needs significant optimization.'
            })
        elif awt > 15:
            insights.append({
                'type': 'success',
                'message': f'⭐ Exceptional watch time ({awt:.1f}s). Use this as a template for other creatives.'
            })
    
    return insights

# Main content area
if st.session_state.df is not None:
    df = calculate_motion_scores(st.session_state.df)
    
    # Apply filters if any
    if 'platforms' in locals() and platforms:
        df = df[df['Platform'].isin(platforms)]
    
    # Tabs (Motion-style)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Performance Overview",
        "📈 Retention Analysis", 
        "🎯 Creative Scores",
        "💡 Insights & Actions",
        "📥 Export Report"
    ])
    
    with tab1:
        # KPI Cards
        st.markdown("### Key Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            avg_thumb = df['Thumb-stop Rate (%)'].mean() if 'Thumb-stop Rate (%)' in df.columns else 0
            benchmark = st.session_state.benchmarks['thumb_stop_rate']
            delta = ((avg_thumb - benchmark) / benchmark * 100)
            st.metric(
                "Avg Thumb-stop",
                f"{avg_thumb:.1f}%",
                f"{delta:+.1f}% vs benchmark",
                delta_color="normal" if delta > 0 else "inverse"
            )
        
        with col2:
            avg_hold = df['Hold Rate (%)'].mean() if 'Hold Rate (%)' in df.columns else 0
            benchmark = st.session_state.benchmarks['hold_rate']
            delta = ((avg_hold - benchmark) / benchmark * 100)
            st.metric(
                "Avg Hold Rate",
                f"{avg_hold:.1f}%",
                f"{delta:+.1f}% vs benchmark",
                delta_color="normal" if delta > 0 else "inverse"
            )
        
        with col3:
            avg_ctr = df['CTR (%)'].mean() if 'CTR (%)' in df.columns else 0
            benchmark = st.session_state.benchmarks['ctr']
            delta = ((avg_ctr - benchmark) / benchmark * 100)
            st.metric(
                "Avg CTR",
                f"{avg_ctr:.2f}%",
                f"{delta:+.1f}% vs benchmark",
                delta_color="normal" if delta > 0 else "inverse"
            )
        
        with col4:
            avg_score = df['Overall Score'].mean() if 'Overall Score' in df.columns else 0
            st.metric(
                "Portfolio Score",
                f"{avg_score:.0f}/100",
                "Motion Score™"
            )
        
        with col5:
            total_creatives = len(df)
            excellent = len(df[df['Overall Score'] >= 80]) if 'Overall Score' in df.columns else 0
            st.metric(
                "Top Performers",
                f"{excellent}/{total_creatives}",
                f"{(excellent/total_creatives*100):.0f}% excellent"
            )
        
        # Creative Performance Grid
        st.markdown("### Creative Performance Matrix")
        
        for idx, row in df.head(10).iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{row['Creative Name']}**")
                    if 'Platform' in row:
                        platform_color = {
                            'Facebook': '#1877f2',
                            'TikTok': '#000000',
                            'YouTube': '#ff0000'
                        }.get(row['Platform'], '#666')
                        st.markdown(
                            f'<span style="color: {platform_color}; font-size: 12px;">● {row["Platform"]}</span>',
                            unsafe_allow_html=True
                        )
                
                with col2:
                    # Score pills
                    scores_html = ""
                    if 'Thumb-stop Score' in row:
                        color_class = 'score-excellent' if row['Thumb-stop Score'] > 80 else 'score-good' if row['Thumb-stop Score'] > 50 else 'score-poor'
                        scores_html += f'<span class="metric-badge {color_class}">Thumb: {row["Thumb-stop Score"]:.0f}</span>'
                    
                    if 'Hold Score' in row:
                        color_class = 'score-excellent' if row['Hold Score'] > 80 else 'score-good' if row['Hold Score'] > 50 else 'score-poor'
                        scores_html += f'<span class="metric-badge {color_class}">Hold: {row["Hold Score"]:.0f}</span>'
                    
                    if 'Click Score' in row:
                        color_class = 'score-excellent' if row['Click Score'] > 80 else 'score-good' if row['Click Score'] > 50 else 'score-poor'
                        scores_html += f'<span class="metric-badge {color_class}">Click: {row["Click Score"]:.0f}</span>'
                    
                    st.markdown(scores_html, unsafe_allow_html=True)
                
                with col3:
                    if 'Hold Rate (%)' in row:
                        st.markdown(f"**Retention:** {row['Hold Rate (%)']:.1f}%")
                    if 'CTR (%)' in row:
                        st.markdown(f"**CTR:** {row['CTR (%)']:.2f}%")
                
                with col4:
                    if 'Overall Score' in row:
                        score_color = '#006644' if row['Overall Score'] > 80 else '#7a4100' if row['Overall Score'] > 50 else '#cf222e'
                        st.markdown(
                            f'<div style="text-align: center; font-size: 24px; font-weight: bold; color: {score_color};">{row["Overall Score"]:.0f}</div>'
                            f'<div style="text-align: center; font-size: 11px; color: #666;">Overall Score</div>',
                            unsafe_allow_html=True
                        )
                
                with col5:
                    if st.button("View Details", key=f"view_{idx}"):
                        st.info(f"Detailed view for {row['Creative Name']}")
                
                st.markdown("---")
    
    with tab2:
        st.markdown("### 📈 Retention Curve Analysis")
        st.caption("Understand where viewers drop off")
        
        # Select creative for detailed analysis
        selected_creative = st.selectbox(
            "Select Creative",
            options=df['Creative Name'].tolist(),
            index=0
        )
        
        selected_row = df[df['Creative Name'] == selected_creative].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Retention curve visualization (simplified)
            retention_points = generate_retention_curve(selected_row)
            
            if retention_points:
                # Create a simple line chart representation
                st.markdown("#### Retention Curve")
                
                # Create retention visualization
                chart_data = pd.DataFrame(retention_points)
                st.line_chart(chart_data.set_index('time')['retention'], height=400)
                
                # Key drop-off points
                st.markdown("#### 🎯 Key Drop-off Points")
                
                if len(retention_points) > 1:
                    for i in range(1, len(retention_points)):
                        drop = retention_points[i-1]['retention'] - retention_points[i]['retention']
                        if drop > 10:
                            st.warning(f"📉 {drop:.1f}% drop at {retention_points[i]['time']}s mark")
        
        with col2:
            st.markdown("#### 📊 Retention Metrics")
            
            metrics_html = f"""
            <div class="performance-card">
                <h4>Performance vs Benchmark</h4>
            """
            
            if 'Thumb-stop Rate (%)' in selected_row:
                rate = selected_row['Thumb-stop Rate (%)']
                benchmark = st.session_state.benchmarks['thumb_stop_rate']
                status = "above-benchmark" if rate > benchmark else "below-benchmark"
                metrics_html += f"""
                <div style="margin: 10px 0;">
                    <span style="color: #666;">0-3s Retention:</span>
                    <strong>{rate:.1f}%</strong>
                    <span class="benchmark-indicator {status}">
                        {'+' if rate > benchmark else ''}{((rate - benchmark) / benchmark * 100):.0f}%
                    </span>
                </div>
                """
            
            if 'Hold Rate (%)' in selected_row:
                rate = selected_row['Hold Rate (%)']
                benchmark = st.session_state.benchmarks['hold_rate']
                status = "above-benchmark" if rate > benchmark else "below-benchmark"
                metrics_html += f"""
                <div style="margin: 10px 0;">
                    <span style="color: #666;">Completion Rate:</span>
                    <strong>{rate:.1f}%</strong>
                    <span class="benchmark-indicator {status}">
                        {'+' if rate > benchmark else ''}{((rate - benchmark) / benchmark * 100):.0f}%
                    </span>
                </div>
                """
            
            metrics_html += "</div>"
            st.markdown(metrics_html, unsafe_allow_html=True)
            
            # Recommendations based on retention
            st.markdown("#### 💡 Optimization Tips")
            
            insights = generate_insights(selected_row)
            for insight in insights[:3]:  # Show top 3 insights
                if insight['type'] == 'success':
                    st.success(insight['message'])
                elif insight['type'] == 'warning':
                    st.warning(insight['message'])
                elif insight['type'] == 'critical':
                    st.error(insight['message'])
    
    with tab3:
        st.markdown("### 🎯 Creative Scoring Dashboard")
        
        # Scoring methodology
        with st.expander("📖 How Scores Are Calculated"):
            st.markdown("""
            **Motion-Style Scoring System:**
            
            - **Thumb-stop Score**: Based on 3-second view rate vs industry benchmark
            - **Hook Score**: Weighted calculation of initial engagement
            - **Hold Score**: Retention rate through the video
            - **Click Score**: CTR performance vs benchmark
            - **Overall Score**: Weighted average of all scores
            
            Scores above 80 are considered excellent, 50-80 good, below 50 needs improvement.
            """)
        
        # Score distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Score Distribution")
            if 'Overall Score' in df.columns:
                # Create bins for score distribution
                bins = [0, 40, 60, 80, 100]
                labels = ['Poor (0-40)', 'Average (40-60)', 'Good (60-80)', 'Excellent (80-100)']
                df['Score Range'] = pd.cut(df['Overall Score'], bins=bins, labels=labels, include_lowest=True)
                
                distribution = df['Score Range'].value_counts()
                st.bar_chart(distribution)
        
        with col2:
            st.markdown("#### Top Performers")
            if 'Overall Score' in df.columns:
                top_5 = df.nlargest(5, 'Overall Score')[['Creative Name', 'Overall Score', 'Performance Tier']]
                for _, row in top_5.iterrows():
                    st.markdown(f"{row['Performance Tier']} **{row['Creative Name']}** - Score: {row['Overall Score']:.0f}")
        
        # Detailed scores table
        st.markdown("#### Detailed Scores")
        
        score_columns = ['Creative Name', 'Thumb-stop Score', 'Hook Score', 'Hold Score', 'Click Score', 'Overall Score', 'Performance Tier']
        available_columns = [col for col in score_columns if col in df.columns]
        
        st.dataframe(
            df[available_columns].style.format({
                'Thumb-stop Score': '{:.0f}',
                'Hook Score': '{:.0f}',
                'Hold Score': '{:.0f}',
                'Click Score': '{:.0f}',
                'Overall Score': '{:.0f}'
            }),
            use_container_width=True,
            height=400
        )
    
    with tab4:
        st.markdown("### 💡 AI-Powered Insights & Actions")
        
        # Generate insights for all creatives
        all_insights = []
        for _, row in df.iterrows():
            creative_insights = generate_insights(row)
            if creative_insights:
                all_insights.append({
                    'creative': row['Creative Name'],
                    'insights': creative_insights
                })
        
        # Summary insights
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 🚀 Quick Wins")
            
            # Find creatives that are close to being excellent
            if 'Overall Score' in df.columns:
                almost_excellent = df[(df['Overall Score'] >= 70) & (df['Overall Score'] < 80)]
                if not almost_excellent.empty:
                    for _, row in almost_excellent.head(3).iterrows():
                        st.info(f"**{row['Creative Name']}** is close to excellent (Score: {row['Overall Score']:.0f}). Small optimizations could push it over 80.")
        
        with col2:
            st.markdown("#### ⚠️ Urgent Actions")
            
            # Find worst performers
            if 'Overall Score' in df.columns:
                poor_performers = df[df['Overall Score'] < 40]
                if not poor_performers.empty:
                    for _, row in poor_performers.head(3).iterrows():
                        st.error(f"**{row['Creative Name']}** needs immediate attention (Score: {row['Overall Score']:.0f})")
        
        # Detailed insights by creative
        st.markdown("#### 📋 Creative-by-Creative Analysis")
        
        for item in all_insights[:5]:  # Show first 5
            with st.expander(f"{item['creative']} - {len(item['insights'])} insights"):
                for insight in item['insights']:
                    if insight['type'] == 'success':
                        st.success(insight['message'])
                    elif insight['type'] == 'warning':
                        st.warning(insight['message'])
                    elif insight['type'] == 'critical':
                        st.error(insight['message'])
        
        # Action plan
        st.markdown("#### 📌 Recommended Action Plan")
        
        st.markdown("""
        Based on your portfolio analysis:
        
        1. **Immediate Actions:**
           - Pause creatives with Overall Score < 40
           - Increase budget on creatives with Score > 80
           - A/B test new hooks for low thumb-stop performers
        
        2. **This Week:**
           - Review and optimize CTAs for low Click Score creatives
           - Create variations of top performers
           - Test shorter versions for low hold rate creatives
        
        3. **This Month:**
           - Develop creative templates based on top performers
           - Establish creative testing framework
           - Set up automated performance monitoring
        """)
    
    with tab5:
        st.markdown("### 📥 Export Professional Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### CSV Export Options")
            
            # Full data export
            csv_full = df.to_csv(index=False)
            st.download_button(
                label="📊 Download Full Dataset",
                data=csv_full,
                file_name=f"creative_analysis_full_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # Scores only export
            if 'Overall Score' in df.columns:
                score_cols = ['Creative Name', 'Overall Score', 'Thumb-stop Score', 'Hook Score', 'Hold Score', 'Click Score', 'Performance Tier']
                score_cols = [col for col in score_cols if col in df.columns]
                csv_scores = df[score_cols].to_csv(index=False)
                st.download_button(
                    label="🎯 Download Scores Only",
                    data=csv_scores,
                    file_name=f"creative_scores_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.markdown("#### Executive Summary")
            
            if 'Overall Score' in df.columns:
                excellent_count = len(df[df['Overall Score'] >= 80])
                good_count = len(df[(df['Overall Score'] >= 60) & (df['Overall Score'] < 80)])
                needs_work = len(df[df['Overall Score'] < 60])
                
                summary = f"""
CREATIVE PERFORMANCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Platform: Motion-Style Analysis

═══════════════════════════════════════

PORTFOLIO OVERVIEW
Total Creatives: {len(df)}
Average Score: {df['Overall Score'].mean():.0f}/100

PERFORMANCE BREAKDOWN
🏆 Excellent (80-100): {excellent_count} creatives
✅ Good (60-80): {good_count} creatives
⚠️ Needs Improvement (<60): {needs_work} creatives

KEY METRICS vs BENCHMARKS
Thumb-stop: {df['Thumb-stop Rate (%)'].mean():.1f}% (Benchmark: {st.session_state.benchmarks['thumb_stop_rate']}%)
Hold Rate: {df['Hold Rate (%)'].mean():.1f}% (Benchmark: {st.session_state.benchmarks['hold_rate']}%)
CTR: {df['CTR (%)'].mean():.2f}% (Benchmark: {st.session_state.benchmarks['ctr']}%)

TOP PERFORMERS
{df.nlargest(3, 'Overall Score')[['Creative Name', 'Overall Score']].to_string(index=False)}

RECOMMENDED ACTIONS
1. Scale: {excellent_count} high-performing creatives
2. Optimize: {good_count} creatives with potential
3. Replace: {needs_work} underperforming creatives

═══════════════════════════════════════
                """
                
                st.text_area("Copy Executive Summary", summary, height=500)

else:
    # Welcome screen
    st.markdown("""
    <div class="performance-card" style="text-align: center; padding: 60px 20px;">
        <h2>Welcome to Creative Intelligence Platform</h2>
        <p style="color: #586069; font-size: 18px; margin: 20px 0;">
            Transform your creative performance data into actionable insights with Motion-style analytics
        </p>
        
        <h3>What You'll Get:</h3>
        <div style="display: flex; justify-content: center; gap: 40px; margin: 30px 0;">
            <div>
                <h4>📊 Performance Scores</h4>
                <p>0-100 scoring system</p>
            </div>
            <div>
                <h4>📈 Retention Curves</h4>
                <p>Second-by-second analysis</p>
            </div>
            <div>
                <h4>🎯 Benchmarking</h4>
                <p>Industry comparisons</p>
            </div>
            <div>
                <h4>💡 AI Insights</h4>
                <p>Actionable recommendations</p>
            </div>
        </div>
        
        <p style="margin-top: 40px;">
            <strong>👈 Click "Load Demo Data" in the sidebar to explore the platform</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #586069; font-size: 12px;">
        Built with inspiration from Motion • Creative Intelligence Platform • 
        <a href="https://motionapp.com" target="_blank" style="color: #0969da;">Learn More</a>
    </div>
    """,
    unsafe_allow_html=True
)
