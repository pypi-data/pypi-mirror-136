#  Create a Cluster
# https://docs.aws.amazon.com/cloudhsm/latest/userguide/create-cluster.html

resource "aws_cloudhsm_v2_cluster" "cloudhsm_cluster" {
  hsm_type   = "hsm1.medium"
  subnet_ids = aws_subnet.cloudhsm_private_subnets.*.id

  tags = {
    Name = "cloudhsm_cluster"
  }
}
