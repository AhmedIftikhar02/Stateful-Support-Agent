import os
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_core.tools import tool

# Environment variables load karein
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabase Client initialize karein
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@tool
def fetch_order_details(order_id: str) -> str:
    """Fetch details of a customer order using the Order ID (e.g. ORD-101)."""
    print(f"\n[TOOL EXECUTING] fetch_order_details called with order_id: {order_id}")
    try:
        response = supabase.table("orders").select("*").eq("id", order_id).execute()
        print(f"[TOOL SUCCESS] Supabase returned data: {response.data}")
        if response.data:
            order = response.data[0]
            return (
                f"Order ID: {order['id']}\n"
                f"Customer: {order['customer_name']}\n"
                f"Product: {order['product_name']}\n"
                f"Amount: ${order['amount']}\n"
                f"Status: {order['status']}\n"
                f"Delivery Date: {order['delivery_date']}"
            )
        else:
            return f"Order with ID '{order_id}' not found in database."
    except Exception as e:
        print(f"[TOOL ERROR] Supabase error: {str(e)}")
        return f"Error fetching order: {str(e)}"

@tool
def create_escalation_ticket(order_id: str, issue_description: str) -> str:
    """Create an escalation ticket for human agent approval when issues cannot be resolved automatically."""
    print(f"\n[TOOL EXECUTING] create_escalation_ticket for order: {order_id}")
    try:
        data = {
            "order_id": order_id,
            "customer_issue": issue_description,
            "status": "pending_approval"
        }
        response = supabase.table("tickets").insert(data).execute()
        print(f"[TOOL SUCCESS] Ticket inserted: {response.data}")
        if response.data:
            ticket_id = response.data[0]['id']
            return f"Escalation ticket created successfully. Ticket ID: {ticket_id}. A human supervisor will review it."
        else:
            return "Failed to create escalation ticket."
    except Exception as e:
        print(f"[TOOL ERROR] Supabase ticket error: {str(e)}")
        return f"Error creating ticket: {str(e)}"