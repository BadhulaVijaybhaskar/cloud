terraform {
  required_version = ">= 1.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.20"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

provider "vault" {
  address = var.vault_addr
}

module "postgres" {
  source = "./modules/postgres"
}

module "langgraph" {
  source = "./modules/langgraph-orchestrator"
  env = {
    DATABASE_URL  = module.postgres.db_url
    VECTOR_DB_URL = module.vector.endpoint
    VAULT_ADDR    = module.vault.addr
  }
}

module "vector" {
  source = "./modules/vector"
}

module "vault" {
  source = "./modules/vault"
}