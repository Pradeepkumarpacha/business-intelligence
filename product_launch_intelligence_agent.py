import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.firecrawl import FirecrawlTools
from dotenv import load_dotenv
from datetime import datetime
from textwrap import dedent
import os

st.set_page_config(
    page_title="AI Business Intelligence Platform",
    page_icon="âš›ï¸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Fission Labs styling
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    
    /* Custom header styling */
    .custom-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 40px;
        border-radius: 24px;
        margin-bottom: 30px;
        border: 1px solid #334155;
        position: relative;
        overflow: hidden;
    }
    
    .custom-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 30px;
    }
    
    .header-text h1 {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 12px;
        line-height: 1.2;
        font-family: 'Inter', sans-serif;
    }
    
    .header-text p {
        font-size: 1.2rem;
        color: #e2e8f0;
        font-weight: 400;
        max-width: 600px;
        font-family: 'Inter', sans-serif;
    }
    
    .logo-container img {
        width: 200px;
        height: auto;
        border-radius: 12px;
        transition: transform 0.3s ease;
    }
    
    .logo-container img:hover {
        transform: scale(1.05);
    }
    
    /* Hide default Streamlit header */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Style the sidebar */
    .css-1d391kg {
        background-color: #1a1a2e;
    }
    
    /* Custom input styling */
    .stTextInput > div > div > input {
        background-color: #16213e;
        border: 2px solid #334155;
        border-radius: 12px;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00b8e6 0%, #0284c7 100%);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #16213e;
        border: 1px solid #334155;
        border-radius: 12px;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%);
        color: white;
    }
    
    /* Success/warning styling */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 12px;
        color: #22c55e;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .css-1d391kg .stMarkdown {
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Custom header with Fission Labs branding
st.markdown("""
<div class="custom-header">
    <div class="header-content">
        <div class="header-text">
            <h1>âš›ï¸ Fission Labs</h1>
            <p>AI-powered insights for GTM, Product Marketing & Growth Teams</p>
        </div>
        <div class="logo-container">
            <img src="https://cdn.prod.website-files.com/61ffed246e785f28c1a44633/63edbbc5b6b5f37b605cf0f2_fl-footer-p-500.png" alt="Fission Labs Logo" />
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

load_dotenv()

st.sidebar.header("ðŸ”‘ API Configuration")
with st.sidebar.container():
    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Required for AI agent functionality"
    )
    
    firecrawl_key = st.text_input(
        "Firecrawl API Key",
        type="password",
        value=os.getenv("FIRECRAWL_API_KEY", ""),
        help="Required for web search and crawling"
    )

# Set environment variables
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
if firecrawl_key:
    os.environ["FIRECRAWL_API_KEY"] = firecrawl_key

# Initialize session state
if 'competitor_response' not in st.session_state:
    st.session_state.competitor_response = None
if 'sentiment_response' not in st.session_state:
    st.session_state.sentiment_response = None
if 'metrics_response' not in st.session_state:
    st.session_state.metrics_response = None

# Create agents only if API keys are provided
if openai_key and firecrawl_key:
    launch_analyst = Agent(
        name="Product Launch Analyst",
        description=dedent("""
        You are a senior Go-To-Market strategist who evaluates competitor product launches with a critical, evidence-driven lens.
        
        Your objective is to uncover:
        â€¢ How the product is positioned in the market
        â€¢ Which launch tactics drove success (strengths)  
        â€¢ Where execution fell short (weaknesses)
        â€¢ Actionable learnings competitors can leverage
        
        Always cite observable signals (messaging, pricing actions, channel mix, timing, engagement metrics). Maintain a crisp, executive tone and focus on strategic value.
        
        IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o-mini"),
        tools=[FirecrawlTools(search=True, crawl=True, poll_interval=10)],
        show_tool_calls=True,
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=2,
    )

    sentiment_analyst = Agent(
        name="Market Sentiment Specialist",
        description=dedent("""
        You are a market research expert specializing in sentiment analysis and consumer perception tracking.
        
        Your expertise includes:
        â€¢ Analyzing social media sentiment and customer feedback
        â€¢ Identifying positive and negative sentiment drivers
        â€¢ Tracking brand perception trends across platforms  
        â€¢ Monitoring customer satisfaction and review patterns
        â€¢ Providing actionable insights on market reception
        
        Focus on extracting sentiment signals from social platforms, review sites, forums, and customer feedback channels.
        
        IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o-mini"),
        tools=[FirecrawlTools(search=True, crawl=True, poll_interval=10)],
        show_tool_calls=True,
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=2,
    )

    metrics_analyst = Agent(
        name="Launch Metrics Specialist",
        description=dedent("""
        You are a product launch performance analyst who specializes in tracking and analyzing launch KPIs.
        
        Your focus areas include:
        â€¢ User adoption and engagement metrics
        â€¢ Revenue and business performance indicators
        â€¢ Market penetration and growth rates
        â€¢ Press coverage and media attention analysis
        â€¢ Social media traction and viral coefficient tracking
        â€¢ Competitive market share analysis
        
        Always provide quantitative insights with context and benchmark against industry standards when possible.
        
        IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o-mini"),
        tools=[FirecrawlTools(search=True, crawl=True, poll_interval=10)],
        show_tool_calls=True,
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=2,
    )
else:
    launch_analyst = None
    sentiment_analyst = None
    metrics_analyst = None

def expand_competitor_report(bullet_text: str, competitor: str) -> str:
    if not launch_analyst:
        st.error("âš ï¸ Please enter both API keys in the sidebar first.")
        return ""
    
    prompt = (
        f"Transform the insight bullets below into a professional launch review for product managers analysing {competitor}.\n\n"
        f"Produce well-structured **Markdown** with a mix of tables, call-outs and concise bullet points --- avoid long paragraphs.\n\n"
        f"=== FORMAT SPECIFICATION ===\n"
        f"# {competitor} -- Launch Review\n\n"
        f"## 1. Market & Product Positioning\n"
        f"â€¢ Bullet point summary of how the product is positioned (max 6 bullets).\n\n"
        f"## 2. Launch Strengths\n"
        f"| Strength | Evidence / Rationale |\n|---|---|\n| ... | ... | (add 4-6 rows)\n\n"
        f"## 3. Launch Weaknesses\n"
        f"| Weakness | Evidence / Rationale |\n|---|---|\n| ... | ... | (add 4-6 rows)\n\n"
        f"## 4. Strategic Takeaways for Competitors\n"
        f"1. ... (max 5 numbered recommendations)\n\n"
        f"=== SOURCE BULLETS ===\n{bullet_text}\n\n"
        f"Guidelines:\n"
        f"â€¢ Populate the tables with specific points derived from the bullets.\n"
        f"â€¢ Only include rows that contain meaningful data; omit any blank entries."
    )
    
    resp = launch_analyst.run(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)

def expand_sentiment_report(bullet_text: str, competitor: str) -> str:
    if not sentiment_analyst:
        st.error("âš ï¸ Please enter both API keys in the sidebar first.")
        return ""
    
    prompt = (
        f"Transform the sentiment bullets below into a comprehensive market sentiment report for {competitor}.\n\n"
        f"Create well-structured **Markdown** with tables, metrics, and clear insights.\n\n"
        f"=== SOURCE BULLETS ===\n{bullet_text}"
    )
    
    resp = sentiment_analyst.run(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)

def expand_metrics_report(bullet_text: str, competitor: str) -> str:
    if not metrics_analyst:
        st.error("âš ï¸ Please enter both API keys in the sidebar first.")
        return ""
    
    prompt = (
        f"Transform the metrics bullets below into a detailed launch performance report for {competitor}.\n\n"
        f"Create well-structured **Markdown** with KPI tables, trend analysis, and benchmarks.\n\n"
        f"=== SOURCE BULLETS ===\n{bullet_text}"
    )
    
    resp = metrics_analyst.run(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)

# Company input section
st.subheader("ðŸ¢ Company Analysis")
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input(
            label="Company Name",
            placeholder="Enter company name (e.g., OpenAI, Tesla, Spotify)",
            help="This company will be analyzed by all three specialized agents",
            label_visibility="collapsed"
        )
    with col2:
        if company_name:
            st.success(f"âœ“ Ready to analyze **{company_name}**")

# Create tabs for analysis types
analysis_tabs = st.tabs(["ðŸ” Competitor Analysis", "ðŸ’¬ Market Sentiment", "ðŸ“ˆ Launch Metrics"])

# Competitor Analysis Tab
with analysis_tabs[0]:
    if company_name:
        analyze_btn = st.button(
            "ðŸš€ Analyze Competitor Strategy",
            key="competitor_btn",
            type="primary",
            use_container_width=True
        )
        
        if analyze_btn:
            if not launch_analyst:
                st.error("âš ï¸ Please enter both API keys in the sidebar first.")
            else:
                with st.spinner("ðŸ” Launch Analyst gathering competitive intelligence..."):
                    try:
                        bullets = launch_analyst.run(
                            f"Generate up to 16 evidence-based insight bullets about {company_name}'s most recent product launches.\n"
                            f"Format requirements:\n"
                            f"â€¢ Start every bullet with exactly one tag: Positioning | Strength | Weakness | Learning\n"
                            f"â€¢ Follow the tag with a concise statement (max 30 words) referencing concrete observations: messaging, differentiation, pricing, channel selection, timing, engagement metrics, or customer feedback."
                        )
                        
                        long_text = expand_competitor_report(
                            bullets.content if hasattr(bullets, "content") else str(bullets),
                            company_name
                        )
                        st.session_state.competitor_response = long_text
                        st.success("âœ… Competitor analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"âŒ Error: {e}")
    
    # Display results
    if st.session_state.competitor_response:
        st.markdown(st.session_state.competitor_response)

# Market Sentiment Tab
with analysis_tabs[1]:
    if company_name:
        analyze_btn = st.button(
            "ðŸ’¬ Analyze Market Sentiment",
            key="sentiment_btn",
            type="primary",
            use_container_width=True
        )
        
        if analyze_btn:
            if not sentiment_analyst:
                st.error("âš ï¸ Please enter both API keys in the sidebar first.")
            else:
                with st.spinner("ðŸ’¬ Sentiment Specialist analyzing market perception..."):
                    try:
                        bullets = sentiment_analyst.run(
                            f"Analyze market sentiment for {company_name} across social media, reviews, and customer feedback channels. "
                            f"Provide specific sentiment signals, positive/negative drivers, and actionable insights."
                        )
                        
                        long_text = expand_sentiment_report(
                            bullets.content if hasattr(bullets, "content") else str(bullets),
                            company_name
                        )
                        st.session_state.sentiment_response = long_text
                        st.success("âœ… Sentiment analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"âŒ Error: {e}")
    
    # Display results
    if st.session_state.sentiment_response:
        st.markdown(st.session_state.sentiment_response)

# Launch Metrics Tab
with analysis_tabs[2]:
    if company_name:
        analyze_btn = st.button(
            "ðŸ“ˆ Analyze Launch Metrics",
            key="metrics_btn",
            type="primary",
            use_container_width=True
        )
        
        if analyze_btn:
            if not metrics_analyst:
                st.error("âš ï¸ Please enter both API keys in the sidebar first.")
            else:
                with st.spinner("ðŸ“ˆ Metrics Specialist tracking launch performance..."):
                    try:
                        bullets = metrics_analyst.run(
                            f"Track and analyze launch performance metrics for {company_name}. "
                            f"Focus on adoption rates, engagement metrics, press coverage, and competitive benchmarks."
                        )
                        
                        long_text = expand_metrics_report(
                            bullets.content if hasattr(bullets, "content") else str(bullets),
                            company_name
                        )
                        st.session_state.metrics_response = long_text
                        st.success("âœ… Metrics analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"âŒ Error: {e}")
    
    # Display results
    if st.session_state.metrics_response:
        st.markdown(st.session_state.metrics_response)

# Sidebar status
with st.sidebar.container():
    st.markdown("### ðŸ¤– System Status")
    if openai_key and firecrawl_key:
        st.success("âœ… All agents ready")
    else:
        st.error("âŒ API keys required")

# Analysis status
if company_name:
    with st.sidebar.container():
        st.markdown("### ðŸ“Š Analysis Status")
        st.markdown(f"**Company:** {company_name}")
        
        status_items = [
            ("ðŸ”", "Competitor Analysis", st.session_state.get('competitor_response')),
            ("ðŸ’¬", "Sentiment Analysis", st.session_state.get('sentiment_response')),
            ("ðŸ“ˆ", "Metrics Analysis", st.session_state.get('metrics_response'))
        ]
        
        for icon, name, status in status_items:
            if status:
                st.success(f"{icon} {name} âœ“")
            else:
                st.info(f"{icon} {name} â³")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 20px;'>
    <p>Powered by <strong>Fission Labs</strong> â€¢ AI-Led Innovation â€¢ Engineering Excellence</p>
    <p><a href='https://linkedin.com/in/pradeepkumarpacha' target='_blank' style='color: #00d4ff;'>LinkedIn</a> | 
    <a href='mailto:pradeep.pacha@gmail.com' style='color: #00d4ff;'>Contact</a></p>
</div>
""", unsafe_allow_html=True)


