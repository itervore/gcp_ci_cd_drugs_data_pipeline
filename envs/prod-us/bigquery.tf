resource "google_bigquery_dataset" "bq_dataset_test" {
  project    = var.project_id
  dataset_id = var.project_name
  location   = var.location
}

resource "google_bigquery_table" "bq_tables_test" {
  for_each   = fileset(var.bq_path_to_schemas, "*.json")
  project    = var.project_id
  dataset_id = google_bigquery_dataset.bq_dataset_test.dataset_id
  table_id   = split(".", each.key)[0]
  schema     = file("${path.root}/${var.bq_path_to_schemas}/${each.key}")
  deletion_protection=false
}

output "project_name" {
  value = google_bigquery_dataset.bq_dataset_test.project
}

output "bq_dataset_test" {
  value = google_bigquery_dataset.bq_dataset_test.dataset_id
}