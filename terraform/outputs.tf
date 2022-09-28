output "cloud_formation" {
  value = data.aws_cloudformation_stack.vpc.outputs
}
