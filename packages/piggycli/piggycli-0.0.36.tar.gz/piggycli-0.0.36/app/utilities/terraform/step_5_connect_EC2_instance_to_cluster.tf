# Connect EC2 Instance to Cluster
# https://docs.aws.amazon.com/cloudhsm/latest/userguide/configure-sg-client-instance.html

# Modify the Default Security Group
resource "aws_security_group_rule" "Add_SSH_Port" {
  depends_on = [aws_vpc.cloudhsm_vpc]

  type = "ingress"
  to_port = 22
  protocol = "tcp"
  from_port = 22
  security_group_id = data.aws_security_groups.default_security_group.ids[0]
  cidr_blocks = var.allowed_ips
}

# Connect the Amazon EC2 Instance to the AWS CloudHSM Cluster
data "aws_security_group" "cloudhsm_security_group" {
  depends_on = [aws_vpc.cloudhsm_vpc, aws_cloudhsm_v2_cluster.cloudhsm_cluster]

  filter {
    name = "group-name"
    values = ["*cloudhsm*"]
  }

  filter {
    name = "vpc-id"
    values = [aws_vpc.cloudhsm_vpc.id]
  }
}

data "aws_instance" "instance" {
  instance_id = aws_instance.ec2.id
}

resource "aws_network_interface_sg_attachment" "sg_attachment" {
  security_group_id    = data.aws_security_group.cloudhsm_security_group.id
  network_interface_id = data.aws_instance.instance.network_interface_id
}

