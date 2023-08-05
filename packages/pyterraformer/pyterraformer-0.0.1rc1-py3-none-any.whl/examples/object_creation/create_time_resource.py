import os
from pyterraformer.terraform import Terraform
from pyterraformer.core import TerraformWorkspace
from pyterraformer.terraform.backends.local_backend import LocalBackend, TemporaryLocalBackend
from logging import StreamHandler
from pyterraformer.serializer.human_serializer import HumanSerializer

from pyterraformer.constants import logger
from pyterraformer.core.resources import ResourceObject

'''resource "time_static" "example" {}

output "current_time" {
  value = time_static.example.rfc3339
}'''

class TimeStatic(ResourceObject):
    _type = 'time_static'




if __name__ == "__main__":
    logger.addHandler(StreamHandler())
    tf = Terraform(terraform_exec_path=r'c:/tech/terraform.exe',
                   backend=TemporaryLocalBackend())
    workspace = TerraformWorkspace(terraform=tf, path = os.getcwd(), serializer=HumanSerializer(terraform=tf))

    file = workspace.add_file('time_resource.tf')
    obj = TimeStatic(id='test', funky_monkey=True)
    file.add_object(obj)

    workspace.save()
    #
    # for cmd in ['init', ['apply', '-auto-approve', ]]:
    #     output = tf.run(cmd, os.getcwd())
    #     print(output)