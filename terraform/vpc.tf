resource "aws_cloudformation_stack" "vpc" {
  name         = "eks"
  template_url = "https://s3.us-west-2.amazonaws.com/amazon-eks/cloudformation/2020-10-29/amazon-eks-vpc-sample.yaml"
}
