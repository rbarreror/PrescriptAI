"""PrescriptAI ML Package.

Core machine learning and data engineering engine for retail probabilistic demand forecasting.
"""

import logging

# Set default logging handler to avoid "No handler found" warnings
logging.getLogger("prescriptai_ml").addHandler(logging.NullHandler())

__version__ = "0.1.0"