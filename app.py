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
st.header("Merchant Setup (Single Merchant)")

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

# ---- Compute Base One-Time Fees (per merchant, setup only, does NOT affect profit) ----
base_one_time_fees_per_merchant = 0.0

if terminal == "Dejavoo P8":
    base_one_time_fees_per_merchant += P8_TERMINAL
elif terminal == "Dejavoo P18":
    base_one_time_fees_per_merchant += P18_TERMINAL
elif terminal == "Dejavoo P12 Mini":
    base_one_time_fees_per_merchant += P12_TERMINAL

if needs_stand and terminal == "Dejavoo P8":
    base_one_time_fees_per_merchant += STAND_P8

if use_mobile:
    base_one_time_fees_per_merchant += num_mobile_devices * MOBILE_APP_DOWNLOAD

# Dual vs Flat one-time per merchant:
dual_one_time_fees_per_merchant = base_one_time_fees_per_merchant + (
    DUAL_COMPLIANCE if use_dual_pricing else 0.0
)
flat_one_time_fees_per_merchant = base_one_time_fees_per_merchant  # no compliance fee on flat rate

# ---- Compute Monthly Fees (per merchant) ----
# - monthly_fees_total_per_merchant: what you show as the monthly cost
# - monthly_fees_agent_per_merchant: what actually reduces the agent's profit when "absorbing"
monthly_fees_total_per_merchant = 0.0
monthly_fees_agent_per_merchant = 0.0

# Base monthly fees (always present on an active account)
monthly_fees_total_per_merchant += ACCOUNT_ON_FILE + GATEWAY
monthly_fees_agent_per_merchant += ACCOUNT_ON_FILE + GATEWAY

# Per-terminal monthly fees
# First terminal
monthly_fees_total_per_merchant += PER_TERMINAL_FIRST
monthly_fees_agent_per_merchant += PER_TERMINAL_FIRST

# Additional terminals (2nd and beyond)
if num_terminals >= 2:
    additional_terminals = num_terminals - 1
    addl_fee = additional_terminals * PER_TERMINAL_ADDITIONAL
    monthly_fees_total_per_merchant += addl_fee
    monthly_fees_agent_per_merchant += addl_fee

# Mobile monthly fee (per merchant)
if use_mobile:
    mobile_monthly_fee = num_mobile_devices * MOBILE_MONTHLY
    monthly_fees_total_per_merchant += mobile_monthly_fee
    monthly_fees_agent_per_merchant += mobile_monthly_fee

# ---- Profit Calculations (per merchant) ----
dual_gross_profit_per_merchant = volume * dual_profit_pct
flat_gross_profit_per_merchant = volume * flat_profit_pct

dual_agent_share_per_merchant = dual_gross_profit_per_merchant * revshare
flat_agent_share_per_merchant = flat_gross_profit_per_merchant * revshare

# Net MONTHLY profit to agent per merchant when absorbing all monthly fees
dual_net_monthly_absorb_per_merchant = (
    dual_agent_share_per_merchant - monthly_fees_agent_per_merchant
)
flat_net_monthly_absorb_per_merchant = (
    flat_agent_share_per_merchant - monthly_fees_agent_per_merchant
)

# Yearly (single merchant)
dual_yearly_passing_single = dual_agent_share_per_merchant * 12
dual_yearly_absorb_single = dual_net_monthly_absorb_per_merchant * 12

flat_yearly_passing_single = flat_agent_share_per_merchant * 12
flat_yearly_absorb_single = flat_net_monthly_absorb_per_merchant * 12

# ---- Results: Single Merchant ----
st.header("Results (Single Merchant)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Dual Pricing (3.99%)")
    st.write(f"**Gross profit (processor, monthly):** ${dual_gross_profit_per_merchant:,.2f}")
    st.write(f"**Agent share (50%, monthly):** ${dual_agent_share_per_merchant:,.2f}")
    st.write(f"**Monthly fees (total, single merchant):** ${monthly_fees_total_per_merchant:,.2f}")
    st.write(f"**Net to agent (passing monthly fees, monthly):** ${dual_agent_share_per_merchant:,.2f}")
    st.write(f"**Net to agent (absorbing monthly fees, monthly):** ${dual_net_monthly_absorb_per_merchant:,.2f}")
    st.write(f"**Yearly net to agent (passing monthly fees):** ${dual_yearly_passing_single:,.2f}")
    st.write(f"**Yearly net to agent (absorbing monthly fees):** ${dual_yearly_absorb_single:,.2f}")
    st.write(f"**One-time setup fees (single merchant):** ${dual_one_time_fees_per_merchant:,.2f}")

