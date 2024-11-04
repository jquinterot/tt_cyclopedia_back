commands:
run app:
poetry run start_app

if any dependency is changed:
poetry lock --no-update

after that:
poetry install

docs url:
http://127.0.0.1:8000/docs

run tests:
pytest