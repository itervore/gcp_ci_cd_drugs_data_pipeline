# gcp_ci_cd_drugs_data_pipeline


## Architecture

### Gitops
IAC via Teraform. Trunk developpement sur la branche main avec un dossier par environment
[source de bonnes pratiques](https://developers.redhat.com/articles/2022/07/20/git-workflows-best-practices-gitops-deployments#)

### Data pipeline

1. Ingestion des données dans un bucket gcs
2. Transformation des données via Dataflow
3. Ecriture des données dans BigQuery
