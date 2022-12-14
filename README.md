# gcp_ci_cd_drugs_data_pipeline


## Architecture

### Gitops
IAC via Teraform. Trunk developpement sur la branche main avec un dossier par environment

[source de bonnes pratiques](https://developers.redhat.com/articles/2022/07/20/git-workflows-best-practices-gitops-deployments#)

Les schémas des tables big query sont disponibles dans le répertoire : envs/prod-us/bigquery_schema
L'ensemble des ressources gcp sont gérées par Terraform

Le réportoire source-code contient la structure suivante : 

source-code : 

    - fichiers de déploiement du DAG
    - fichiers de création d'image FLEX pour la data_pipeline
    - le dossier data_pipeline : 
      - contient les pipelines Apache Beam de chargement et production du json de résultat
      - ficher d'exécution locale des pipelines
      - le dossier pipeline/beam_classes contient les classes qui sont partagées à travers les différentes étapes de traitements 


### Data pipeline

1. Ingestion des données dans un bucket gcs
2. Transformation des données via Dataflow
![ingesstion via dataflow](img/dataflow-graph.png)
3. Ecriture des données dans BigQuery
4. Ecriture de la sortie json dans Cloud Storage (le fichier est disponible en exemple dans le répertoire "result_json")

![image graph](./img/compose-graph.png)

### Traitement ad-hoc

Le résultat de la pipeline est un fichier json mais celui-ci est aussi stocké avec le même schéma dans une table bigquery. Voici la requête que j'utiliserai afin de récupérer le nom du journal ayant cité le plus médicaments différents : 

```SQL
SELECT  
  j.journal_title,
  count(distinct(drug_name)) AS nb_distinct_drug_mention  
FROM `gcp-ci-cd-drugs-data-pipeline.gcp_ci_cd_drugs_data_pipeline.drug_mention`, UNNEST(journals) AS j 
group by j.journal_title 
ORDER BY count(distinct(drug_name)) DESC
LIMIT 100
```


### Source de bonnes pratiques : 
- [Dataflow Production-Ready Pipeline](https://github.com/GoogleCloudPlatform/professional-services/tree/main/examples/dataflow-production-ready)
- [GCP CI/CD with Cloud Build, Composer and Dataflow](https://github.com/marcelomarques05/gcp-cicd-terraform)
- [terraform-google-bootstrap](https://github.com/terraform-google-modules/terraform-google-bootstrap)


### Amélioration à réaliser : 

* Ecriture de tests
* Mettre en place le Change Data Capture entre le chargement brut et la couche de reporting 

## Pour aller plus loin

***Quels sont les éléments à considérer pour faire évoluer votre code afin qu’il puisse gérer de grosses
volumétries de données (fichiers de plusieurs To ou millions de fichiers par exemple)***

Concernant le problèmes des millions de lignes, l'approche via apache beam permettra de gérer le chargement en parallèle des données.
Pour les flux ne permettant pas le chargement des fichiers via beam, il sera préferable de conserver de petits fichiers.

Pour prendre en charge de nombreux petits fichiers, beam sera capable de prendre un charge le répertoire source et de paralléliser le traitement.

Pour les fichiers ne pouvants être charger par beam, il faudra démarrer autant de pipeline de chargement que de fichier afin de paralléliser les traitements.

***Pourriez-vous décrire les modifications qu’il faudrait apporter, s’il y en a, pour prendre en considération de
telles volumétries ?***

Composer permettra de démarrer les chaines de traitements à l'arriver de nouveaux fichiers et de gérer son auto-scaling.


# SQL

## Première partie du test

Trouver le chiffre d’affaires (le montant total des ventes), jour par jour, du 1er janvier 2019 au 31 décembre 2019 :

```SQL
SELECT FORMAT_DATE('%d/%m/%Y', date) as date, sum( prod_price * prod_qty) as ventes 
FROM `gcp_ci_cd_drugs_data_pipeline.TRANSACTION` 
WHERE EXTRACT(YEAR FROM date) = 2019
GROUP BY date
ORDER BY date
```
## Seconde partie du test

Trouver le chiffre d’affaires (le montant total des ventes), jour par jour, du 1er janvier 2019 au 31 décembre 2019. Le résultat
sera trié sur la date à laquelle la commande a été passée.

```SQL
SELECT TRANSACTION.client_id,
  SUM(COALESCE(CASE WHEN PRODUCT_NOMENCLATURE.product_type like 'MEUBLE' THEN TRANSACTION.prod_price * TRANSACTION.prod_qty END, 0))  ventes_meuble,
  SUM(COALESCE(CASE WHEN PRODUCT_NOMENCLATURE.product_type like 'DECO' THEN TRANSACTION.prod_price * TRANSACTION.prod_qty END, 0))  ventes_deco
FROM `gcp_ci_cd_drugs_data_pipeline.PRODUCT_NOMENCLATURE` PRODUCT_NOMENCLATURE 
INNER JOIN `gcp_ci_cd_drugs_data_pipeline.TRANSACTION` TRANSACTION on TRANSACTION.prod_id = PRODUCT_NOMENCLATURE.product_id
WHERE EXTRACT(YEAR FROM date) = 2020
GROUP BY TRANSACTION.client_id
```
