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
