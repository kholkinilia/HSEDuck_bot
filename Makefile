init:
	pip install -r requirements.txt
run: init
	python3 ./hseduck/main.py
test: init
	echo "No tests yet :("