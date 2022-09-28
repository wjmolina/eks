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

data "aws_iam_policy" "AmazonEKSClusterPolicy" {
  arn = "AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "" {
  role       = aws_iam_role.eks
  policy_arn = aws_iam_policy.AmazonEKSClusterPolicy.arn
}
