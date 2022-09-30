output "cloud_formation" {
  value = aws_cloudformation_stack.eks.outputs
}

output "aws_eks_cluster_eks_name" {
  value = aws_eks_cluster.eks.name
}
