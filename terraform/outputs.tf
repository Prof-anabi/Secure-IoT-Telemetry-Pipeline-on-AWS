data "aws_iot_endpoint" "ats" { endpoint_type = "iot:Data-ATS" }

output "iot_endpoint"  { value = data.aws_iot_endpoint.ats.endpoint_address }
output "dashboard_url" { value = "https://${aws_cloudfront_distribution.cdn.domain_name}" }
output "bucket_name"   { value = aws_s3_bucket.site.id }
output "lambda_role"   { value = aws_iam_role.fn.arn }