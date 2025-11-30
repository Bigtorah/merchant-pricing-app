import streamlit as st

# -----------------------------
#   PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Pinpoint – Merchant Revenue & Fees Calculator",
    page_icon="💳",
    layout="wide",
)

# -----------------------------
#   BASIC BRAND STYLING
# -----------------------------
st.markdown(
    """
    <style>
    .main { background-color: #ffffff; }

    h1, h2, h3, h4 {
        color: #0F4C81;  /* logo blue */
        font-weight: 700;
    }

    .pp-subtitle {
        color: #4A4F5A;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
#   LOGO + TITLE
# -----------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=220)

st.markdown(
    "<h2 style='text-align:center; margin-bottom:0.10rem;'>Single Merchant Revenue & Fees Calculator</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='pp-subtitle'>Compare <strong>Dual Pricing</strong> vs "
    "<strong>Flat Rate</strong> with clear monthly, yearly, and one-time economics.</p>",
    unsafe_allow_html=True,
)

# -----------------------------
#   MONTHLY VOLUME
# -----------------------------
st.markdown("### Monthly Volume")

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

# Profit assumptions (fixed)
dual_profit_pct = 0.015   # 1.5% profit for Dual Pricing
flat_profit_pct = 0.01    # 1.0% profit for Flat Rate
revshare = 0.50           # 50% to agent

st.write("---")

# -----------------------------
#   MERCHANT SETUP
# -----------------------------
st.markdown("### Merchant Setup")

colA, colB = st.columns(2)

with colA:
    terminal = st.selectbox(
        "Terminal type",
        ["None", "Dejavoo P8", "Dejavoo P18", "Dejavoo P12 Mini"],
    )

    num_terminals = st.number_input(
        "Number of terminals", min_value=1, value=1, step=1
    )

with colB:
    needs_stand = False
    if terminal == "Dejavoo P8":
        needs_stand = st.checkbox("Add Dejavoo P8 stand? ($35 one-time)", value=False)

    # Mobile device count (default 0)
    num_mobile_devices = st.number_input(
        "Number of mobile devices (optional)",
        min_value=0,
        value=0,
        step=1,
        help="10 per month per device + 30 one-time download per device.",
    )

st.write("---")

# -----------------------------
#   FEE CONSTANTS
# -----------------------------
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
DUAL_COMPLIANCE = 3.00  # one-time DP compliance fee (always applies to Dual Pricing)

# -----------------------------
#   ONE-TIME FEES (PER MERCHANT)
# -----------------------------
one_time_terminal = 0.0
if terminal == "Dejavoo P8":
    one_time_terminal = P8_TERMINAL
elif terminal == "Dejavoo P18":
    one_time_terminal = P18_TERMINAL
elif terminal == "Dejavoo P12 Mini":
    one_time_terminal = P12_TERMINAL

one_time_stand = STAND_P8 if (terminal == "Dejavoo P8" and needs_stand) else 0.0
one_time_mobile = num_mobile_devices * MOBILE_APP_DOWNLOAD

# Dual includes $3 compliance; Flat does not
dual_one_time_fees = one_time_terminal + one_time_stand + one_time_mobile + DUAL_COMPLIANCE
flat_one_time_fees = one_time_terminal + one_time_stand + one_time_mobile

# -----------------------------
#   MONTHLY FEES (PER MERCHANT)
# -----------------------------
monthly_account = ACCOUNT_ON_FILE
monthly_gateway = GATEWAY
monthly_first_terminal = PER_TERMINAL_FIRST
monthly_additional_terminals = max(num_terminals - 1, 0) * PER_TERMINAL_ADDITIONAL
monthly_mobile = num_mobile_devices * MOBILE_MONTHLY

monthly_fees_total = (
    monthly_account
    + monthly_gateway
    + monthly_first_terminal
    + monthly_additional_terminals
    + monthly_mobile
)

# All monthly fees are treated as "agent-responsible" in absorbing scenario
monthly_fees_agent = monthly_fees_total

# -----------------------------
#   PROFIT CALCULATIONS
# -----------------------------
dual_gross = volume * dual_profit_pct
flat_gross = volume * flat_profit_pct

dual_agent = dual_gross * revshare
flat_agent = flat_gross * revshare

dual_net_absorb = dual_agent - monthly_fees_agent
flat_net_absorb = flat_agent - monthly_fees_agent

dual_year_pass = dual_agent * 12
dual_year_absorb = dual_net_absorb * 12

flat_year_pass = flat_agent * 12
flat_year_absorb = flat_net_absorb * 12

# -----------------------------
#   RESULTS (SINGLE MERCHANT)
# -----------------------------
st.markdown("### Results (Single Merchant)")

colLeft, colRight = st.columns(2)

with colLeft:
    st.subheader("Dual Pricing (3.99%)")
    st.write(f"**Gross profit (processor, monthly):** ${dual_gross:,.2f}")
    st.write(f"**Agent share (50%, monthly):** ${dual_agent:,.2f}")

    with st.expander(
        f"Monthly fees (total): ${monthly_fees_total:,.2f}  — click to view breakdown"
    ):
        st.markdown(f"- Account on file (bank): ${monthly_account:,.2f}")
        st.markdown(f"- Dejavoo gateway: ${monthly_gateway:,.2f}")
        st.markdown(f"- Dejavoo first terminal: ${monthly_first_terminal:,.2f}")
        if monthly_additional_terminals > 0:
            st.markdown(
                f"- Dejavoo additional terminals: ${monthly_additional_terminals:,.2f}"
            )
        if monthly_mobile > 0:
            st.markdown(
                f"- Dejavoo mobile devices: ${monthly_mobile:,.2f}"
            )

    st.write(f"**Net to agent (passing monthly fees):** ${dual_agent:,.2f}")
    st.write(f"**Net to agent (absorbing monthly fees):** ${dual_net_absorb:,.2f}")
    st.write(f"**Yearly net (passing monthly fees):** ${dual_year_pass:,.2f}")
    st.write(f"**Yearly net (absorbing monthly fees):** ${dual_year_absorb:,.2f}")

    with st.expander(
        f"One-time setup fees: ${dual_one_time_fees:,.2f}  — click to view breakdown"
    ):
        if one_time_terminal > 0:
            st.markdown(
                f"- Dejavoo terminal hardware: ${one_time_terminal:,.2f}"
            )
        if one_time_stand > 0:
            st.markdown(
                f"- Dejavoo P8 stand (if selected): ${one_time_stand:,.2f}"
            )
        if one_time_mobile > 0:
            st.markdown(
                f"- Dejavoo mobile app download ({num_mobile_devices} device(s)): "
                f"${one_time_mobile:,.2f}"
            )
        st.markdown(
            f"- Dual Pricing compliance fee: ${DUAL_COMPLIANCE:,.2f}"
        )

with colRight:
    st.subheader("Flat Rate (2.95% + $0.30)")
    st.write(f"**Gross profit (processor, monthly):** ${flat_gross:,.2f}")
    st.write(f"**Agent share (50%, monthly):** ${flat_agent:,.2f}")

    with st.expander(
        f"Monthly fees (total): ${monthly_fees_total:,.2f}  — click to view breakdown"
    ):
        st.markdown(f"- Account on file (bank): ${monthly_account:,.2f}")
        st.markdown(f"- Dejavoo gateway: ${monthly_gateway:,.2f}")
        st.markdown(f"- Dejavoo first terminal: ${monthly_first_terminal:,.2f}")
        if monthly_additional_terminals > 0:
            st.markdown(
                f"- Dejavoo additional terminals: ${monthly_additional_terminals:,.2f}"
            )
        if monthly_mobile > 0:
            st.markdown(
                f"- Dejavoo mobile devices: ${monthly_mobile:,.2f}"
            )

    st.write(f"**Net to agent (passing monthly fees):** ${flat_agent:,.2f}")
    st.write(f"**Net to agent (absorbing monthly fees):** ${flat_net_absorb:,.2f}")
    st.write(f"**Yearly net (passing monthly fees):** ${flat_year_pass:,.2f}")
    st.write(f"**Yearly net (absorbing monthly fees):** ${flat_year_absorb:,.2f}")

    with st.expander(
        f"One-time setup fees: ${flat_one_time_fees:,.2f}  — click to view breakdown"
    ):
        if one_time_terminal > 0:
            st.markdown(
                f"- Dejavoo terminal hardware: ${one_time_terminal:,.2f}"
            )
        if one_time_stand > 0:
            st.markdown(
                f"- Dejavoo P8 stand (if selected): ${one_time_stand:,.2f}"
            )
        if one_time_mobile > 0:
            st.markdown(
                f"- Dejavoo mobile app download ({num_mobile_devices} device(s)): "
                f"${one_time_mobile:,.2f}"
            )
        st.markdown(
            "- Dual Pricing compliance fee: $0.00 (not charged on flat rate)"
        )

# -----------------------------
#   DISCLAIMER
# -----------------------------
st.write("---")
st.markdown(
    "_These are only estimates. BIN mix and method of processing "
    "(Card Not Present, Swipe, MOTO) can all change the exact profit for any merchant._"
)
