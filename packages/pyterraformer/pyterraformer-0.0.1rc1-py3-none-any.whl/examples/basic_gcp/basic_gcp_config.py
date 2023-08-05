import os
from logging import DEBUG
from logging import StreamHandler

from examples.basic_gcp.generated_example import GoogleStorageBucket, Website, WebsiteItem, CorsItem, Cors
from pyterraformer import HumanSerializer
from pyterraformer.constants import logger
from pyterraformer.core import TerraformWorkspace
from pyterraformer.terraform import Terraform
from pyterraformer.terraform.backends.local_backend import LocalBackend

logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

if __name__ == "__main__":
    tf = Terraform(terraform_exec_path=r'c:/tech/terraform.exe',
                   backend=LocalBackend(path=os.getcwd()))
    workspace = TerraformWorkspace(terraform=tf, path=os.getcwd(), serializer=HumanSerializer(terraform=tf,))

    namespace = workspace.get_file_safe('resource.tf')

    namespace.add_object(GoogleStorageBucket(
        tf_id='test-bucket',
        name="pyterraformer-test-bucket",
        location="US-EAST1",
        project="pyterraformer-test",
        force_destroy=True,
        uniform_bucket_level_access=True,
        website=Website([WebsiteItem(not_found_page="404.html")]),
        cors=Cors([CorsItem(origin=["https://readthedocs.org"],
                            method=[
                                "GET",
                                "HEAD",
                                "PUT",
                                "POST",
                                "DELETE"],
                            response_header=[
                                "*"],
                            max_age_seconds=3601)])
    ),
    replace=True)

    workspace.save()

    application = workspace.apply()
    print(application)
