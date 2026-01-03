def explain(metric):
    explanations = {
        "bid-ask spread": "The bid-ask spread shows how tight the market is. Smaller = more liquid.",
        "amihud illiquidity": "Amihud Illiquidity measures price impact per unit volume. Lower = more liquid.",
        "order book imbalance": "Shows which side dominates the market. Positive = more bids, negative = more asks.",
        "kyle's lambda": "Estimates how much price moves per unit of signed volume. Lower = more liquid."
    }
    return explanations.get(metric.lower(), "No explanation available.")

# def explain(metric):
#     explanations = {
#         "spread": "The bid-ask spread shows how tight the market is. Smaller = more liquid.",
#         "amihud": "Amihud Illiquidity measures price impact per unit volume.",
#         "imbalance": "Order book imbalance shows which side dominates the market.",
#         "lambda": "Kyle’s Lambda estimates how much price moves per unit of signed volume."
#     }
#     return explanations.get(metric, "No explanation available.")
