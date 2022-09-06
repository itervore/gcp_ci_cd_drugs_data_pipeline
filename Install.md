# Configuration initiale

Création du repo github

Création du projet GCP

Liste des APIs à activer : 

- Cloud Build
- Compute Engine 

``` bash
gcloud services enable cloudbuild.googleapis.com compute.googleapis.com composer.googleapis.com dataflow.googleapis.com
```


Configurations à effectuer :

1. Lancer des pipeline Cloud run depuis Github: [documentation](https://cloud.google.com/build/docs/automating-builds/github/build-repos-from-github?hl=fr)
2. Préparer l'usage de Terraform en créant le bucket qui servira de backend pour les tf-states : [documentation](https://cloud.google.com/docs/terraform/resource-management/store-state)
3. Mettre en place une méthodologie gitops : [documentation](https://cloud.google.com/architecture/managing-infrastructure-as-code?hl=fr)
4. Création de la pipeline CI CD dataflow : [documentation](https://github.com/GoogleCloudPlatform/professional-services/tree/main/examples/dataflow-production-ready/python)
5. Remplir la variable project dans main_1st_install.tf
6. Remplir les variables terraform dans  envs/prod-us/terraform.tfvars
7. Creation du backend gcs pour Terraform
   ```bash
    terraform apply
    ```
8. Deploiement de l'architecture Terraform 
    ```bash
    cd envs/prod-us
    terraform apply
    ```
9. Configuration de l'environnement de développement : 
    ```bash
    python3 -m venv /tmp/venv/dataflow-data-pipeline-env
    source /tmp/venv/dataflow-data-pipeline-env/bin/activate
    pip install -r source-code/requirements.txt
    ``` 
10. Configuration des varibles d'environnement pour l'exécution en local : 
    ```bash
    export PROJECT_ID="gcp-ci-cd-drugs-data-pipeline"
    export INPUT_BUCKET="gs://${PROJECT_ID}-composer-input-test"
    export OUTPUT_BUCKET="gs://${PROJECT_ID}-composer-result-test"
    export BQ_RESULTS="${PROJECT_ID}:gcp_ci_cd_drugs_data_pipeline"
    export BQ_ERRORS="${PROJECT_ID}:gcp_ci_cd_drugs_data_pipeline"
    export TEMP_LOCATION="gs://${PROJECT_ID}-dataflow-staging-test" 
    export SETUP_FILE="/dataflow/template/data_pipeline/setup.py"
    ```
10. Configuration des varibles d'environnement pour l'exécution sur le service dataflow : 
    ```bash
    export PROJECT_ID="gcp-ci-cd-drugs-data-pipeline"
    export REGION="us-west1"
    export INPUT_BUCKET="gs://${PROJECT_ID}-composer-input-test"
    export OUTPUT_BUCKET="gs://${PROJECT_ID}-composer-result-test"
    export BQ_RESULTS="${PROJECT_ID}:gcp_ci_cd_drugs_data_pipeline"
    export BQ_ERRORS="${PROJECT_ID}:gcp_ci_cd_drugs_data_pipeline"
    export TEMP_LOCATION="gs://${PROJECT_ID}-dataflow-staging-test" 
    export SETUP_FILE="/dataflow/template/data_pipeline/setup.py"
    ```
11. Configuration des variables d'environnement pour l'exécution de temple Flex :
    ```bash
    export SETUP_FILE="/dataflow/template/data_pipeline/setup.py"
    ```
