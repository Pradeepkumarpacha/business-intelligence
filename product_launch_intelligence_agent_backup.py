import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.firecrawl import FirecrawlTools
from dotenv import load_dotenv
from datetime import datetime
from textwrap import dedent
import os

st.set_page_config(
    page_title="Product Intelligence Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

st.sidebar.header("🔑 API Configuration")
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
        • How the product is positioned in the market
        • Which launch tactics drove success (strengths)  
        • Where execution fell short (weaknesses)
        • Actionable learnings competitors can leverage
        
        Always cite observable signals (messaging, pricing actions, channel mix, timing, engagement metrics). Maintain a crisp, executive tone and focus on strategic value.
        
        IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o"),
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
        • Analyzing social media sentiment and customer feedback
        • Identifying positive and negative sentiment drivers
        • Tracking brand perception trends across platforms  
        • Monitoring customer satisfaction and review patterns
        • Providing actionable insights on market reception
        
        Focus on extracting sentiment signals from social platforms, review sites, forums, and customer feedback channels.
        
        IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o"),
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
        • User adoption and engagement metrics
        • Revenue and business performance indicators
        • Market penetration and growth rates
        • Press coverage and media attention analysis
        • Social media traction and viral coefficient tracking
        • Competitive market share analysis
        
        Always provide quantitative insights with context and benchmark against industry standards when possible.
        
        IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o"),
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
        st.error("⚠️ Please enter both API keys in the sidebar first.")
        return ""
    
    prompt = (
        f"Transform the insight bullets below into a professional launch review for product managers analysing {competitor}.\n\n"
        f"Produce well-structured **Markdown** with a mix of tables, call-outs and concise bullet points --- avoid long paragraphs.\n\n"
        f"=== FORMAT SPECIFICATION ===\n"
        f"# {competitor} -- Launch Review\n\n"
        f"## 1. Market & Product Positioning\n"
        f"• Bullet point summary of how the product is positioned (max 6 bullets).\n\n"
        f"## 2. Launch Strengths\n"
        f"| Strength | Evidence / Rationale |\n|---|---|\n| ... | ... | (add 4-6 rows)\n\n"
        f"## 3. Launch Weaknesses\n"
        f"| Weakness | Evidence / Rationale |\n|---|---|\n| ... | ... | (add 4-6 rows)\n\n"
        f"## 4. Strategic Takeaways for Competitors\n"
        f"1. ... (max 5 numbered recommendations)\n\n"
        f"=== SOURCE BULLETS ===\n{bullet_text}\n\n"
        f"Guidelines:\n"
        f"• Populate the tables with specific points derived from the bullets.\n"
        f"• Only include rows that contain meaningful data; omit any blank entries."
    )
    
    resp = launch_analyst.run(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)

def expand_sentiment_report(bullet_text: str, competitor: str) -> str:
    if not sentiment_analyst:
        st.error("⚠️ Please enter both API keys in the sidebar first.")
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
        st.error("⚠️ Please enter both API keys in the sidebar first.")
        return ""
    
    prompt = (
        f"Transform the metrics bullets below into a detailed launch performance report for {competitor}.\n\n"
        f"Create well-structured **Markdown** with KPI tables, trend analysis, and benchmarks.\n\n"
        f"=== SOURCE BULLETS ===\n{bullet_text}"
    )
    
    resp = metrics_analyst.run(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)

# Main UI
st.title("🚀 Product Launch Intelligence Agent")
st.markdown("*AI-powered insights for GTM, Product Marketing & Growth Teams*")
st.divider()

# Company input section
st.subheader("🏢 Company Analysis")
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
            st.success(f"✓ Ready to analyze **{company_name}**")

# Create tabs for analysis types
analysis_tabs = st.tabs(["🔍 Competitor Analysis", "💬 Market Sentiment", "📈 Launch Metrics"])

# Competitor Analysis Tab
with analysis_tabs[0]:
    if company_name:
        analyze_btn = st.button(
            "🚀 Analyze Competitor Strategy",
            key="competitor_btn",
            type="primary",
            use_container_width=True
        )
        
        if analyze_btn:
            if not launch_analyst:
                st.error("⚠️ Please enter both API keys in the sidebar first.")
            else:
                with st.spinner("🔍 Launch Analyst gathering competitive intelligence..."):
                    try:
                        bullets = launch_analyst.run(
                            f"Generate up to 16 evidence-based insight bullets about {company_name}'s most recent product launches.\n"
                            f"Format requirements:\n"
                            f"• Start every bullet with exactly one tag: Positioning | Strength | Weakness | Learning\n"
                            f"• Follow the tag with a concise statement (max 30 words) referencing concrete observations: messaging, differentiation, pricing, channel selection, timing, engagement metrics, or customer feedback."
                        )
                        
                        long_text = expand_competitor_report(
                            bullets.content if hasattr(bullets, "content") else str(bullets),
                            company_name
                        )
                        st.session_state.competitor_response = long_text
                        st.success("✅ Competitor analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
    # Display results
    if st.session_state.competitor_response:
        st.markdown(st.session_state.competitor_response)

# Market Sentiment Tab
with analysis_tabs[1]:
    if company_name:
        analyze_btn = st.button(
            "💬 Analyze Market Sentiment",
            key="sentiment_btn",
            type="primary",
            use_container_width=True
        )
        
        if analyze_btn:
            if not sentiment_analyst:
                st.error("⚠️ Please enter both API keys in the sidebar first.")
            else:
                with st.spinner("💬 Sentiment Specialist analyzing market perception..."):
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
                        st.success("✅ Sentiment analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
    # Display results
    if st.session_state.sentiment_response:
        st.markdown(st.session_state.sentiment_response)

# Launch Metrics Tab
with analysis_tabs[2]:
    if company_name:
        analyze_btn = st.button(
            "📈 Analyze Launch Metrics",
            key="metrics_btn",
            type="primary",
            use_container_width=True
        )
        
        if analyze_btn:
            if not metrics_analyst:
                st.error("⚠️ Please enter both API keys in the sidebar first.")
            else:
                with st.spinner("📈 Metrics Specialist tracking launch performance..."):
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
                        st.success("✅ Metrics analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
    # Display results
    if st.session_state.metrics_response:
        st.markdown(st.session_state.metrics_response)

# Sidebar status
with st.sidebar.container():
    st.markdown("### 🤖 System Status")
    if openai_key and firecrawl_key:
        st.success("✅ All agents ready")
    else:
        st.error("❌ API keys required")

# Analysis status
if company_name:
    with st.sidebar.container():
        st.markdown("### 📊 Analysis Status")
        st.markdown(f"**Company:** {company_name}")
        
        status_items = [
            ("🔍", "Competitor Analysis", st.session_state.get('competitor_response')),
            ("💬", "Sentiment Analysis", st.session_state.get('sentiment_response')),
            ("📈", "Metrics Analysis", st.session_state.get('metrics_response'))
        ]
        
        for icon, name, status in status_items:
            if status:
                st.success(f"{icon} {name} ✓")
            else:
                st.info(f"{icon} {name} ⏳")
