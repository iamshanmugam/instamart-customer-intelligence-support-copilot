"""Streamlit UI for Instamart Support Co-Pilot."""

import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Instamart Co-Pilot", layout="wide")
st.title("Instamart Customer Intelligence & Support Co-Pilot")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Dashboard", "Segments", "Ticket Triage", "Assistant", "Refund Sim"]
)

seg_path = ROOT / "outputs" / "segmentation" / "customer_segments.csv"
eda_path = ROOT / "outputs" / "eda" / "eda_summary.csv"

with tab1:
    st.subheader("Dashboard")
    if eda_path.exists():
        st.dataframe(pd.read_csv(eda_path, header=None, names=["metric", "value"]))
    else:
        st.info("Run `python run_project.py` to generate outputs.")
    if (ROOT / "outputs" / "eda").exists():
        for img in sorted((ROOT / "outputs" / "eda").glob("*.png"))[:3]:
            st.image(str(img), caption=img.name)

with tab2:
    st.subheader("Customer segments")
    if seg_path.exists():
        st.dataframe(pd.read_csv(seg_path).head(100))
        ret = ROOT / "outputs" / "segmentation" / "retention_list.csv"
        if ret.exists():
            st.subheader("Retention list")
            st.dataframe(pd.read_csv(ret).head(50))
    else:
        st.warning("Segments not found.")

with tab3:
    st.subheader("Classify ticket")
    text = st.text_area("Ticket text")
    strategy = st.selectbox("Strategy", ["zero_shot", "few_shot"])
    if st.button("Classify"):
        try:
            r = requests.post(
                f"{API_BASE}/tickets/classify",
                json={"text": text, "strategy": strategy},
                timeout=30,
            )
            st.json(r.json())
        except Exception as e:
            from src.ticket_triage import classify_ticket

            st.json(classify_ticket(text, strategy=strategy))

with tab4:
    q = st.text_input("Ask about policy")
    if st.button("Ask"):
        try:
            r = requests.post(f"{API_BASE}/assistant/ask", json={"question": q}, timeout=30)
            st.write(r.json().get("answer", r.json()))
        except Exception:
            st.error("Start API: uvicorn api.main:app --reload")

with tab5:
    oid = st.text_input("Order ID", value="ORD000001")
    reason = st.text_area("Reason", value="Refund for damaged item")
    if st.button("Simulate refund"):
        try:
            r = requests.post(
                f"{API_BASE}/refund/request",
                json={"order_id": oid, "reason": reason},
                timeout=30,
            )
            st.json(r.json())
        except Exception:
            st.error("Start API or run pipeline first.")
