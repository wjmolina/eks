output "cloud_formation" {
  value = aws_cloudformation_stack.eks.outputs
}

output "kubeconfig" {
  value = null_resource.kubeconfig
}
