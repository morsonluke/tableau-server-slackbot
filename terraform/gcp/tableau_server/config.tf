resource "google_compute_instance" "vm_instance" {
  name                    = "tableau-server-trial"
  metadata_startup_script = file("templates/startup.sh")
  machine_type            = "n1-standard-8"
  tags                    = ["web"]

  boot_disk {
    initialize_params {
      image = "centos-cloud/centos-7"
      size  = 100
    }
  }

  service_account {
    email  = "${google_service_account.tableau_instance_sa.email}"
    scopes = ["userinfo-email", "compute-ro", "storage-rw", "monitoring-write", "logging-write"]
  }

  network_interface {
    # A default network is created for all GCP projects
    network = "${google_compute_network.vpc_network.self_link}"
    access_config {
    }
  }
}

resource "google_compute_network" "vpc_network" {
  name                    = "tableau-network"
  auto_create_subnetworks = "true"
}


resource "google_compute_firewall" "tableau-network" {
  name    = "tableau-firewall"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "8850", "8860", "8000-9000", "27000-27010"]
  }

  source_tags   = ["web"]
  source_ranges = ["0.0.0.0/0"]
}
