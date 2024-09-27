import aws_cdk as core
import aws_cdk.assertions as assertions

from abdu_fyi_backend.abdu_fyi_backend_stack import AbduFyiBackendStack

# example tests. To run these tests, uncomment this file along with the example
# resource in abdu_fyi_backend/abdu_fyi_backend_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AbduFyiBackendStack(app, "abdu-fyi-backend")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
