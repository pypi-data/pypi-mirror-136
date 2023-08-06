# Create a private subnet for each availability zone
# https://docs.aws.amazon.com/cloudhsm/latest/userguide/create-subnets.htmlt

data "aws_availability_zones" "available" {}

resource "aws_subnet" "cloudhsm_private_subnets" {
  depends_on = [aws_vpc.cloudhsm_vpc]
  count                   = 3
  vpc_id                  = aws_vpc.cloudhsm_vpc.id
  cidr_block              = element(var.private_subnets, count.index)
  availability_zone       = element(data.aws_availability_zones.available.names, count.index)

  tags = {
    Name = "cloudhsm private subnet"
  }
}
