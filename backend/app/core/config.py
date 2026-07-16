from app.config.settings import settings

# OpenAPI Documentation metadata
API_TITLE = "Agentic AI Framework for Autonomous Retail Fraud Investigation"
API_DESCRIPTION = """
Enterprise-grade agentic auditing framework designed to detect, investigate, and report retail fraud.
Includes interfaces for autonomous agents, transaction analysis, and machine learning fraud models.
"""
API_VERSION = "1.0.0"

# OpenAPI Tags metadata
TAGS_METADATA = [
    {
        "name": "Health",
        "description": "System health check endpoints.",
    },
    {
        "name": "Audit",
        "description": "Retail fraud audit run control and query operations.",
    },
    {
        "name": "Agents",
        "description": "LLM agent status, tool calls, and run parameters.",
    },
]

# Expose settings directly for convenience
app_settings = settings