with col2:
    st.subheader("Flat Rate (2.95% + $0.30)")
    st.write(f"**Gross profit (processor, monthly):** ${flat_gross_profit_per_merchant:,.2f}")
    st.write(f"**Agent share (50%, monthly):** ${flat_agent_share_per_merchant:,.2f}")
    st.write(f"**Monthly fees (total, single merchant):** ${monthly_fees_total_per_merchant:,.2f}")
    st.write(f"**Net to agent (passing monthly fees, monthly):** ${flat_agent_share_per_merchant:,.2f}")
    st.write(f"**Net to agent (absorbing monthly fees, monthly):** ${flat_net_monthly_absorb_per_merchant:,.2f}")
    st.write(f"**Yearly net to agent (passing monthly fees):** ${flat_yearly_passing_single:,.2f}")
    st.write(f"**Yearly net to agent (absorbing monthly fees):** ${flat_yearly_absorb_single:,.2f}")
    st.write(f"**One-time setup fees (single merchant):** ${flat_one_time_fees_per_merchant:,.2f}")

# ---- Additional Merchant Profitability Report ----
st.write("")
st.write("")  # extra spacing

st.header("Additional Merchant Profitability Report")

num_merchants = st.number_input(
    "Number of merchants using this same setup", min_value=1, value=1, step=1
)

# Scale monthly and yearly numbers by number of merchants
dual_agent_share_all_merchants = dual_agent_share_per_merchant * num_merchants
flat_agent_share_all_merchants = flat_agent_share_per_merchant * num_merchants

dual_net_monthly_absorb_all_merchants = dual_net_monthly_absorb_per_merchant * num_merchants
flat_net_monthly_absorb_all_merchants = flat_net_monthly_absorb_per_merchant * num_merchants

dual_yearly_passing_all = dual_agent_share_all_merchants * 12
dual_yearly_absorb_all = dual_net_monthly_absorb_all_merchants * 12

flat_yearly_passing_all = flat_agent_share_all_merchants * 12
flat_yearly_absorb_all = flat_net_monthly_absorb_all_merchants * 12

dual_one_time_fees_total = dual_one_time_fees_per_merchant * num_merchants
flat_one_time_fees_total = flat_one_time_fees_per_merchant * num_merchants

col3, col4 = st.columns(2)

with col3:
    st.subheader("Dual Pricing – All Merchants")
    st.write(f"**Net to agent (passing monthly fees, monthly):** ${dual_agent_share_all_merchants:,.2f}")
    st.write(f"**Net to agent (absorbing monthly fees, monthly):** ${dual_net_monthly_absorb_all_merchants:,.2f}")
    st.write(f"**Yearly net to agent (passing monthly fees):** ${dual_yearly_passing_all:,.2f}")
    st.write(f"**Yearly net to agent (absorbing monthly fees):** ${dual_yearly_absorb_all:,.2f}")
    st.write(f"**Total one-time setup fees (all merchants):** ${dual_one_time_fees_total:,.2f}")

with col4:
    st.subheader("Flat Rate – All Merchants")
    st.write(f"**Net to agent (passing monthly fees, monthly):** ${flat_agent_share_all_merchants:,.2f}")
    st.write(f"**Net to agent (absorbing monthly fees, monthly):** ${flat_net_monthly_absorb_all_merchants:,.2f}")
    st.write(f"**Yearly net to agent (passing monthly fees):** ${flat_yearly_passing_all:,.2f}")
    st.write(f"**Yearly net to agent (absorbing monthly fees):** ${flat_yearly_absorb_all:,.2f}")
    st.write(f"**Total one-time setup fees (all merchants):** ${flat_one_time_fees_total:,.2f}")

st.write("---")
st.markdown(
    "_These are only estimates, BIN mix, method of processing i.e. Card Not Present, "
    "Swipe, MOTO can all change the exact profit for any merchant._"
)
