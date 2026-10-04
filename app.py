
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Restaurant Pricing Decision Engine",
    page_icon="₹",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    recommendations = pd.read_csv("final_recommendations.csv")
    scenarios = pd.read_csv("prototype_scenarios.csv")
    return recommendations, scenarios

recommendations, scenarios = load_data()

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("Restaurant Pricing Decision Engine")

st.markdown(
    "Explore price alternatives by store and product, "
    "forecast demand, and identify the price with the highest "
    "expected contribution within commercial guardrails."
)

st.divider()

# --------------------------------------------------
# SIDEBAR — INPUTS
# --------------------------------------------------

st.sidebar.header("Pricing Inputs")

stores = sorted(
    recommendations["Store_ID"].dropna().astype(str).unique().tolist()
)

selected_store = st.sidebar.selectbox(
    "Select Store",
    stores
)

products = sorted(
    recommendations.loc[
        recommendations["Store_ID"].astype(str) == selected_store,
        "Product_ID"
    ].dropna().astype(str).unique().tolist()
)

selected_product = st.sidebar.selectbox(
    "Select Product",
    products
)

# --------------------------------------------------
# SELECT RECOMMENDATION
# --------------------------------------------------

selected_rows = recommendations[
    (recommendations["Store_ID"].astype(str) == selected_store) &
    (recommendations["Product_ID"].astype(str) == selected_product)
]

if selected_rows.empty:
    st.error("No recommendation is available for this Store × Product combination.")
    st.stop()

rec = selected_rows.iloc[0]

scenario = scenarios[
    (scenarios["Store_ID"].astype(str) == selected_store) &
    (scenarios["Product_ID"].astype(str) == selected_product)
].copy()

if scenario.empty:
    st.error("No pricing scenarios are available for this Store × Product combination.")
    st.stop()

# --------------------------------------------------
# SAFE NUMERIC VALUES
# --------------------------------------------------

current_price = float(rec["Base_List_Price"])
recommended_price = float(rec["Candidate_Price"])
expected_orders = float(rec["Expected_Orders"])
contribution_uplift = float(rec["Contribution_Change_Pct"])
volume_change = float(rec["Volume_Change_Pct"])
competitor_premium = float(rec["Competitor_Premium_Pct"])
elasticity = float(rec["Elasticity"])
variable_cost = float(rec["Variable_Cost"])

pricing_direction = str(rec["Pricing_Direction"])
decision = str(rec["Decision"])
evidence_strength = str(rec["Evidence_Strength"])

# --------------------------------------------------
# DISPLAY PRODUCT / STORE INFORMATION
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Current List Price",
        f"₹{current_price:,.0f}"
    )

with col2:
    st.metric(
        "Recommended Price",
        f"₹{recommended_price:,.2f}"
    )

with col3:
    st.metric(
        "Pricing Action",
        pricing_direction
    )

# --------------------------------------------------
# RECOMMENDATION SUMMARY
# --------------------------------------------------

st.subheader("Business Recommendation")

if decision == "RECOMMEND":
    st.success(
        f"RECOMMEND — {pricing_direction} price to "
        f"₹{recommended_price:,.2f}"
    )

elif decision == "PILOT":
    st.warning(
        f"PILOT — test {pricing_direction.lower()} "
        f"price to ₹{recommended_price:,.2f} before rollout"
    )

else:
    st.info(
        f"HOLD — retain price at approximately "
        f"₹{recommended_price:,.2f}"
    )

# --------------------------------------------------
# KEY BUSINESS METRICS
# --------------------------------------------------

st.subheader("Expected Business Impact")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Expected Orders",
        f"{expected_orders:,.1f}"
    )

with m2:
    st.metric(
        "Contribution Uplift",
        f"{contribution_uplift:.1%}"
    )

with m3:
    st.metric(
        "Volume Impact",
        f"{volume_change:.1%}"
    )

with m4:
    st.metric(
        "Competitor Premium",
        f"{competitor_premium:.1%}"
    )

# --------------------------------------------------
# MODEL INFORMATION
# --------------------------------------------------

st.subheader("Model Evidence")

e1, e2, e3 = st.columns(3)

with e1:
    st.metric(
        "Estimated Elasticity",
        f"{elasticity:.2f}"
    )

with e2:
    st.metric(
        "Evidence Strength",
        evidence_strength
    )

