from pyterraformer import HumanSerializer

def standard_string(string:str):
    return ' '.join(string.split())

def human_serialization():
    hs = HumanSerializer(terraform=r'c:/tech/terraform.exe')
    example_string = '''resource "aws_s3_bucket" "b" {
      bucket = "my-tf-test-bucket"
    
      tags = {
        Name        = "My bucket"
        Environment = "Dev"
      }
    }
    
    resource "aws_s3_bucket" "b2" {
      bucket = "my-tf-test-bucket"
    
      tags = {
        Name        = "My bucket"
        Environment = "Dev"
      }
    }'''
    bucket = hs.parse_string(example_string)[0]

    bucket.tags["Environment"] = "Prod"
    bucket.bucket = 'my-updated-bucket'

    # and written back to a string
    # formatting requires a valid terraform binary to be provided
    updated = hs.render_object(bucket, format=True)
    print(hs.render_object(bucket, format=False))
    print('-----')
    print(updated)

if __name__ == "__main__":
    human_serialization()