# streamlit_app.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from queries import QUERIES  # Import the dictionary from your queries.py file

DB_PATH = "food_wastage.db"


# --- 1. DATABASE SETUP & UTILITIES ---

@st.cache_resource
def get_db_connection():
    """Establishes a persistent connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def execute_query(conn, query, params=()):
    """Executes a query (INSERT, UPDATE, DELETE) and handles commits."""
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False


def fetch_data(conn, query, params=()):
    """Fetches data (SELECT) and returns a DataFrame."""
    return pd.read_sql_query(query, conn, params=params)


# --- 2. UI TABS ---

st.set_page_config(page_title="Food Donation Platform", layout="wide")
st.title("🍏 Food Wastage & Donation Management Platform")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard & Filtering", "📈 Analysis", "🗃️ Manage Data (CRUD)", "📞 Contact Directory"])

# --- 3. TAB 1: DASHBOARD & FILTERING ---

with tab1:
    st.header("Live Food Listings")
    conn = get_db_connection()

    # --- Sidebar Filters ---
    st.sidebar.header("Filter Listings")

    # Fetch filter options from DB
    locations = fetch_data(conn, "SELECT DISTINCT Location FROM Food_Listings ORDER BY Location")['Location'].tolist()
    providers = fetch_data(conn, "SELECT DISTINCT Name FROM Providers ORDER BY Name")['Name'].tolist()
    food_types = fetch_data(conn, "SELECT DISTINCT Food_Type FROM Food_Listings ORDER BY Food_Type")[
        'Food_Type'].tolist()

    # Create widgets
    selected_location = st.sidebar.multiselect("Filter by Location:", locations, default=[])
    selected_provider = st.sidebar.multiselect("Filter by Provider:", providers, default=[])
    selected_food_type = st.sidebar.multiselect("Filter by Food Type:", food_types, default=[])

    # --- Dynamic Query based on Filters ---
    query = """
    SELECT 
        f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, p.Name as Provider, 
        f.Location, f.Food_Type, f.Meal_Type
    FROM Food_Listings f
    JOIN Providers p ON f.Provider_ID = p.Provider_ID
    """

    conditions = []
    params = []

    if selected_location:
        conditions.append("f.Location IN ({})".format(','.join('?' for _ in selected_location)))
        params.extend(selected_location)
    if selected_provider:
        conditions.append("p.Name IN ({})".format(','.join('?' for _ in selected_provider)))
        params.extend(selected_provider)
    if selected_food_type:
        conditions.append("f.Food_Type IN ({})".format(','.join('?' for _ in selected_food_type)))
        params.extend(selected_food_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    filtered_listings = fetch_data(conn, query, params=tuple(params))

    if filtered_listings.empty:
        st.warning("No listings found for the selected filters.")
    else:
        st.dataframe(filtered_listings, use_container_width=True)

# --- 4. TAB 2: ANALYSIS ---

with tab2:
    st.header("Platform Analysis")
    conn = get_db_connection()

    query_display_names = {name.replace("_", " ").title(): name for name in QUERIES.keys()}
    selected_display_name = st.selectbox(
        "Choose a report to view:",
        options=list(query_display_names.keys())
    )
    selected_query_name = query_display_names[selected_display_name]

    st.subheader(f"Results for: `{selected_display_name}`")
    result_df = fetch_data(conn, QUERIES[selected_query_name])

    if not result_df.empty:
        st.dataframe(result_df, use_container_width=True)
        # Attempt to create a relevant chart
        if len(result_df.columns) >= 2:
            try:
                st.bar_chart(result_df.set_index(result_df.columns[0]))
            except Exception:
                st.info("This data might not be suitable for a bar chart.")
    else:
        st.warning("No results found for this analysis.")

# --- 5. TAB 3: MANAGE DATA (CRUD) ---

with tab3:
    st.header("Manage Database Records")
    conn = get_db_connection()

    table_to_manage = st.radio("Select a table to manage:",
                               ("Providers", "Receivers", "Food Listings", "Claims"), horizontal=True)

    # --- PROVIDER CRUD ---
    if table_to_manage == "Providers":
        st.subheader("Add or Update a Provider")
        with st.form("provider_form", clear_on_submit=True):
            name = st.text_input("Provider Name*")
            ptype = st.selectbox("Provider Type", ["Restaurant", "Individual", "Supermarket", "NGO", "Other"])
            address = st.text_input("Address")
            city = st.text_input("City")
            contact = st.text_input("Contact (Phone/Email)")

            submitted = st.form_submit_button("Add Provider")
            if submitted and name:
                query = "INSERT INTO Providers (Name, Type, Address, City, Contact) VALUES (?, ?, ?, ?, ?)"
                if execute_query(conn, query, (name, ptype, address, city, contact)):
                    st.success(f"Provider '{name}' added successfully!")
                    st.rerun()
            elif submitted:
                st.error("Provider Name is a required field.")

        st.subheader("Current Providers")
        st.dataframe(fetch_data(conn, "SELECT * FROM Providers"), use_container_width=True)

    # --- RECEIVER CRUD ---
    if table_to_manage == "Receivers":
        st.subheader("Add or Update a Receiver")
        with st.form("receiver_form", clear_on_submit=True):
            name = st.text_input("Receiver Name*")
            rtype = st.selectbox("Receiver Type", ["NGO", "Shelter", "Individual", "Community Fridge", "Other"])
            city = st.text_input("City")
            contact = st.text_input("Contact (Phone/Email)")

            submitted = st.form_submit_button("Add Receiver")
            if submitted and name:
                query = "INSERT INTO Receivers (Name, Type, City, Contact) VALUES (?, ?, ?, ?)"
                if execute_query(conn, query, (name, rtype, city, contact)):
                    st.success(f"Receiver '{name}' added successfully!")
                    st.rerun()
            elif submitted:
                st.error("Receiver Name is a required field.")

        st.subheader("Current Receivers")
        st.dataframe(fetch_data(conn, "SELECT * FROM Receivers"), use_container_width=True)

    # --- FOOD LISTING CRUD ---
    if table_to_manage == "Food Listings":
        st.subheader("Add a Food Listing")
        provider_df = fetch_data(conn, "SELECT Provider_ID, Name FROM Providers")
        provider_map = dict(zip(provider_df['Name'], provider_df['Provider_ID']))

        with st.form("food_listing_form", clear_on_submit=True):
            provider_name = st.selectbox("Select Provider*", options=provider_map.keys())
            food_name = st.text_input("Food Name*")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            expiry_date = st.date_input("Expiry Date")
            location = st.text_input("Location (City)")
            food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan", "Unknown"])
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks", "Unknown"])

            submitted = st.form_submit_button("Add Listing")
            if submitted and food_name and provider_name:
                provider_id = provider_map[provider_name]
                query = """
                INSERT INTO Food_Listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                if execute_query(conn, query,
                                 (food_name, quantity, expiry_date, provider_id, location, food_type, meal_type)):
                    st.success(f"Listing '{food_name}' added successfully!")
                    st.rerun()
            elif submitted:
                st.error("Food Name and Provider are required fields.")

        st.subheader("Current Food Listings")
        st.dataframe(fetch_data(conn, "SELECT * FROM Food_Listings"), use_container_width=True)

    # --- CLAIMS CRUD ---
    if table_to_manage == "Claims":
        st.subheader("Add or Update a Claim")

        food_df = fetch_data(conn, "SELECT Food_ID, Food_Name FROM Food_Listings")
        food_map = dict(zip(food_df['Food_Name'], food_df['Food_ID']))

        receiver_df = fetch_data(conn, "SELECT Receiver_ID, Name FROM Receivers")
        receiver_map = dict(zip(receiver_df['Name'], receiver_df['Receiver_ID']))

        with st.form("claim_form", clear_on_submit=True):
            food_name = st.selectbox("Select Food Item*", options=food_map.keys())
            receiver_name = st.selectbox("Select Receiver*", options=receiver_map.keys())
            status = st.selectbox("Claim Status", ["Pending", "Successful", "Failed"])

            submitted = st.form_submit_button("Add Claim")
            if submitted:
                food_id = food_map[food_name]
                receiver_id = receiver_map[receiver_name]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                query = "INSERT INTO Claims (Food_ID, Receiver_ID, Status, Timestamp) VALUES (?, ?, ?, ?)"
                if execute_query(conn, query, (food_id, receiver_id, status, timestamp)):
                    st.success(f"Claim for '{food_name}' by '{receiver_name}' added!")
                    st.rerun()

        st.subheader("Current Claims")
        st.dataframe(fetch_data(conn, "SELECT * FROM Claims"), use_container_width=True)

# --- 6. TAB 4: CONTACT DIRECTORY ---

with tab4:
    st.header("Contact Information")

    st.subheader("Providers")
    provider_contacts = fetch_data(conn, "SELECT Name, Type, City, Contact FROM Providers")
    st.dataframe(provider_contacts, use_container_width=True)

    st.subheader("Receivers")
    receiver_contacts = fetch_data(conn, "SELECT Name, Type, City, Contact FROM Receivers")
    st.dataframe(receiver_contacts, use_container_width=True)

