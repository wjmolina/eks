terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket = "wmolina"
    region = "us-west-1"
    key    = "eks"
  }
}

provider "aws" {
  region = "us-west-1"
}
