PYTHON ?= python

.PHONY: install run test coverage lint openapi docker-build

install:
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

run:
	$(PYTHON) -m uvicorn app.main:app --reload

test:
	$(PYTHON) -m pytest tests/unit -q

coverage:
	$(PYTHON) -m pytest tests/unit --cov=app --cov-report=term-missing --cov-fail-under=80

lint:
	ruff check app tests
	ruff format --check app tests

openapi:
	$(PYTHON) -c 'import json, yaml; from pathlib import Path; from app.main import app; s = app.openapi(); Path("openapi.json").write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8"); Path("openapi.yaml").write_text(yaml.safe_dump(s, sort_keys=False, allow_unicode=True), encoding="utf-8"); print("Generated openapi.json and openapi.yaml")'

docker-build:
	docker build -t cmpe272-issues-gateway .