import streamlit as st

st.title("Single Merchant Revenue & Fees Calculator")

st.markdown(
    "Compare **Dual Pricing** vs **Flat Rate** for a single merchant and "
    "instantly see agent earnings, monthly fees, and one-time setup costs."
)

# ---- Core Inputs ----
st.header("Base Inputs")

# Default volume now 15,000 but still fully adjustable
volume = st.number_input("Monthly Processing Volume ($)", value=15000, step=500)

st.subheader("Pricing Models (fixed assumptions)")
st.markdown(
    "- **Dual Pricing:** 3.99% (assumes **1.5%** profit to the processor)\n"
    "- **Flat Rate:** 2.95% + $0.30 (assumes **1.0%** profit to the processor)"
)

# Fixed profit assumptions
dual_profit_pct = 0.015   # 1.5%
flat_profit_pct = 0.01    # 1.0%

# Fixed revshare
revshare = 0.50
st.markdown("**Revshare to Agent:** 50% (fixed)")

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
num_terminals = st.number_input("Number of terminals", min_value=0, value=0, step=1)

# Mobile payments?
use_mobile = st.checkbox("Will they use mobile payments (iPhone/Android)?", value=False)
num_mobile_devices = 0
if use_mobile:
    num_mobile_devices = st.number_input("Number of mobile devices", min_value=1, value=1, step=1)

# Pricing model flag (used only to add the DP compliance one-time fee)
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

# ---- Compute One-Time Fees (setup only, does NOT affect profit) ----
one_time_fees = 0.0

if terminal == "Dejavoo P8":
    one_time_fees += P8_TERMINAL
elif terminal == "Dejavoo P18":
    one_time_fees += P18_TERMINAL
elif terminal == "Dejavoo P12 Mini":
    one_time_fees += P12_TERMINAL

if needs_stand and terminal == "Dejavoo P8":
    one_time_fees += STAND_P8

if use_mobile:
    one_time_fees += num_mobile_devices * MOBILE_APP_DOWNLOAD

if use_dual_pricing:
    one_time_fees += DUAL_COMPLIANCE

# ---- Compute Monthly Fees (these DO reduce agent profit) ----
monthly_fees = 0.0

# Base monthly fees (assumed for an active merchant)
monthly_fees += ACCOUNT_ON_FILE
monthly_fees += GATEWAY

# Per-terminal monthly fees
if num_terminals >= 1:
    monthly_fees += PER_TERMINAL_FIRST
if num_terminals >= 2:
    monthly_fees += (num_terminals - 1) * PER_TERMINAL_ADDITIONAL

# Mobile monthly fee
if use_mobile:
    monthly_fees += num_mobile_devices * MOBILE_MONTHLY

# ---- Profit Calculations ----
dual_gross_profit = volume * dual_profit_pct
flat_gross_profit = volume * flat_profit_pct

dual_agent_share = dual_gross_profit * revshare
flat_agent_share = flat_gross_profit * revshare

# Net MONTHLY profit to agent (after monthly fees only)
dual_net_monthly = dual_agent_share - monthly_fees
flat_net_monthly = flat_agent_share - monthly_fees

st.header("Results")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Dual Pricing (3.99%)")
    st.write(f"**Gross profit (processor):** ${dual_gross_profit:,.2f}")
    st.write(f"**Agent share (50%):** ${dual_agent_share:,.2f}")
    st.write(f"**Monthly fees (total):** ${monthly_fees:,.2f}")
    st.write(f"**Net monthly to Agent (after monthly fees):** ${dual_net_monthly:,.2f}")
    st.write(f"**One-time setup fees (not deducted above):** ${one_time_fees:,.2f}")

with col2:
    st.subheader("Flat Rate (2.95% + $0.30)")
    st.write(f"**Gross profit (processor):** ${flat_gross_profit:,.2f}")
    st.write(f"**Agent share (50%):** ${flat_agent_share:,.2f}")
    st.write(f"**Monthly fees (total):** ${monthly_fees:,.2f}")
    st.write(f"**Net monthly to Agent (after monthly fees):** ${flat_net_monthly:,.2f}")
    st.write("**One-time setup fees:**")
    st.write(
        "- Same hardware/mobile setup fees as selected above.\n"
        "- No Dual Pricing compliance fee on flat rate."
    )

st.write("---")
st.caption("Adjust the volume and setup options above to model different merchant scenarios.")
