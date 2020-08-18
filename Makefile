ifneq (,)
.error This Makefile requires GNU Make.
endif

tableau:
	cd ./terraform/gcp/tableau_server/ && tfswitch && terraform init && terraform apply

zipfunctions:
	cd ./cloud_functions/slackbot_publish/ && rm -rf index.zip && zip -r index.zip main.py publish.py requirements.txt
	cd ./cloud_functions/slackbot_consume/ && rm -rf index.zip && zip -r index.zip main.py tableau_api.py requirements.txt

cloudfunctions:
	cd ./terraform/gcp/cloud_functions/slackbot_publish/ && tfswitch && terraform init && terraform apply -auto-approve
	cd ./terraform/gcp/cloud_functions/slackbot_pubsub_consume/ && tfswitch && terraform init && terraform apply -auto-approve

destroy:
	cd ./terraform/gcp/tableau_server/ && tfswitch && terraform destroy
	cd ./terraform/gcp/cloud_functions/slackbot_publish/ && tfswitch && terraform destroy
	cd ./terraform/gcp/cloud_functions/slackbot_pubsub_consume/ && tfswitch && terraform destroy
