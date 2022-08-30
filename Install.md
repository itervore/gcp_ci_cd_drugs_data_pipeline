# Configuration initiale

Création du repo github

Création du projet GCP

Liste des APIs à activer : 

- Cloud Build
- Compute Engine 

``` bash
gcloud services enable cloudbuild.googleapis.com compute.googleapis.com
```


Configurations à effectuer :

1. Lancer des pipeline Cloud run depuis Github: [documentation](https://cloud.google.com/build/docs/automating-builds/github/build-repos-from-github?hl=fr)
2. Préparer l'usage de Terraform en créant le bucket qui servira de backend pour les tf-states : [documentation](https://cloud.google.com/docs/terraform/resource-management/store-state)
3. Mettre en place une méthodologie gitops : [documentation](https://cloud.google.com/architecture/managing-infrastructure-as-code?hl=fr)