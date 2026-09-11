from datetime import datetime, timezone


def get_system_status():
    return {
        "service": "hivexchange-platform",
        "environment": "production",
        "region": "ap-south",
        "version": "2.8.4",
        "status": "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "components": {
            "gateway": {
                "status": "operational",
                "latency_ms": 42
            },
            "market_engine": {
                "status": "operational",
                "latency_ms": 61
            },
            "wallet_sync": {
                "status": "operational",
                "queue_depth": 3
            },
            "api_service": {
                "status": "degraded",
                "latency_ms": 284
            },
            "database": {
                "status": "operational",
                "replica_lag_ms": 18
            }
        },

        "uptime_seconds": 864321,
        "maintenance_mode": False
    }

def get_market_data():
    return {
        "BTC": {"price": 68240.50, "change_24h": 1.82},
        "ETH": {"price": 3518.20, "change_24h": -0.74},
        "SOL": {"price": 162.48, "change_24h": 2.11}
    }


def get_account_summary():
    return {
        "user": "synthetic-user",
        "portfolio_value": 24820.46,
        "available_balance": 4250.00,
        "currency": "USD",
        "account_tier": "Standard"
    }