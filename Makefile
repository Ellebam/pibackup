include .env
.PHONY: venv install  run-playbooks clean docker-build docker-run run-rclone-copy

export 

venv:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	echo "Virtual environment created and dependencies installed."

install-collections: venv
	mkdir -p ./venv/collections
	source venv/bin/activate && ansible-galaxy collection install -r requirements.yml -p ./venv/collections

install-roles: venv
	mkdir -p ./venv/roles
	source venv/bin/activate && ansible-galaxy role install -r requirements.yml -p ./venv/roles

install: install-collections install-roles
	echo "All installations complete."


run-playbooks: install
	./venv/bin/ansible-playbook setup-backup-server.yml -i 192.168.178.80, \
		-u ellebam \
		--extra-vars "username=${USERNAME}"\
		-e 'ansible_ssh_extra_args="-o StrictHostKeyChecking=no"'
		


clean:
	rm -rf venv
	echo "Cleaned up virtual environment."

run-rclone-ls:
	cd app && rclone -vv --config rclone.conf lsd mygdrive: --drive-shared-with-me
run-rclone-copy: 
	rm -rf testbackups/*
	cd app && rclone copy -v --config rclone.conf --drive-shared-with-me mygdrive:'ellebam' testbackups/
	echo "Synced files from Google Drive to testbackups folder."

docker-build:
	docker build -t backup-image:latest app/

docker-run: docker-build
	mkdir -p tempbackups
	mkdir -p backups
	docker container prune -f
	docker run -d --name=backup-container \
	--env-file .env \
	-v ${PWD}/tempbackups:/tempbackups \
	-v ${PWD}/backups:/backups \
	backup-image:latest


docker-full-rebuild: docker-build docker-run

run-python-script:
	 cd app && ../venv/bin/python backups.py

generate-test-backups:
	bash generate_test_backups.sh