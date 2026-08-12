# --workers 1 : flow_store (routes/auth.py) est en mémoire process, pas partagé entre workers.
web: gunicorn app:app --workers 1 --bind 0.0.0.0:$PORT
