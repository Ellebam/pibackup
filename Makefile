include .env
.PHONY: venv install  run-playbooks clean docker-build docker-run

export USERNAME GMAIL_USERNAME GMAIL_PASSWORD GMAIL_RECEIVER SERVICE_ACCOUNT_FILE

venv:
	python3 -m venv venv
	echo "Virtual environment created. Activate with 'source venv/bin/activate'."

install-collections: venv
	mkdir -p ./venv/collections
	source venv/bin/activate && ansible-galaxy collection install -r requirements.yml -p ./venv/collections

install-roles: venv
	mkdir -p ./venv/roles
	source venv/bin/activate && ansible-galaxy role install -r requirements.yml -p ./venv/roles


install: install-collections install-roles
	./venv/bin/pip install -r requirements.txt
	echo "Dependencies installed."


run-playbooks: install
	./venv/bin/ansible-playbook -i grudge,\
		-u ellebam\
		--extra-vars "username=${USERNAME}"\
		-e 'ansible_ssh_extra_args="-o StrictHostKeyChecking=no"'\
		setup-backup-server.yml 


clean:
	rm -rf venv
	echo "Cleaned up virtual environment."



docker-build:
	docker build -t backup-image:latest app/

docker-run:
	mkdir -p testbackups
	docker container prune -f
	docker run -d --name backup-test \
		-v ${PWD}/testbackups:/app/backup \
		-e GMAIL_USERNAME="${GMAIL_USERNAME}" \
		-e GMAIL_PASSWORD="${GMAIL_PASSWORD}" \
		-e GMAIL_RECEIVER="${GMAIL_RECEIVER}" \
		-e SERVICE_ACCOUNT_FILE="${SERVICE_ACCOUNT_FILE}" \
		backup-image:latest 

docker-full-rebuild: docker-build docker-run