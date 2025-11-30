import streamlit as st

st.markdown(
    """
    <div style='text-align:center; margin-bottom: 0.2rem;'>
        <img src="logo.png" width="220">
    </div>
    """,
    unsafe_allow_html=True
)

# --- Basic styling to feel closer to pinpointpayments.com ---
st.markdown(
    """
    <style>
    .main {
        background-color: #ffffff;
    }
    .pp-card {
        background-color: #F5F6FA;
        padding: 1.5rem 1.8rem;
        border-radius: 14px;
        border: 1px solid #E1E4EB;
        margin-bottom: 1.5rem;
    }
    h1, h2, h3, h4 {
        color: #0F4C81;
        font-weight: 700;
    }
    .pp-subtitle {
        color: #4A4F5A;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Logo + title ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 0.2rem;">
        <img src="https://www.pinpointpayments.com/wp-content/uploads/2022/09/PinpointLogo-Color.png"
             alt="Pinpoint Payments" width="220">
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h2 style='text-align:center; margin-bottom:0.1rem;'>Single Merchant Revenue & Fees Calculator</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='pp-subtitle' style='text-align:center;'>Compare <strong>Dual Pricing</strong> vs "
    "<strong>Flat Rate</strong> for one merchant with clear monthly, yearly, and one-time economics.</p>",
    unsafe_allow_html=True,
)

# ---- Core Inputs ----
with st.container():
    st.markdown("<div class='pp-card'>", unsafe_allow_html=True)

    st.markdown("#### Monthly Volume")
    volume_input = st.text_input("Monthly Processing Volume ($)", value="15,000")

    def parse_dollar_input(text: str) -> float:
        text = text.replace(",", "").replace("$", "").strip()
        if text == "":
            return 0.0
        try:
            return float(text)
        except ValueError:
            return 0.0

    volume = parse_dollar_input(volume_input)

    # Fixed profit assumptions
    dual_profit_pct = 0.015   # 1.5% profit for Dual Pricing
    flat_profit_pct = 0.01    # 1.0% profit for Flat Rate
    revshare = 0.50           # 50% to agent

    st.markdown("</div>", unsafe_allow_html=True)

# ---- Merchant Setup ----
with st.container():
    st.markdown("<div class='pp-card'>", unsafe_allow_html=True)
    st.markdown("### Merchant Setup")

    col_setup_left, col_setup_right = st.columns(2)

    with col_setup_left:
        terminal = st.selectbox(
            "Terminal type",
            ["None", "Dejavoo P8", "Dejavoo P18", "Dejavoo P12 Mini"],
        )

        num_terminals = st.number_input(
            "Number of terminals", min_value=1, value=1, step=1
        )

        use_dual_pricing = st.checkbox(
            "This merchant is using Dual Pricing (3.99%)", value=True
        )

    with col_setup_right:
        needs_stand = False
        if terminal == "Dejavoo P8":
            needs_stand = st.checkbox("Add stand for P8? ($35 one-time)", value=False)

        use_mobile = st.checkbox(
            "Will they use mobile payments (iPhone/Android)?", value=False
        )
        num_mobile_devices = 0
        if use_mobile:
            num_mobile_devices = st.number_input(
                "Number of mobile devices", min_value=1, value=1, step=1
            )

    st.markdown("</div>", unsafe_allow_html=True)

# ---- Fee Constants ----
ACCOUNT_ON_FILE = 7.50
GATEWAY = 10.00
PER_TERMINAL_FIRST = 4.00
PER_TERMINAL_ADDITIONAL = 2.00
MOBILE_MONTHLY = 10.00

P8_TERMINAL = 310.00
P18_TERMINAL = 446.50
P12_TERMINAL = 166.75
STAND_P8 = 35.00
MOBILE_APP_DOWNLOAD = 30.00
DUAL_COMPLIANCE = 3.00

# ---- One-Time Fees (single merchant) ----
base_one_time_fees = 0.0

if terminal == "Dejavoo P8":
    base_one_time_fees += P8_TERMINAL
elif terminal == "Dejavoo P18":
    base_one_time_fees += P18_TERMINAL
elif terminal == "Dejavoo P12 Mini":
    base_one_time_fees += P12_TERMINAL

if needs_stand and terminal == "Dejavoo P8":
    base_one_time_fees += STAND_P8

if use_mobile:
    base_one_time_fees += num_mobile_devices * MOBILE_APP_DOWNLOAD

dual_one_time_fees = base_one_time_fees + (DUAL_COMPLIANCE if use_dual_pricing else 0.0)
flat_one_time_fees = base_one_time_fees

# ---- Monthly Fees (single merchant) ----
monthly_fees_total = 0.0
monthly_fees_agent = 0.0

monthly_fees_total += ACCOUNT_ON_FILE + GATEWAY
monthly_fees_agent += ACCOUNT_ON_FILE + GATEWAY

monthly_fees_total += PER_TERMINAL_FIRST
monthly_fees_agent += PER_TERMINAL_FIRST

if num_terminals >= 2:
    additional_terminals = num_terminals - 1
    addl_fee = additional_terminals * PER_TERMINAL_ADDITIONAL
    monthly_fees_total += addl_fee
    monthly_fees_agent += addl_fee

if use_mobile:
    mobile_monthly_fee = num_mobile_devices * MOBILE_MONTHLY
    monthly_fees_total += mobile_monthly_fee
    monthly_fees_agent += mobile_monthly_fee

# ---- Profit Calculations (single merchant) ----
dual_gross_profit = volume * dual_profit_pct
flat_gross_profit = volume * flat_profit_pct

dual_agent_share = dual_gross_profit * revshare
flat_agent_share = flat_gross_profit * revshare

dual_net_monthly_absorb = dual_agent_share - monthly_fees_agent
flat_net_monthly_absorb = flat_agent_share - monthly_fees_agent

dual_yearly_passing = dual_agent_share * 12
dual_yearly_absorb = dual_net_monthly_absorb * 12

flat_yearly_passing = flat_agent_share * 12
flat_yearly_absorb = flat_net_monthly_absorb * 12

# ---- Results ----
with st.container():
    st.markdown("<div class='pp-card'>", unsafe_allow_html=True)
    st.markdown("### Results (Single Merchant)")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dual Pricing (3.99%)")
        st.write(f"**Gross profit (processor, monthly):** ${dual_gross_profit:,.2f}")
        st.write(f"**Agent share (50%, monthly):** ${dual_agent_share:,.2f}")
        st.write(f"**Monthly fees (total):** ${monthly_fees_total:,.2f}")
        st.write(
            f"**Net to agent (passing monthly fees, monthly):** "
            f"${dual_agent_share:,.2f}"
        )
        st.write(
            f"**Net to agent (absorbing monthly fees, monthly):** "
            f"${dual_net_monthly_absorb:,.2f}"
        )
        st.write(
            f"**Yearly net to agent (passing monthly fees):** "
            f"${dual_yearly_passing:,.2f}"
        )
        st.write(
            f"**Yearly net to agent (absorbing monthly fees):** "
            f"${dual_yearly_absorb:,.2f}"
        )
        st.write(f"**One-time setup fees:** ${dual_one_time_fees:,.2f}")

    with col2:
        st.subheader("Flat Rate (2.95% + $0.30)")
        st.write(f"**Gross profit (processor, monthly):** ${flat_gross_profit:,.2f}")
        st.write(f"**Agent share (50%, monthly):** ${flat_agent_share:,.2f}")
        st.write(f"**Monthly fees (total):** ${monthly_fees_total:,.2f}")
        st.write(
            f"**Net to agent (passing monthly fees, monthly):** "
            f"${flat_agent_share:,.2f}"
        )
        st.write(
            f"**Net to agent (absorbing monthly fees, monthly):** "
            f"${flat_net_monthly_absorb:,.2f}"
        )
        st.write(
            f"**Yearly net to agent (passing monthly fees):** "
            f"${flat_yearly_passing:,.2f}"
        )
        st.write(
            f"**Yearly net to agent (absorbing monthly fees):** "
            f"${flat_yearly_absorb:,.2f}"
        )
        st.write(f"**One-time setup fees:** ${flat_one_time_fees:,.2f}")

    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")
st.markdown(
    "_These are only estimates. BIN mix and method of processing "
    "(Card Not Present, Swipe, MOTO) can all change the exact profit for any merchant._"
)
