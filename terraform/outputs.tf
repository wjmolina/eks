output "eks_name" {
  value = aws_eks_cluster.eks.name
}

output "ecr_name" {
  value = aws_ecr_repository.eks.name
}
