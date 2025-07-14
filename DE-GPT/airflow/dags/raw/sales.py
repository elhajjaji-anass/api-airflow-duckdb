import requests
import pandas as pd
import duckdb
import logging
from io import StringIO

def fetch_sales_data(**kwargs):
    """📥 Fetch sales data from the Mockaroo API and return a list of records."""
    api_url = "https://my.api.mockaroo.com/sales_.json"
    headers = {
        "X-API-Key": "788c61e0"
    }

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"❌ Error fetching data, status code: {response.status_code}")
        else:
            # Read CSV response text
            df = pd.read_csv(StringIO(response.text))
            logging.info("✅ Successfully fetched sales data from the API.")
            return df.to_dict(orient='records')  # Return list of dicts for XCom
    except Exception as e:
        logging.error(f"❌ Failed to fetch data from API: {e}")
        raise


def store_sales_data_to_db(**kwargs):
    """📦 Store the fetched sales data into DuckDB raw_layer.sales table."""
    # Récupérer les données depuis XCom
    data_dict = kwargs['ti'].xcom_pull(task_ids='01_fetch_api_sales_data_task')
    df = pd.DataFrame(data_dict)

    # 🔗 Connexion à DuckDB
    duckdb_path = "/opt/airflow/dags/db/ecommerce_data.duckdb"
    conn = duckdb.connect(duckdb_path)

    # ✅ Insérer dans la table raw_layer.sales
    for record in data_dict:
        conn.execute("""
            INSERT INTO raw_layer.sales (
                order_id, order_date, quantity, payment_method, order_status,
                customer_id, customer_name, email, gender, country_code,
                product_id, product_name, unit_price, unit_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record['order_id'],
            record['order_date'],
            record['quantity'],
            record['payment_method'],
            record['order_status'],
            record['customer_id'],
            record['customer_name'],
            record['email'],
            record['gender'],
            record['country_code'],
            record['product_id'],
            record['product_name'],
            record['unit_price'],
            record['unit_count']
        ))

    conn.close()
    logging.info("✅ Data successfully inserted into DuckDB.")

