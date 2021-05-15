.PHONY: run
run:
	docker run --rm -it --env-file .env -v $(shell pwd)/main.py:/main.py forana/ymc:latest pipenv run python /main.py

.PHONY: k8s-install
k8s-install:
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/secret.yaml
	kubectl apply -f k8s/job.yaml
