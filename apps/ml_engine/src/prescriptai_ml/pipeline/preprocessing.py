import logging
from typing import List

from prescriptai_ml.data.db_connector import DatabaseConnector
from prescriptai_ml.data.transformer import DataTransformer

logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """Orchestrates the sequential transformation steps to build the ML dataset."""

    def __init__(self, connector: DatabaseConnector):
        self._transformer = DataTransformer(connector)

    def run_preparation_pipeline(self, target_years: List[int]) -> None:
        """
        Executes the ELT sequence: melting wide sales tables and unifying splits.
        """
        logger.info("=== STARTING PRESCRIPT-AI DATA PREPARATION PIPELINE ===")

        # 1. Melt the raw sales tables from wide format (bronze) to long format (silver)
        for year in target_years:
            self._transformer.melt_sales_data(year=year)

        # 2. Unify the long sales records into a master table
        self._transformer.unify_yearly_tables(
            base_table_name="sales_long",
            years=target_years,
            source_schema="silver",
            target_schema="silver"
        )
        
        # 3. Unify complementary dimensions
        self._transformer.unify_yearly_tables(
            base_table_name="calendar",
            years=target_years,
            source_schema="bronze",
            target_schema="silver"
        )
        
        self._transformer.unify_yearly_tables(
            base_table_name="sell_prices",
            years=target_years,
            source_schema="bronze",
            target_schema="silver"
        )

        # 4. Join all unified tables into a single wide dataset for ML feature engineering
        self._transformer.join_core_tables(
            sales_table="sales_long",
            calendar_table="calendar",
            prices_table="sell_prices",
            schema="silver",
            target_table="features_core",
            #limit=limit_prototyping
        )

        logger.info("=== PREPROCESSING PIPELINE COMPLETED SUCCESSFULLY ===")