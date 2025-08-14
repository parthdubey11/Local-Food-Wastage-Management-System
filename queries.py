# queries.py
# This file stores all the SQL queries for the application.

QUERIES = {
    # --- Original 15 Queries ---
    "providers_receivers_per_city": """
        SELECT City, 
               COUNT(DISTINCT Provider_ID) AS Providers, 
               COUNT(DISTINCT Receiver_ID) AS Receivers
        FROM (
            SELECT City, Provider_ID, NULL AS Receiver_ID FROM Providers
            UNION ALL
            SELECT City, NULL, Receiver_ID FROM Receivers
        )
        GROUP BY City
    """,
    "top_provider_type": """
        SELECT Type, COUNT(*) AS Total_Providers
        FROM Providers GROUP BY Type ORDER BY Total_Providers DESC LIMIT 1
    """,
    "contact_providers_in_mumbai": """
        SELECT Name, Contact, City FROM Providers WHERE City = 'Mumbai'
    """,
    "top_5_receivers_by_claims": """
        SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
        FROM Claims c JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        GROUP BY r.Name ORDER BY Total_Claims DESC LIMIT 5
    """,
    "total_food_quantity_available": """
        SELECT SUM(Quantity) AS Total_Quantity FROM Food_Listings
    """,
    "city_with_most_listings": """
        SELECT Location, COUNT(*) AS Listings
        FROM Food_Listings GROUP BY Location ORDER BY Listings DESC LIMIT 1
    """,
    "most_common_food_types": """
        SELECT Food_Type, COUNT(*) AS Count
        FROM Food_Listings GROUP BY Food_Type ORDER BY Count DESC
    """,
    "claims_per_food_item": """
        SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
        FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Food_Name ORDER BY Claim_Count DESC
    """,
    "top_provider_by_successful_claims": """
        SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        JOIN Providers p ON f.Provider_ID = p.Provider_ID
        WHERE c.Status = 'Successful'
        GROUP BY p.Name ORDER BY Successful_Claims DESC LIMIT 1
    """,
    "claim_status_distribution": """
        SELECT Status, COUNT(*) AS Count FROM Claims GROUP BY Status
    """,
    "avg_quantity_per_receiver": """
        SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity
        FROM Claims c
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY r.Name
    """,
    "most_claimed_meal_type": """
        SELECT f.Meal_Type, COUNT(*) AS Claim_Count
        FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Meal_Type ORDER BY Claim_Count DESC LIMIT 1
    """,
    "quantity_donated_by_provider": """
        SELECT p.Name, SUM(f.Quantity) AS Total_Quantity
        FROM Food_Listings f JOIN Providers p ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Name ORDER BY Total_Quantity DESC
    """,
    "food_expiring_in_3_days": """
        SELECT Food_Name, Expiry_Date
        FROM Food_Listings
        WHERE julianday(Expiry_Date) - julianday('now') BETWEEN 0 AND 3
    """,
    "top_cities_by_successful_claims": """
        SELECT f.Location, COUNT(*) AS Successful_Claims
        FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        WHERE c.Status = 'Successful'
        GROUP BY f.Location ORDER BY Successful_Claims DESC
    """,
    # --- Additional 7 Queries ---
    "top_5_providers_by_quantity": """
        SELECT p.Name, SUM(f.Quantity) AS Total_Quantity
        FROM Food_Listings f JOIN Providers p ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Name ORDER BY Total_Quantity DESC LIMIT 5
    """,
    "top_5_receivers_by_successful_claims": """
        SELECT r.Name, COUNT(c.Claim_ID) AS Successful_Claims
        FROM Claims c JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        WHERE c.Status = 'Successful'
        GROUP BY r.Name ORDER BY Successful_Claims DESC LIMIT 5
    """,
    "food_type_distribution_in_successful_claims": """
        SELECT f.Food_Type, COUNT(*) AS Successful_Claims
        FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        WHERE c.Status = 'Successful'
        GROUP BY f.Food_Type ORDER BY Successful_Claims DESC
    """,
    "daily_claim_trends": """
        SELECT DATE(Timestamp) AS Claim_Date, COUNT(*) AS Total_Claims
        FROM Claims GROUP BY Claim_Date ORDER BY Claim_Date
    """,
    "food_items_claimed_multiple_times": """
        SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
        FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Food_Name HAVING Claim_Count > 1
        ORDER BY Claim_Count DESC
    """,
    "providers_with_100_percent_successful_claims": """
        SELECT p.Name
        FROM Providers p
        JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
        JOIN Claims c ON f.Food_ID = c.Food_ID
        GROUP BY p.Name
        HAVING SUM(CASE WHEN c.Status = 'Successful' THEN 1 ELSE 0 END) = COUNT(c.Claim_ID)
    """
}