# Phase J.1 Production Infrastructure
# Terraform configuration for ATOM Cloud production deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

variable "project" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE Cluster Name"
  type        = string
  default     = "atom-prod-cluster"
}

variable "node_count" {
  description = "Number of nodes per zone"
  type        = number
  default     = 3
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project
  region  = var.region
}

# GKE Cluster
resource "google_container_cluster" "atom_cluster" {
  name     = var.cluster_name
  location = var.region

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = google_compute_network.atom_vpc.name
  subnetwork = google_compute_subnetwork.atom_subnet.name

  # Enable network policy
  network_policy {
    enabled = true
  }

  # Enable workload identity
  workload_identity_config {
    workload_pool = "${var.project}.svc.id.goog"
  }

  # Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All networks"
    }
  }
}

# Node Pool
resource "google_container_node_pool" "atom_nodes" {
  name       = "${var.cluster_name}-nodes"
  location   = var.region
  cluster    = google_container_cluster.atom_cluster.name
  node_count = var.node_count

  node_config {
    preemptible  = false
    machine_type = "e2-standard-4"

    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = google_service_account.atom_cluster_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment = "production"
      project     = "atom-cloud"
    }

    tags = ["atom-cluster-node"]
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# VPC Network
resource "google_compute_network" "atom_vpc" {
  name                    = "atom-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "atom_subnet" {
  name          = "atom-subnet"
  ip_cidr_range = "10.0.0.0/16"
  region        = var.region
  network       = google_compute_network.atom_vpc.id

  secondary_ip_range {
    range_name    = "atom-pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "atom-services"
    ip_cidr_range = "10.2.0.0/16"
  }
}

# Service Account for cluster
resource "google_service_account" "atom_cluster_sa" {
  account_id   = "atom-cluster-sa"
  display_name = "ATOM Cluster Service Account"
}

# IAM bindings for service account
resource "google_project_iam_member" "atom_cluster_sa_bindings" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer"
  ])

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.atom_cluster_sa.email}"
}

# Cloud SQL instance for production data
resource "google_sql_database_instance" "atom_db" {
  name             = "atom-prod-db"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
    }

    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.atom_vpc.id
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }

  deletion_protection = false
}

# Database
resource "google_sql_database" "atom_database" {
  name     = "atom_prod"
  instance = google_sql_database_instance.atom_db.name
}

# Database user
resource "google_sql_user" "atom_user" {
  name     = "atom_user"
  instance = google_sql_database_instance.atom_db.name
  password = "atom_password_change_me"
}

# Outputs
output "cluster_name" {
  value = google_container_cluster.atom_cluster.name
}

output "cluster_endpoint" {
  value = google_container_cluster.atom_cluster.endpoint
}

output "database_connection_name" {
  value = google_sql_database_instance.atom_db.connection_name
}