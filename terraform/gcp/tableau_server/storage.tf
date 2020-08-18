resource "google_storage_bucket" "tableau_store" {
  name          = "tableau_config_store"
  location      = var.region
  project       = var.project
  force_destroy = true
  storage_class = "REGIONAL"
}

resource "google_storage_bucket_object" "cluster_config" {
  name   = "config.json"
  source = "${path.module}/templates/config.json.tpl"
  bucket = "${google_storage_bucket.tableau_store.name}"
}

resource "google_storage_bucket_object" "registration_template" {
  name   = "reg_templ.json"
  source = "${path.module}/templates/reg_templ.json.tpl"
  bucket = "${google_storage_bucket.tableau_store.name}"
}