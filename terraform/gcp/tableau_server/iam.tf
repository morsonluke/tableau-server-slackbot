resource "google_service_account" "tableau_instance_sa" {
  account_id   = var.project
  project      = var.project
  display_name = "Tableau Storage User"
}

resource "google_storage_bucket_iam_member" "tableau_instance_sa" {
  bucket = "${google_storage_bucket.tableau_store.name}"
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.tableau_instance_sa.email}"

  depends_on = [
    "google_storage_bucket.tableau_store",
  ]
}