install:
	uv sync

clean:
	rm -rf .venv
	rm -f output.log
	find . -type d -name "__pycache__" -exec rm -rf {} +

run:
	nohup uv run streamlit run app.py > output.log 2>&1 &

stop:
	-pkill -f "streamlit run app.py"

orsup:
	docker compose up -d

orsdown:
	docker compose down
