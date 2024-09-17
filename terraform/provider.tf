provider "google" {
  credentials = var.CREDENTIALS
  project     = var.GCP_PROJECT_ID
  region      = "us-central1"
}


