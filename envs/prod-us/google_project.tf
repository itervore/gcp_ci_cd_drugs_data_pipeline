data "google_project" "my_project" {
}

output "number" {
  value = data.google_project.my_project.number
}