# Restaurant Pricing Decision Engine

Streamlit decision-support prototype. For any Store x Product it shows the recommended
price, expected business impact, model evidence, the full price-scenario table, a
price-vs-contribution chart and three commercial guardrail checks.

## Files
- `app.py` - the application
- `final_recommendations.csv` - one recommended price per Store x Product
- `prototype_scenarios.csv` - candidate-price scenarios per Store x Product
- `requirements.txt` - dependencies
- `.streamlit/config.toml` - theme

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

Elasticity estimates are based on synthetic historical data; validate any price change
through a controlled pilot before rollout.
