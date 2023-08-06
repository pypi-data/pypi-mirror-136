# Launch an EC2 Client
# https://docs.aws.amazon.com/cloudhsm/latest/userguide/launch-client-instance.html

data "aws_ami" "amazon_linux_2" {
  most_recent      = true
  owners           = ["amazon"]

  filter {
   name   = "name"
   values = ["amzn2-ami-hvm*"]
 }
}


data "aws_security_groups" "default_security_group" {
  depends_on = [aws_vpc.cloudhsm_vpc]

  filter {
    name = "group-name"
    values = ["*default*"]
  }

  filter {
    name = "vpc-id"
    values = [aws_vpc.cloudhsm_vpc.id]
  }
  
}

resource "aws_instance" "ec2" {
  depends_on = [aws_vpc.cloudhsm_vpc, aws_subnet.cloudhsm_public_subnet]
    
  ami = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro"
  subnet_id = aws_subnet.cloudhsm_public_subnet.id
  associate_public_ip_address = true
  vpc_security_group_ids = data.aws_security_groups.default_security_group.ids
  key_name = var.ssh_key_name
}
