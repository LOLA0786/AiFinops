#!/usr/bin/env bash
set -e
echo "Bootstrapping AiFinOps: full-stack enterprise scaffolding..."

# requirements
cat << 'REQ' > requirements.txt
httpx
python-dotenv
boto3
streamlit
pandas
numpy
PyGithub
matplotlib
seaborn
prophet
scikit-learn
slack-sdk
kubernetes
joblib
