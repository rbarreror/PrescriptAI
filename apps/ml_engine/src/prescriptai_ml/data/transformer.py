import logging
from typing import List, Optional

from sqlalchemy import text

from prescriptai_ml.data.db_connector import DatabaseConnector

# Initialize the logger for this module
logger = logging.getLogger(__name__)


class DataTransformer:
    """Executes ELT (Extract, Load, Transform) operations directly in the database."""

    def __init__(self, connector: DatabaseConnector):
        """
        Inject the database connector to reuse the existing SQLAlchemy engine.
        """
        self._connector = connector

    def melt_sales_data(
        self,
        year: int,
        schema_bronze: str = "bronze",
        schema_silver: str = "silver",
        id_vars: Optional[List[str]] = None,
    ) -> str:
        """
        Transforms the sales table from wide to long format 
        using PostgreSQL UNNEST arrays.
        """
        if id_vars is None:
            id_vars = ["id", "item_id", "cat_id", "store_id", "state_id"]

        table_bronze = f"sales_train_evaluation_{year}"
        table_silver = f"sales_long_{year}"

        logger.info(f"Orchestrating ELT transformation for {schema_bronze}.{table_bronze}...")

        with self._connector.connect() as conn:
            # 1. Extract column names using safe bind parameters
            query_cols = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = :schema 
                  AND table_name = :table;
            """)
            
            result = conn.execute(query_cols, {"schema": schema_bronze, "table": table_bronze})
            all_cols = [row[0] for row in result.fetchall()]

            # 2. Filter and sort the day columns ('d_')
            d_cols = [col for col in all_cols if col.startswith("d_")]
            d_cols = sorted(d_cols, key=lambda x: int(x.split("_")[1]))

            if not d_cols:
                logger.error(f"No 'd_' columns found in table {table_bronze}.")
                raise ValueError(f"Table {table_bronze} does not have the expected format.")

            # 3. Dynamic SQL construction
            id_vars_sql = ", ".join([f'"{col}"' for col in id_vars])
            d_cols_names_array = ", ".join([f"'{col}'" for col in d_cols])
            d_cols_values_array = ", ".join([f'"{col}"' for col in d_cols])

            sql_melt = text(f"""
                DROP TABLE IF EXISTS {schema_silver}.{table_silver};
                
                CREATE TABLE {schema_silver}.{table_silver} AS
                SELECT 
                    {id_vars_sql},
                    UNNEST(ARRAY[{d_cols_names_array}]) AS d,
                    UNNEST(ARRAY[{d_cols_values_array}]) AS units_sold
                FROM {schema_bronze}.{table_bronze}
                --LIMIT 1000;  -- Optional: limit for testing, remove in production
            """)

            # 4. Execute the transformation
            logger.info(f"Applying Unpivot/Melt in DB ({len(d_cols)} days detected)...")
            conn.execute(sql_melt)
            
            # Mandatory in SQLAlchemy 2.0 for DDL/DML operations that modify the DB
            conn.commit()  

        logger.info(f"Transformation completed! Data saved to {schema_silver}.{table_silver}.")
        return table_silver

    def unify_yearly_tables(
            self,
            base_table_name: str,
            years: List[int],
            source_schema: str = "bronze",
            target_schema: str = "silver"
        ) -> str:
        """
        Unifies multiple yearly tables into a single table using UNION ALL.
        The resulting table will drop the year suffix (e.g., 'sales_long_2011' 
        and 'sales_long_2012' become 'sales_long').
        
        Args:
            base_table_name: The base name of the tables without the year 
                            (e.g., 'sales_long', 'calendar', 'sell_prices').
            years: A list of integers representing the years to concatenate.
            source_schema: The schema containing the input tables.
            target_schema: The schema where the unified table will be created.
            
        Returns:
            The name of the newly created unified table.
        """
        if not years:
            logger.error("The list of years provided is empty.")
            raise ValueError("You must provide at least one year to unify.")

        unified_table_name = base_table_name
        logger.info(f"Unifying {len(years)} years for \
                    '{base_table_name}' in schema '{source_schema}'...")

        with self._connector.connect() as conn:
            # 1. Build the SELECT statements dynamically for each year
            select_statements = []
            for year in years:
                table_name = f"{base_table_name}_{year}"
                select_statements.append(f"SELECT * FROM {source_schema}.{table_name}")
            
            # 2. Join all the queries using UNION ALL (preserves all rows, including duplicates if any)
            union_query = "\nUNION ALL\n".join(select_statements)

            # 3. Build the final DDL query to create the consolidated table
            sql_unify = text(f"""
                DROP TABLE IF EXISTS {target_schema}.{unified_table_name};
                
                CREATE TABLE {target_schema}.{unified_table_name} AS
                {union_query};
            """)

            # 4. Execute the transformation
            logger.info(f"Executing UNION ALL to create {target_schema}.{unified_table_name}...")
            conn.execute(sql_unify)
            conn.commit()  # Mandatory for DDL operations in SQLAlchemy 2.0

        logger.info(f"Unification completed! \
                    Consolidated data saved to {target_schema}.{unified_table_name}.")
        
        return unified_table_name

    def join_core_tables(
            self,
            sales_table: str = "sales_long",
            calendar_table: str = "calendar",
            prices_table: str = "sell_prices",
            schema: str = "silver",
            target_table: str = "features_core",
            limit: Optional[int] = None
        ) -> str:
        """
        Executes a sequence of JOINs to merge sales, calendar, and price data 
        into a single consolidated table within the database.
        
        Args:
            sales_table: Name of the long-format sales table.
            calendar_table: Name of the calendar dimension table.
            prices_table: Name of the weekly prices table.
            schema: Schema where both input and output tables reside.
            target_table: Name of the resulting joined table.
            limit: Optional integer to restrict the number of processed sales rows 
                (useful for quick prototyping and debugging).
                
        Returns:
            The name of the newly created joined table.
        """
        logger.info(f"Initiating dimensional JOIN to build {schema}.{target_table}...")

        # Optional limiting clause for prototyping
        limit_clause = f"LIMIT {limit}" if limit else ""

        with self._connector.connect() as conn:
            # We use CTEs (WITH clause) to structure the joins sequentially.
            # Using LEFT JOIN from sales ensures we never drop sales records, 
            # even if prices or calendar data is unexpectedly missing.
            sql_join = text(f"""
                DROP TABLE IF EXISTS {schema}.{target_table};
                
                CREATE TABLE {schema}.{target_table} AS
                WITH 
                base_sales AS (
                    SELECT *
                    FROM {schema}.{sales_table}
                    {limit_clause}
                ),
                sales_calendar AS (
                    SELECT *
                    FROM base_sales bs
                    LEFT JOIN {schema}.{calendar_table} c
                        USING (d)
                ),
                sales_calendar_prices AS (
                    SELECT 
                        sc.*, 
                        p.sell_price
                    FROM sales_calendar sc
                    LEFT JOIN {schema}.{prices_table} p
                        USING (store_id, item_id, wm_yr_wk)
                )
                SELECT *
                FROM sales_calendar_prices;
            """)

            logger.info("Executing JOIN operations at the database level...")
            conn.execute(sql_join)
            conn.commit()

        logger.info(f"JOIN completed! Master dataset saved to {schema}.{target_table}.")
        return target_table