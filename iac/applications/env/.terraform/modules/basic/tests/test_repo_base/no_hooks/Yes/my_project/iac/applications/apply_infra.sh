#!/bin/usr/env bash

project_dev=my-project-dev
project_uat=my-project-uat
project_prod=my-project-prod
project_ops=my-project-ops

cd my_project/iac/applications/env

for env in dev uat prod ops; do

        id=project_$env
        gcloud config set project "${!id}"

        terraform init -backend-config="${env}.backend" -reconfigure
        terraform plan -out="tf.plan" -var-file="${env}.tfvars.json"

        while true; do
        read -p "Apply plan to ${env} project? " ans
        case $ans in
                [Yy]* )
                        terraform apply "tf.plan" &&
                        break
                        ;;
                [Nn]* )
                        break
                        ;;
                * )
                        echo "Choose Y or N."
                        ;;
        esac
        done

        if [ "$env" = "prod" ]; then
                cd ../ops
        fi
done
