[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/jagdevsinghdosanjh/liquidity_analyzer/main/app.py)


💧 Liquidity Analyzer Pro
A modular, API‑ready, classroom‑friendly liquidity analysis suite built with Python + Streamlit.

This app helps traders, students, and educators explore:

Bid‑Ask Spread

Amihud Illiquidity

Kyle’s Lambda

Order Book Imbalance

Slippage

Execution Speed

Depth Heatmaps

Multi‑Asset Comparison

PDF Reporting

Teaching Mode (explains each metric)

🚀 Features
Upload CSV or fetch real‑time data from Binance API

Interactive charts (Plotly)

Order book depth heatmaps

Multi‑asset comparison

Auto‑generated PDF reports

Modular architecture for easy extension

Secure API key handling

Streamlit Cloud compatible

📦 Installation
bash
git clone https://github.com/YOUR_USERNAME/liquidity-analyzer.git
cd liquidity-analyzer
pip install -r requirements.txt
🔐 API Key Setup
1. Local Development
Copy the example file:

bash
cp config/settings.toml.example config/settings.toml
Add your API keys:

Code
[api]
api_key = "YOUR_KEY"
api_secret = "YOUR_SECRET"
2. Streamlit Cloud
Go to:

Settings → Secrets → Add secrets

Paste:

Code
[api]
api_key = "YOUR_KEY"
api_secret = "YOUR_SECRET"
▶️ Run the App
bash
streamlit run app.py
📁 Project Structure
Code
liquidity_analyzer/
│
├── app.py
├── config/
│   ├── settings.toml.example
│
├── modules/
│   ├── api_client.py
│   ├── liquidity_metrics.py
│   ├── visualizer.py
│   ├── report_generator.py
│   ├── teaching_mode.py
│   ├── utils.py
│   └── data_loader.py
│
├── assets/
│   └── logo.png
│
├── sample_data/
│   └── sample_orderbook.csv
│
├── requirements.txt
├── README.md
└── .gitignore
🛡️ Security Notes
Never commit API keys

.gitignore blocks all secret files

Streamlit Cloud uses encrypted secrets

No sensitive data is stored in the repository

🧑‍🏫 Teaching Mode
Enable explanations for each metric:

What it means

Why it matters

How to interpret it

Perfect for classrooms and workshops.

🤝 Contributing
Pull requests are welcome.
For major changes, open an issue first to discuss what you’d like to improve.

📜 License
MIT License.

🌟 Ready for GitHub & Streamlit Deployment
You now have:

✔ requirements.txt  
✔ .gitignore  
✔ README.md  
✔ Secure API key templates
✔ Deployment‑safe structure