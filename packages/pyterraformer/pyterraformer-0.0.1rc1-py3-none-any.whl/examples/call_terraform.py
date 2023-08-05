import os
from pyterraformer.terraform import Terraform
from pyterraformer.terraform.backends.local_backend import LocalBackend

if __name__ == "__main__":
    tf = Terraform(terraform_exec_path=r'c:/tech/terraform.exe',
                   backend=LocalBackend(path=os.getcwd()))

    output = tf.run('init', os.getcwd())
    print(output)