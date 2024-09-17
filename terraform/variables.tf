variable "GCP_PROJECT_ID" {
  type = string
}

variable "CREDENTIALS" {
  type = string
}

variable "region" {
  description = "The region where the resources will be deployed"
  type        = string
  default     = "us-central1"
}

variable "clusterName" {
  description = "Name of our Cluster"
}
variable "diskSize" {
  description = "Node disk size in GB"
}
variable "minNode" {
  description = "Minimum Node Count"
}
variable "maxNode" {
  description = "maximum Node Count"
}
variable "machineType" {
  description = "Node Instance machine type"
}
