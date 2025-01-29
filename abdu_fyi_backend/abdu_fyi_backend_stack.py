'''
abdu.fyi  backend stack
'''
# import json
import time
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
    CfnOutput,
    aws_iam as iam
)
# import requests
from constructs import Construct


class AbduFyiBackendStack(Stack):
    '''
    Used to Deploy and maintain the domain abdu.fyi and all of its subdomains
    '''

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_domain_name = "abdu.fyi"

        hyphenated_user_domain_name = user_domain_name.replace('.', '-')

        # to be changed to production
        print('bucket creation...')
        site_bucket = s3.Bucket(scope=self, website_index_document="index.html", website_error_document="404.html", bucket_name=user_domain_name,
                                id=user_domain_name, removal_policy=RemovalPolicy.DESTROY, block_public_access=s3.BlockPublicAccess.BLOCK_ACLS)
        print('bucket policy...')
        site_bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[site_bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()]
        ))
        print('hosted zone...')
        hostedzone = route53.PublicHostedZone(
            self, hyphenated_user_domain_name + "-hosted-zone", zone_name=user_domain_name, comment="managed by CDK")
        
        # print('sleep')
        # 2 minutes sleep
        # time.sleep(60)

        # ns = ''
        # for i in hostedzone.hosted_zone_name_servers:
        #     ns = ns + i + '/n'

        # print('name servers')
        
        # CfnOutput(self, "HostedZoneNameservers",
        #           value = ns,
        #           description="Nameservers for the hosted zone"
        #           )

        # response = input("Enter after you have changed the name servers on your domain provider (Y/N): ")

        # if (response == 'N'):
        #     print('Exiting program...')
        #     return

        # use in godaddy to change nameservers
        # nameservers = hostedzone.hosted_zone_name_servers

        # self.update_godaddy_nameservers(
        #     domain="abdu.fyi", nameservers=nameservers)

        certificate = cm.Certificate(self, hyphenated_user_domain_name + "-cert-ssl",
                                     domain_name=user_domain_name,
                                     subject_alternative_names=[
                                         f"www.{user_domain_name}"],
                                     validation=cm.CertificateValidation.from_dns(
                                         hostedzone)
                                     )

        site_distribution = cloudfront.Distribution(id="NAdistribution-abdu-fyi", scope=self, default_behavior=cloudfront.BehaviorOptions(
            origin=origins.S3Origin(site_bucket),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER
        ), domain_names=[user_domain_name], certificate=certificate, default_root_object="index.html")

        # route53.ARecord(self, "abdu-fyi-subdomain", zone=hostedzone, record_name="www",
        #                 target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(site_distribution)))

        route53.ARecord(self, hyphenated_user_domain_name + "-domain", zone=hostedzone, record_name="",
                        target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(site_distribution)))
        patterns.HttpsRedirect(
            self, "WwwToNonWwwRedirect",
            zone=hostedzone,
            record_names=[f"www.{user_domain_name}"],
            target_domain=user_domain_name,
            certificate=certificate
        )

        # https://domainnamewire.com/2019/07/25/tutorial-how-to-update-dns-records-using-godaddy-api/

        deployment.BucketDeployment(distribution=site_distribution, sources=[deployment.Source.asset(
            '../abdu-fyi/dist/',)], destination_bucket=site_bucket, scope=self, id="s3deployment")
