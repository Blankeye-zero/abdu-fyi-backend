'''
abdu.fyi  backend stack
'''
# import json
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as cm,
    aws_s3_deployment as deployment,
    RemovalPolicy,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_route53_patterns as patterns,
    # CfnOutput,
    aws_iam as iam
)
# import requests
from constructs import Construct


class AbduFyiBackendStack(Stack):
    '''
    Used to Deploy and maintain the domain abdu.fyi and all of its subdomains
    '''
    # def update_godaddy_nameservers(self, domain, nameservers):
    #     gd_prod_key = "XXXX"
    #     gd_prod_secret = "XXXXX"
    #     godaddy_key = "XXXX"
    #     godaddy_secret = "XXXXX"
    #     gd_url = f'https://api.godaddy.com/v1/domains/{domain}/records'

    #     headers = {
    #         'Authorization': f'sso-key {gd_prod_key}:{gd_prod_secret}',
    #         'Content-Type': 'application/json'
    #     }

    #     data = [
    #         {
    #             "type": "NS",
    #             "name": "@",
    #             "data": ns,
    #             "ttl": 3600
    #         } for ns in nameservers
    #     ]

    #     response = requests.put(
    #         gd_url, headers=headers, data=json.dumps(data),)

    #     if response.status_code == 200:
    #         CfnOutput(self, id="domain name server change", key="result",
    #                   value=f"Successfully updated nameservers for {domain}")
    #     else:
    #         CfnOutput(self, id="domain name server change", key="result",
    #                   value=f"Failed to update nameservers: {response.content}")

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_domain_name = "abdu.fyi"

        # to be changed to production

        site_bucket = s3.Bucket(scope=self, website_index_document="index.html", website_error_document="404.html", bucket_name=user_domain_name,
                                id=user_domain_name, removal_policy=RemovalPolicy.DESTROY, block_public_access=s3.BlockPublicAccess.BLOCK_ACLS)

        site_bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[site_bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()]
        ))

        # https://bahr.dev/2020/09/01/multiple-frontends/

        hostedzone = route53.PublicHostedZone(
            self, "abdu-fyi-hosted-zone", zone_name=user_domain_name, comment="managed by CDK")
        
        
        # use in godaddy to change nameservers
        # nameservers = hostedzone.hosted_zone_name_servers

        # self.update_godaddy_nameservers(
        #     domain="abdu.fyi", nameservers=nameservers)

        certificate = cm.Certificate(self, "abdu-fyi-cert-ssl",
                                     domain_name="abdu.fyi",
                                     subject_alternative_names=[
                                         "www.abdu.fyi"],
                                     validation=cm.CertificateValidation.from_dns(
                                         hostedzone)
                                     )

        site_distribution = cloudfront.Distribution(id="NAdistribution-abdu-fyi", scope=self, default_behavior=cloudfront.BehaviorOptions(
            origin=origins.S3Origin(site_bucket),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER
        ), domain_names=["abdu.fyi"], certificate=certificate, default_root_object="index.html")

        # route53.ARecord(self, "abdu-fyi-subdomain", zone=hostedzone, record_name="www",
        #                 target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(site_distribution)))
        route53.ARecord(self, "abdu-fyi-domain", zone=hostedzone, record_name="",
                        target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(site_distribution)))
        patterns.HttpsRedirect(
            self, "WwwToNonWwwRedirect",
            zone=hostedzone,
            record_names=[f"www.{user_domain_name}"],
            target_domain=user_domain_name,
            certificate=certificate
        )
        # for validation_option in cm.CertificateValidation.from_dns(hostedzone):
        #     # Add the CNAME record to the hosted zone
        #     route53.CnameRecord(self, f"ValidationCNAME{validation_option.domain_name}",
        #         zone=hostedzone,
        #         record_name=validation_option.resource_record_name,
        #         domain_name=validation_option.resource_record_value,
        #         ttl=Duration.minutes(5)
        #     )

        # https://domainnamewire.com/2019/07/25/tutorial-how-to-update-dns-records-using-godaddy-api/

        deployment.BucketDeployment(distribution=site_distribution, sources=[deployment.Source.asset(
            '../abdu-fyi/dist/',)], destination_bucket=site_bucket, scope=self, id="s3deployment")
