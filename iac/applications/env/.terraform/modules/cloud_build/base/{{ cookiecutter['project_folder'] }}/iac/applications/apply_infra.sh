#!/bin/usr/env bash

project_dev={{ cookiecutter['project_id_dev'] }}
project_uat={{ cookiecutter['project_id_uat'] }}
project_prod={{ cookiecutter['project_id_prod'] }}
project_ops={{ cookiecutter['project_id_ops'] }}

cd {{cookiecutter['project_folder']}}/iac/applications/env

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
