output "vpc_id" {
  value = aws_vpc.cloudhsm_vpc.id
}

output "cluster_id" {
  description = "Cluster Id"
  value       = aws_cloudhsm_v2_cluster.cloudhsm_cluster.id

}

output "ec2_instance_id" {
  value = aws_instance.ec2.id
}
