# ⚡ Predicting Renewable Energy Power Generation

![Demo](data/corrdiff-before_after.gif)

As the energy sector transitions toward sustainable sources, accurate forecasting of renewable energy production is essential for efficient grid management, energy trading, and system reliability. This project leverages machine learning models to predict power generation from renewable sources—such as solar and wind—based on weather and environmental data.


## 🔍 Key Features

- End-to-end pipeline for renewable energy forecasting
- Data quality checks and preprocessing
- Multiple machine learning models (LSTM, Random Forest, XGBoost)
- Evaluation metrics and visualization tools
- Modular and extensible codebase
- Dependency management with [Poetry](https://python-poetry.org/)
- Reproducible development environment using `.devcontainer`

## 📁 Project Structure


.
├── .devcontainer/                  # Development container configuration for VS Code
├── data/                           # Raw and processed datasets
├── notebooks/                      # Jupyter notebooks for EDA and modeling
├── src/                            # Source code
│   ├── data_quality/               # Data validation and completeness checks
│   ├── forecasting_evaluation/     # Evaluation metrics and visualization scripts
│   ├── models/                     # Model implementations
│   │   ├── lstm/                   # LSTM-based forecasting models
│   │   ├── random_forest_regressor_model/  # Random Forest model
│   │   └── xgboost_model/          # XGBoost model
│   ├── utils/                      # Utility functions and helpers
│   └── data_loader.py              # Module for loading and preprocessing data
├── pyproject.toml                  # Poetry configuration file
├── poetry.lock                     # Locked dependency versions
└── README.md                       # Project documentation

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/renewable-energy-forecasting.git
cd renewable-energy-forecasting

2. Set up the development environment
This project includes a .devcontainer folder for use with https://code.visualstudio.com/docs/devcontainers/containers. To get started:

Install https://www.docker.com/
Install https://code.visualstudio.com/ and the Dev Containers extension
Open the project in VS Code and select:
"Reopen in Container"

This will automatically set up the environment with all dependencies installed.
3. Alternatively, install dependencies manually with Poetry
If you're not using the dev container:

📈 Example
notebooks/solar_forecasting.ipynb

🤝 Contributing
Contributions are welcome! If you'd like to improve this project, feel free to fork the repo, open an issue, or submit a pull request.

📜 License
This project is licensed under the MIT License. See the LICENSE file for details.
