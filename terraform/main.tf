terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket = "wmolina"
    key    = "eks"
    region = "us-west-1"
  }
}

resource "aws_iam_role" "eks" {
  tags = {
    "Owner" = "wmolina"
  }
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

resource "aws_iam_role_policy_attachment" "eks_AmazonEKSClusterPolicy" {
  role       = aws_iam_role.eks.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_cloudformation_stack" "eks" {
  tags = {
    "Owner" = "wmolina"
  }
  name         = "eks"
  template_url = "https://s3.us-west-2.amazonaws.com/amazon-eks/cloudformation/2020-10-29/amazon-eks-vpc-sample.yaml"
}

resource "aws_eks_cluster" "eks" {
  tags = {
    "Owner" = "wmolina"
  }
  name     = "eks"
  role_arn = aws_iam_role.eks.arn
  vpc_config {
    subnet_ids         = split(",", aws_cloudformation_stack.eks.outputs["SubnetIds"])
    security_group_ids = split(",", aws_cloudformation_stack.eks.outputs["SecurityGroups"])
  }
}

resource "aws_iam_role" "ec2" {
  tags = {
    "Owner" = "wmolina"
  }
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_AmazonEKSWorkerNodePolicy" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "ec2_AmazonEKS_CNI_Policy" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "ec2_AmazonEC2ContainerRegistryReadOnly" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "ec2_AmazonDynamoDBFullAccess" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_eks_node_group" "eks" {
  tags = {
    "Owner" = "wmolina"
  }
  cluster_name   = aws_eks_cluster.eks.name
  node_role_arn  = aws_iam_role.ec2.arn
  subnet_ids     = [split(",", aws_cloudformation_stack.eks.outputs["SubnetIds"])[0]]
  disk_size      = 200
  instance_types = ["t2.small"]
  scaling_config {
    min_size     = 1
    max_size     = 1
    desired_size = 1
  }
}

resource "aws_dynamodb_table" "eks" {
  tags = {
    "Owner" = "wmolina"
  }
  name         = "Milestones"
  hash_key     = "MilestoneId"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "MilestoneId"
    type = "S"
  }
}

resource "aws_dynamodb_table" "connect_four" {
  tags = {
    "Owner" = "wmolina"
  }
  name         = "ConnectFour"
  hash_key     = "GameId"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "GameId"
    type = "S"
  }
}

resource "aws_ecr_repository" "eks" {
  tags = {
    "Owner" = "wmolina"
  }
  name                 = "eks"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = false
  }
}
