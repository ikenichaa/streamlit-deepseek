# Virtual ENV

## Create virtual env

```
python3 -m venv streamlit-fastapi
```

## Activate virtual env

```
source streamlit-fastapi/bin/activate
```

## Pip

Install package from requirements

```
pip install -r requirements.txt
```

Freeze requirement

```
pip freeze > requirements.txt
```

# Streamlit

```
streamlit run app.py
```

# Fast API

```
uvicorn fast-api:app --reload
```

# Deepseek local

1. Run the two apps from Docker Compose:

```sh
docker compose up -d
```

2. Install the Deepseek models: (This might take a few minutes)

```sh
docker compose exec ollama ollama pull deepseek-r1:7b
```

3. Run the website on http://localhost:3001
