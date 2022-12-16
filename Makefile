migrate:
	dbmate up

drop:
	dbmate drop

test:
	env PYTHONPATH=. pytest

lint:
	mkdir -p reports
	touch reports/pylint.txt;
	chmod -R 777 reports/
	isort app --check
	black app --check
	pylint app | tee reports/pylint.txt
	mypy app