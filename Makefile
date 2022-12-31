init:
	pip install -r requirements.txt
run: init
	python3 ./src/main.py
test: init
	echo "No tests yet :("