import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="NSE Market Explorer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for distinctive design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Playfair+Display:wght@700;900&display=swap');
    
    /* Global Styling */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        color: #e8eaed;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #00d4ff !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(135deg, #00d4ff 0%, #00ff88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2rem !important;
        color: #00ff88 !important;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #8b92a8 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.7rem !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1420 0%, #1a1f3a 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #00d4ff !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: rgba(26, 31, 58, 0.6) !important;
        color: #e8eaed !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stDateInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0088ff 100%) !important;
        color: #0a0e27 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.5);
    }
    
    /* Data Tables */
    .dataframe {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: rgba(26, 31, 58, 0.4) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: rgba(0, 255, 136, 0.1) !important;
        border-left: 4px solid #00ff88 !important;
        color: #00ff88 !important;
    }
    
    .stError {
        background-color: rgba(255, 82, 82, 0.1) !important;
        border-left: 4px solid #ff5252 !important;
        color: #ff5252 !important;
    }
    
    /* Info Boxes */
    .stInfo {
        background-color: rgba(0, 212, 255, 0.1) !important;
        border-left: 4px solid #00d4ff !important;
        color: #00d4ff !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(0, 212, 255, 0.2) !important;
        margin: 2rem 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(26, 31, 58, 0.4) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #00d4ff !important;
    }
    
    /* Custom accent elements */
    .accent-line {
        height: 3px;
        background: linear-gradient(90deg, #00d4ff 0%, #00ff88 100%);
        border-radius: 2px;
        margin: 1rem 0;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
BASE_URL = "https://dmtdmptukjopiheowbgg.supabase.co/functions/v1/api-gateway"

def get_api_key():
    """Retrieve API key from Streamlit secrets"""
    try:
        return st.secrets["api"]["key"]
    except Exception as e:
        st.error(f"❌ API key not found in secrets. Please configure it in .streamlit/secrets.toml")
        st.stop()

def fetch_ohlcv_data(symbol, from_date=None, to_date=None, limit=500):
    """Fetch OHLCV data from the API"""
    api_key = get_api_key()
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    params = {
        "symbol": symbol.upper()
    }
    
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if limit:
        params["limit"] = limit
    
    try:
        response = requests.get(
            f"{BASE_URL}/ohlcv",
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

def create_candlestick_chart(df):
    """Create an interactive candlestick chart with Plotly"""
    fig = go.Figure(data=[go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff5252',
        increasing_fillcolor='rgba(0, 255, 136, 0.3)',
        decreasing_fillcolor='rgba(255, 82, 82, 0.3)'
    )])
    
    fig.update_layout(
        title={
            'text': 'Price Movement',
            'font': {'family': 'Playfair Display', 'size': 24, 'color': '#00d4ff'}
        },
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        template='plotly_dark',
        plot_bgcolor='rgba(26, 31, 58, 0.4)',
        paper_bgcolor='rgba(10, 14, 39, 0.6)',
        font={'family': 'JetBrains Mono', 'color': '#e8eaed'},
        xaxis=dict(
            gridcolor='rgba(0, 212, 255, 0.1)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='rgba(0, 212, 255, 0.1)',
            showgrid=True
        ),
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_volume_chart(df):
    """Create a volume bar chart"""
    colors = ['#00ff88' if row['close'] >= row['open'] else '#ff5252' 
              for idx, row in df.iterrows()]
    
    fig = go.Figure(data=[go.Bar(
        x=df['date'],
        y=df['volume'],
        marker_color=colors,
        name='Volume',
        opacity=0.7
    )])
    
    fig.update_layout(
        title={
            'text': 'Trading Volume',
            'font': {'family': 'Playfair Display', 'size': 24, 'color': '#00d4ff'}
        },
        xaxis_title='Date',
        yaxis_title='Volume',
        template='plotly_dark',
        plot_bgcolor='rgba(26, 31, 58, 0.4)',
        paper_bgcolor='rgba(10, 14, 39, 0.6)',
        font={'family': 'JetBrains Mono', 'color': '#e8eaed'},
        xaxis=dict(
            gridcolor='rgba(0, 212, 255, 0.1)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='rgba(0, 212, 255, 0.1)',
            showgrid=True
        ),
        height=300,
        hovermode='x unified'
    )
    
    return fig

def calculate_metrics(df):
    """Calculate key market metrics"""
    if df.empty:
        return None
    
    latest = df.iloc[-1]
    first = df.iloc[0]
    
    change = latest['close'] - first['close']
    change_pct = (change / first['close']) * 100
    
    metrics = {
        'current_price': latest['close'],
        'change': change,
        'change_pct': change_pct,
        'high': df['high'].max(),
        'low': df['low'].min(),
        'avg_volume': df['volume'].mean(),
        'total_volume': df['volume'].sum()
    }
    
    return metrics

# Main App
def main():
    # Header
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.title("📈 NSE Market Explorer")
    st.markdown("*Real-time OHLCV data visualization and analysis*")
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Query Parameters")
        
        # Symbol input
        symbol = st.text_input(
            "Stock Symbol",
            value="RELIANCE",
            help="Enter NSE stock symbol (e.g., RELIANCE, TCS, INFY)"
        ).upper()
        
        st.markdown("---")
        
        # Date range
        st.subheader("📅 Date Range")
        use_date_range = st.checkbox("Specify date range", value=False)
        
        from_date = None
        to_date = None
        
        if use_date_range:
            col1, col2 = st.columns(2)
            with col1:
                from_date = st.date_input(
                    "From",
                    value=datetime.now() - timedelta(days=90),
                    max_value=datetime.now()
                )
            with col2:
                to_date = st.date_input(
                    "To",
                    value=datetime.now(),
                    max_value=datetime.now()
                )
            
            from_date = from_date.strftime("%Y-%m-%d")
            to_date = to_date.strftime("%Y-%m-%d")
        
        st.markdown("---")
        
        # Limit
        limit = st.number_input(
            "Record Limit",
            min_value=1,
            max_value=1000,
            value=500,
            step=50,
            help="Maximum number of records to fetch (max: 1000)"
        )
        
        st.markdown("---")
        
        # Fetch button
        fetch_button = st.button("🚀 Fetch Data", use_container_width=True)
        
        st.markdown("---")
        
        # API Info
        with st.expander("ℹ️ API Information"):
            st.markdown(f"""
            **Base URL:**  
            `{BASE_URL}`
            
            **Endpoint:**  
            `/ohlcv`
            
            **Authentication:**  
            API Key from Streamlit Secrets
            """)
    
    # Main content
    if fetch_button:
        with st.spinner(f"🔍 Fetching data for {symbol}..."):
            result = fetch_ohlcv_data(symbol, from_date, to_date, limit)
        
        if result and result.get('success'):
            data = result.get('data', [])
            
            if not data:
                st.warning(f"⚠️ No data found for symbol: {symbol}")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate metrics
            metrics = calculate_metrics(df)
            
            if metrics:
                # Display metrics
                st.subheader(f"📊 {symbol} Market Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    delta_color = "normal" if metrics['change'] >= 0 else "inverse"
                    st.metric(
                        "Current Price",
                        f"₹{metrics['current_price']:,.2f}",
                        f"{metrics['change']:+,.2f} ({metrics['change_pct']:+.2f}%)",
                        delta_color=delta_color
                    )
                
                with col2:
                    st.metric(
                        "Period High",
                        f"₹{metrics['high']:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        "Period Low",
                        f"₹{metrics['low']:,.2f}"
                    )
                
                with col4:
                    st.metric(
                        "Avg Volume",
                        f"{metrics['avg_volume']:,.0f}"
                    )
                
                st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
                
                # Charts
                tab1, tab2, tab3 = st.tabs(["📈 Candlestick Chart", "📊 Volume Analysis", "📋 Raw Data"])
                
                with tab1:
                    candlestick_fig = create_candlestick_chart(df)
                    st.plotly_chart(candlestick_fig, use_container_width=True)
                
                with tab2:
                    volume_fig = create_volume_chart(df)
                    st.plotly_chart(volume_fig, use_container_width=True)
                    
                    # Additional volume metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Volume", f"{metrics['total_volume']:,.0f}")
                    with col2:
                        st.metric("Avg Daily Volume", f"{metrics['avg_volume']:,.0f}")
                
                with tab3:
                    st.dataframe(
                        df.style.format({
                            'open': '₹{:.2f}',
                            'high': '₹{:.2f}',
                            'low': '₹{:.2f}',
                            'close': '₹{:.2f}',
                            'volume': '{:,.0f}'
                        }),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"{symbol}_ohlcv_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                st.success(f"✅ Successfully loaded {len(df)} records for {symbol}")
        
        elif result:
            st.error(f"❌ API Error: {result.get('error', 'Unknown error')}")
        else:
            st.error("❌ Failed to fetch data. Please check your API configuration.")
    
    else:
        # Welcome screen
        st.info("👈 Configure your query parameters in the sidebar and click **Fetch Data** to begin")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Features
            - **Real-time OHLCV Data** from NSE
            - **Interactive Charts** with Plotly
            - **Candlestick Visualization**
            - **Volume Analysis**
            - **Downloadable Data** in CSV format
            - **Customizable Date Ranges**
            """)
        
        with col2:
            st.markdown("""
            ### 📚 Popular Symbols
            - **RELIANCE** - Reliance Industries
            - **TCS** - Tata Consultancy Services
            - **INFY** - Infosys
            - **HDFCBANK** - HDFC Bank
            - **ICICIBANK** - ICICI Bank
            - **SBIN** - State Bank of India
            """)

if __name__ == "__main__":
    main()
