import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

DB_PATH = "lcis.db"

st.set_page_config(page_title="LCIS Dashboard", layout="wide")
st.title("LCIS — Cost Intelligence Dashboard")

def get_conn():
    return sqlite3.connect(DB_PATH)

conn = get_conn()

clients_df = pd.read_sql("SELECT id, client_name, markup_percentage FROM clients", conn)
projects_df = pd.read_sql("SELECT id, client_id, project_name FROM projects", conn)
logs_df = pd.read_sql("SELECT * FROM request_logs", conn)
rules_df = pd.read_sql("SELECT * FROM budget_rules", conn)

if clients_df.empty:
    st.warning("No clients yet. Create some via the API first.")
    st.stop()

# --- Cost per client ---
st.header("Cost per Client")
cost_by_client = logs_df.groupby("client_id")["cost"].sum().reset_index()
cost_by_client = cost_by_client.merge(clients_df, left_on="client_id", right_on="id", how="left")
st.bar_chart(cost_by_client.set_index("client_name")["cost"])
st.dataframe(cost_by_client[["client_name", "cost"]], use_container_width=True)

# --- Cost per project ---
st.header("Cost per Project")
cost_by_project = logs_df.groupby("project_id")["cost"].sum().reset_index()
cost_by_project = cost_by_project.merge(projects_df, left_on="project_id", right_on="id", how="left")
st.dataframe(cost_by_project[["project_name", "cost"]], use_container_width=True)

# --- Cost per model ---
st.header("Cost per Model")
cost_by_model = logs_df.groupby(["provider", "model"])["cost"].sum().reset_index()
st.dataframe(cost_by_model, use_container_width=True)

# --- Budget status ---
st.header("Budget Status")
if rules_df.empty:
    st.info("No budget rules configured.")
else:
    rows = []
    for _, rule in rules_df.iterrows():
        if rule["scope_type"] == "client":
            spend = logs_df[logs_df["client_id"] == rule["scope_id"]]["cost"].sum()
        else:
            spend = logs_df[logs_df["project_id"] == rule["scope_id"]]["cost"].sum()
        breached = spend >= rule["budget_amount"]
        rows.append({
            "scope_type": rule["scope_type"],
            "scope_id": rule["scope_id"],
            "budget": rule["budget_amount"],
            "spend": round(spend, 4),
            "status": "🔴 BREACHED" if breached else "🟢 OK",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

# --- Invoice export ---
st.header("Export Client Invoice (CSV)")
client_names = clients_df.set_index("id")["client_name"].to_dict()
selected_client_id = st.selectbox("Client", options=list(client_names.keys()), format_func=lambda x: client_names[x])
date_range = st.date_input("Date range", value=(datetime.today().date(), datetime.today().date()))

if st.button("Generate Invoice"):
    markup = clients_df.loc[clients_df["id"] == selected_client_id, "markup_percentage"].values[0]
    client_logs = logs_df[logs_df["client_id"] == selected_client_id].copy()
    client_logs["timestamp"] = pd.to_datetime(client_logs["timestamp"])

    if len(date_range) == 2:
        start, end = date_range
        client_logs = client_logs[
            (client_logs["timestamp"].dt.date >= start) & (client_logs["timestamp"].dt.date <= end)
        ]

    if client_logs.empty:
        st.warning("No usage found for this client/date range.")
    else:
        client_logs["billed_amount"] = client_logs["cost"] * (1 + markup / 100)
        total_cost = client_logs["cost"].sum()
        total_billed = client_logs["billed_amount"].sum()

        st.write(f"**Total cost:** ${total_cost:.4f}  |  **Markup:** {markup}%  |  **Total billed:** ${total_billed:.4f}")
        st.dataframe(client_logs[["timestamp", "provider", "model", "tokens_used", "cost", "billed_amount"]])

        csv = client_logs[["timestamp", "provider", "model", "tokens_used", "cost", "billed_amount"]].to_csv(index=False)
        st.download_button("Download Invoice CSV", data=csv, file_name=f"invoice_client_{selected_client_id}.csv", mime="text/csv")

conn.close()