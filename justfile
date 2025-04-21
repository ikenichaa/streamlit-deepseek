run-fast-api:
    @echo "✨ Start Fast API..."
    python3 -m uvicorn api:app --reload

run-streamlit:
    @echo "✨ Start Streamlit..."
    python3 -m streamlit run app.py

run-deepseek:
    @echo "✨ Start Deepseek locally"
    docker compose up

down-deepseek:
    @echo "✨ Down Deepseek locally"
    docker compose down