with e3:
    st.metric(
        "Variable Cost",
        f"₹{variable_cost:,.0f}"
    )

# --------------------------------------------------
# SCENARIO TABLE
# --------------------------------------------------

st.subheader("Price Scenario Analysis")

display_df = scenario[
    [
        "Candidate_Price",
        "Expected_Orders",
        "Revenue",
        "Contribution",
        "Contribution_Change_Pct",
        "Volume_Change_Pct",
        "Competitor_Premium_Pct",
        "Feasible"
    ]
].copy()

display_df.columns = [
    "Price",
    "Expected Orders",
    "Revenue",
    "Contribution",
    "Contribution Change",
    "Volume Change",
    "Competitor Premium",
    "Feasible"
]

display_df["Price"] = display_df["Price"].map(
    lambda x: f"₹{float(x):,.2f}"
)

display_df["Expected Orders"] = display_df["Expected Orders"].map(
    lambda x: f"{float(x):,.1f}"
)

display_df["Revenue"] = display_df["Revenue"].map(
    lambda x: f"₹{float(x):,.0f}"
)

display_df["Contribution"] = display_df["Contribution"].map(
    lambda x: f"₹{float(x):,.0f}"
)

display_df["Contribution Change"] = display_df["Contribution Change"].map(
    lambda x: f"{float(x):.1%}"
)

display_df["Volume Change"] = display_df["Volume Change"].map(
    lambda x: f"{float(x):.1%}"
)

display_df["Competitor Premium"] = display_df["Competitor Premium"].map(
    lambda x: f"{float(x):.1%}"
)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True
)

# --------------------------------------------------
# CONTRIBUTION CHART
# --------------------------------------------------

st.subheader("Price vs Expected Contribution")

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(
    scenario["Candidate_Price"].astype(float),
    scenario["Contribution"].astype(float),
    marker="o"
)

recommended_row = scenario[
    np.isclose(
        scenario["Candidate_Price"].astype(float),
        recommended_price
    )
]

if not recommended_row.empty:
    ax.scatter(
        recommended_row["Candidate_Price"].astype(float),
        recommended_row["Contribution"].astype(float),
        s=100
    )

ax.set_xlabel("Candidate Price (₹)")
ax.set_ylabel("Expected Contribution (₹)")
ax.set_title(
    f"{selected_store} / {selected_product}"
)

ax.grid(True, alpha=0.25)

st.pyplot(fig)

plt.close(fig)

# --------------------------------------------------
# DECISION LOGIC
# --------------------------------------------------

st.subheader("Why This Recommendation?")

reason_items = []

if contribution_uplift > 0:
    reason_items.append(
        f"Expected contribution improves by "
        f"{contribution_uplift:.1%}."
    )

if volume_change < 0:
    reason_items.append(
        f"Expected order volume changes by "
        f"{volume_change:.1%}, within the 10% decline guardrail."
    )
else:
    reason_items.append(
        f"Expected order volume increases by "
        f"{volume_change:.1%}."
    )

if competitor_premium <= 0:
    reason_items.append(
        "The proposed price remains below the estimated competitor average."
    )
else:
    reason_items.append(
        f"The proposed price is "
        f"{competitor_premium:.1%} above the estimated competitor average."
    )

for item in reason_items:
    st.markdown(f"- {item}")

# --------------------------------------------------
# GUARDRAILS
# --------------------------------------------------

st.subheader("Commercial Guardrails")

g1, g2, g3 = st.columns(3)

with g1:
    if volume_change >= -0.10:
        st.success("✓ Volume guardrail passed")
    else:
        st.error("✗ Volume guardrail failed")

with g2:
    food_cost_pct = variable_cost / recommended_price

    if food_cost_pct <= 0.35:
        st.success("✓ Food-cost guardrail passed")
    else:
        st.error("✗ Food-cost guardrail failed")

with g3:
    if competitor_premium <= 0.05:
        st.success("✓ Competition guardrail passed")
    else:
        st.error("✗ Competition guardrail failed")

# --------------------------------------------------
# LIMITATION
# --------------------------------------------------

st.divider()

st.caption(
    "Prototype limitation: elasticity estimates are based on "
    "synthetic historical data. Recommended price changes should "
    "be validated through a controlled pilot before full rollout."
)
