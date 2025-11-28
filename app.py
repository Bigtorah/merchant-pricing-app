import streamlit as st

st.title("Single Merchant Revenue & Fees Calculator")

st.markdown("Compare **Dual Pricing** vs **Flat Rate**")

# ---- Core Inputs ----

# Monthly volume as text so commas are allowed, e.g. "15,000"
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

# Fixed profit assumptions (not shown, just used)
dual_profit_pct = 0.015   # 1.5% profit for Dual Pricing
flat_profit_pct = 0.01    # 1.0% profit for Flat Rate

# Fixed revshare to agent
revshare = 0.50  # 50% to agent

st.write("---")

# ---- Setup Options (Decision Tree) ----
st.header("Merchant Setup")

# Terminal choice (for one-time hardware cost only)
terminal = st.selectbox(
    "Which terminal are they using?",
    ["None", "Dejavoo P8", "Dejavoo P18", "Dejavoo P12 Mini"],
)

# Stand only if needed (only relevant for P8)
needs_stand = False
if terminal == "Dejavoo P8":
    needs_stand = st.checkbox("Add stand for P8? ($35 one-time)", value=False)

# Number of terminals (affects monthly per-terminal fees)
# Assume at least 1 terminal on a live account
num_terminals = st.number_input("Number of terminals", min_value=1, value=1, step=1)

# Mobile payments?
use_mobile = st.checkbox("Will they use mobile payments (iPhone/Android)?", value=False)
num_mobile_devices = 0
if use_mobile:
    num_mobile_devices = st.number_input("Number of mobile devices", min_value=1, value=1, step=1)

# Pricing model flag (used to decide if this is a Dual Pricing merchant)
use_dual_pricing = st.checkbox("This merchant is using Dual Pricing", value=True)

st.write("---")

# ---- Fee Constants ----

# Monthly fees (base + per usage)
ACCOUNT_ON_FILE = 7.50
GATEWAY = 10.00
PER_TERMINAL_FIRST = 4.00
PER_TERMINAL_ADDITIONAL = 2.00   # 2nd and beyond
MOBILE_MONTHLY = 10.00           # per mobile device

# One-time fees
P8_TERMINAL = 310.00
P18_TERMINAL = 446.50
P12_TERMINAL = 166.75
STAND_P8 = 35.00
MOBILE_APP_DOWNLOAD = 30.00      # per mobile device
DUAL_COMPLIANCE = 3.00           # Dual Pricing only, per merchant

# ---- Compute Base One-Time Fees (setup only, does NOT affect profit) ----
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

# Dual vs Flat one-time:
dual_one_time_fees = base_one_time_fees + (DUAL_COMPLIANCE if use_dual_pricing else 0.0)
flat_one_time_fees = base_one_time_fees  # no compliance fee on flat rate

# ---- Compute Monthly Fees ----
# - monthly_fees_total: what you show as the monthly cost
# - monthly_fees_agent: what actually reduces the agent's profit when "absorbing"
monthly_fees_total = 0.0
monthly_fees_agent = 0.0

# Base monthly fees (always present on an active account)
monthly_fees_total += ACCOUNT_ON_FILE + GATEWAY
monthly_fees_agent += ACCOUNT_ON_FILE + GATEWAY

# Per-terminal monthly fees
# First terminal
monthly_fees_total += PER_TERMINAL_FIRST
monthly_fees_agent += PER_TERMINAL_FIRST

# Additional terminals (2nd and beyond)
if num_terminals >= 2:
    additional_terminals = num_terminals - 1
    addl_fee = additional_terminals * PER_TERMINAL_ADDITIONAL
    monthly_fees_total += addl_fee
    monthly_fees_agent += addl_fee

# Mobile monthly fee:
# Added to BOTH total and agent-responsible fees,
# so absorbing monthly fees will decrease net when mobile is used.
if use_mobile:
    mobile_monthly_fee = num_mobile_devices * MOBILE_MONTHLY
    monthly_fees_total += mobile_monthly_fee
    monthly_fees_agent += mobile_monthly_fee

# ---- Profit Calculations ----
dual_gross_profit = volume * dual_profit_pct
flat_gross_profit = volume * flat_profit_pct

dual_agent_share = dual_gross_profit * revshare
flat_agent_share = flat_gross_profit * revshare

# Net MONTHLY profit to agent when absorbing all monthly fees
dual_net_monthly_absorb = dual_agent_share - monthly_fees_agent
flat_net_monthly_absorb = flat_agent_share - monthly_fees_agent

st.header("Results")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Dual Pricing (3.99%)")
    st.write(f"**Gross profit (processor):** ${dual_gross_profit:,.2f}")
    st.write(f"**Agent share (50%):** ${dual_agent_share:,.2f}")
    st.write(f"**Monthly fees (total):** ${monthly_fees_total:,.2f}")
    st.write(f"**Net to agent (passing monthly fees to merchant):** ${dual_agent_share:,.2f}")
    st.write(f"**Net to agent (absorbing monthly fees):** ${dual_net_monthly_absorb:,.2f}")
    st.write(f"**One-time setup fees:** ${dual_one_time_fees:,.2f}")

with col2:
    st.subheader("Flat Rate (2.95% + $0.30)")
    st.write(f"**Gross profit (processor):** ${flat_gross_profit:,.2f}")
    st.write(f"**Agent share (50%):** ${flat_agent_share:,.2f}")
    st.write(f"**Monthly fees (total):** ${monthly_fees_total:,.2f}")
    st.write(f"**Net to agent (passing monthly fees to merchant):** ${flat_agent_share:,.2f}")
    st.write(f"**Net to agent (absorbing monthly fees):** ${flat_net_monthly_absorb:,.2f}")
    st.write(f"**One-time setup fees:** ${flat_one_time_fees:,.2f}")

st.write("---")
st.caption("Adjust the volume and setup options above to model different merchant scenarios.")
