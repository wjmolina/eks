output "region" {
  value = var.region
}

output "cloud_formation" {
  value = aws_cloudformation_stack.eks.outputs
}
