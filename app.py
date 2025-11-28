import streamlit as st

st.title("Single Merchant Revenue & Fees Calculator")

st.markdown("Compare **Dual Pricing** vs **Flat Rate** for a single merchant and instantly see earnings, monthly fees, and one-time costs.")

# ---- Core Inputs ----
st.header("Base Inputs")

# Default volume now 15,000 but still fully adjustable
volume = st.number_input("Monthly Processing Volume ($)", value=15000, step=500)
dual_profit_pct = st.number_input("Estimated Profit % (Dual Pricing)", value=1.5, step=0.1) / 100
flat_profit_pct = st.number_input("Estimated Profit % (Flat Rate)", value=1.0, step=0.1) / 100
revshare = st.number_input("Revshare to Solonist (%)", value=50.0, step=5.0) / 100

st.write("---")

# ---- Setup Options (Decision Tree) ----
st.header("Merchant Setup")

# Terminal choice
terminal = st.selectbox(
    "Which terminal are they using?",
    ["None", "Dejavoo P8", "Dejavoo P18", "Dejavoo P12 Mini"],
)

# Stand only if needed
needs_stand = False
if terminal == "Dejavoo P8":
    needs_stand = st.checkbox("Add stand for P8? ($35 one-time)", value=False)

# Number of terminals
num_terminals = st.number_input("Number of terminals", min_value=0, value=1 if terminal != "None" else 0, step=1)

# Mobile payments?
use_mobile = st.checkbox("Will they use mobile payments (iPhone/Android)?", value=False)
num_mobile_devices = 0
if use_mobile:
    num_mobile_devices = st.number_input("Number of mobile devices", min_value=1, value=1, step=1)

# Pricing model?
use_dual_pricing = st.checkbox("Is this merchant using Dual Pricing?", value=True)

st.write("---")

# ---- Fee Constants ----

# Monthly fees
ACCOUNT_ON_FILE = 7.50
GATEWAY = 10.00
PER_TERMINAL_FIRST = 4.00
PER_TERMINAL_SECOND = 2.00
MOBILE_MONTHLY = 10.00  # per mobile device

# One-time fees
P8_TERMINAL = 310.00
P18_TERMINAL = 446.50
P12_TERMINAL = 166.75
STAND_P8 = 35.00
MOBILE_APP_DOWNLOAD = 30.00  # per device
DUAL_COMPLIANCE = 3.00  # Dual Pricing only

# ---- Compute One-Time Fees ----
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

# ---- Compute Monthly Fees ----
monthly_fees = 0.0

if terminal != "None":
    monthly_fees += ACCOUNT_ON_FILE
    monthly_fees += GATEWAY

    if num_terminals >= 1:
        monthly_fees += PER_TERMINAL_FIRST
    if num_terminals >= 2:
        monthly_fees += PER_TERMINAL_SECOND

if use_mobile:
    monthly_fees += num_mobile_devices * MOBILE_MONTHLY

# ---- Profit Calculations ----
dual_gross_profit = volume * dual_profit_pct
flat_gross_profit = volume * flat_profit_pct

dual_solonist_share = dual_gross_profit * revshare
flat_solonist_share = flat_gross_profit * revshare

dual_net_first_month = dual_solonist_share - monthly_fees - one_time_fees
flat_net_first_month = flat_solonist_share - monthly_fees  # flat rate has no DP compliance fee

st.header("Results")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Dual Pricing (3.99%)")
    st.write(f"**Gross profit (processor):** ${dual_gross_profit:,.2f}")
    st.write(f"**Solonist share:** ${dual_solonist_share:,.2f}")
    st.write(f"**Monthly fees:** ${monthly_fees:,.2f}")
    st.write(f"**One-time fees:** ${one_time_fees:,.2f}")
    st.write(f"**Net first month (Solonist):** ${dual_net_first_month:,.2f}")

with col2:
    st.subheader("Flat Rate (2.95% + $0.30)")
    st.write(f"**Gross profit (processor):** ${flat_gross_profit:,.2f}")
    st.write(f"**Solonist share:** ${flat_solonist_share:,.2f}")
    st.write(f"**Monthly fees:** ${monthly_fees:,.2f}")
    st.write("**One-time fees:** $0.00 (no DP compliance on flat rate)")
    st.write(f"**Net first month (Solonist):** ${flat_net_first_month:,.2f}")

st.write("---")
st.caption("Adjust the inputs above to calculate fees and earnings for any merchant setup.")
