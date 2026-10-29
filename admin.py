import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# Environment variables load karein
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page Configuration
st.set_page_config(page_title="Admin Supervisor Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Human Supervisor Escalation Dashboard")
st.caption("Review and approve AI Agent escalated customer support issues")

# Refresh Button
if st.button("🔄 Refresh Tickets"):
    st.rerun()

# Fetch all tickets from Supabase
try:
    response = supabase.table("tickets").select("*").order("created_at", desc=True).execute()
    tickets = response.data
    
    if not tickets:
        st.info("No escalation tickets found in database.")
    else:
        pending_tickets = [t for t in tickets if t.get("status") == "pending_approval"]
        resolved_tickets = [t for t in tickets if t.get("status") != "pending_approval"]

        st.subheader(f"📋 Pending Approvals ({len(pending_tickets)})")

        if not pending_tickets:
            st.success("🎉 No pending tickets! All customer issues are resolved.")
        else:
            for ticket in pending_tickets:
                with st.expander(f"⚠️ Ticket ID: {ticket['id']} | Order: {ticket['order_id']}", expanded=True):
                    st.write(f"**Customer Issue:** {ticket['customer_issue']}")
                    st.write(f"**Created At:** {ticket['created_at']}")
                    st.write(f"**Status:** `{ticket['status']}`")
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✅ Approve Resolution / Refund", key=f"app_{ticket['id']}", type="primary"):
                            supabase.table("tickets").update({"status": "Approved"}).eq("id", ticket["id"]).execute()
                            st.success(f"Ticket {ticket['id'][:8]} Approved successfully!")
                            st.rerun()
                    with col2:
                        if st.button("❌ Reject Issue", key=f"rej_{ticket['id']}"):
                            supabase.table("tickets").update({"status": "Rejected"}).eq("id", ticket["id"]).execute()
                            st.warning(f"Ticket {ticket['id'][:8]} Rejected!")
                            st.rerun()

        st.divider()
        st.subheader("📜 Resolution History")
        if resolved_tickets:
            st.dataframe(resolved_tickets, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching tickets: {str(e)}")