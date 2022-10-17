migrate:
	dbmate up

drop:
	dbmate drop

test:
	env PYTHONPATH=. pytest
