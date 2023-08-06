provider "aws" {
  region     = var.region
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
}

# Create a VPC with one Pulic Subnet
# https://docs.aws.amazon.com/cloudhsm/latest/userguide/create-vpc.html

resource "aws_vpc" "cloudhsm_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "CloudHSM"
  }
}

resource "aws_subnet" "cloudhsm_public_subnet" {
  depends_on = [aws_vpc.cloudhsm_vpc]
  vpc_id     = aws_vpc.cloudhsm_vpc.id
  cidr_block = "10.0.0.0/24"
  tags = {
    Name = "CloudHSM public subnet"
  }
}

resource "aws_internet_gateway" "igw" {
  depends_on = [aws_vpc.cloudhsm_vpc, aws_subnet.cloudhsm_public_subnet]
  vpc_id     = aws_vpc.cloudhsm_vpc.id
}

data "aws_route_table" "rt" {
  depends_on = [aws_vpc.cloudhsm_vpc]
  vpc_id     = aws_vpc.cloudhsm_vpc.id
}

resource "aws_route" "igw_route" {
  depends_on = [
    aws_vpc.cloudhsm_vpc,
    aws_subnet.cloudhsm_public_subnet,
    aws_internet_gateway.igw
  ]
  route_table_id         = data.aws_route_table.rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.cloudhsm_public_subnet.id
  route_table_id = data.aws_route_table.rt.id
}
