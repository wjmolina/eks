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

resource "aws_iam_role" "eks" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

data "aws_iam_policy" "eks" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "eks" {
  role       = aws_iam_role.eks.name
  policy_arn = data.aws_iam_policy.eks.arn
}

resource "aws_cloudformation_stack" "vpc" {
  name         = "eks"
  template_url = "https://s3.us-west-2.amazonaws.com/amazon-eks/cloudformation/2020-10-29/amazon-eks-vpc-sample.yaml"
}

resource "aws_eks_cluster" "eks" {
  name     = "eks"
  role_arn = aws_iam_role.eks.arn
  vpc_config {
    subnet_ids = split(",", aws_cloudformation_stack.vpc.outputs["SubnetIds"])
  }
}
