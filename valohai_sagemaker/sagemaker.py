import sagemaker
from .path import PathDelegate
from .shell import CommandRunner


class SageMakerAdapter(object):
    def __init__(self, image, command_runner=None, path_delegate=None, sagemaker_session=None):
        self.image = image
        self.cmd = command_runner
        self.path = path_delegate
        self.sagemaker_session = sagemaker_session

        if self.path is None:
            self.path = PathDelegate()

        if self.cmd is None:
            self.cmd = CommandRunner()

        if self.sagemaker_session is None:
            self.sagemaker_session = sagemaker.Session()


    def get_account(self):
        return self.sagemaker_session.boto_session.client('sts').get_caller_identity()['Account']


    def get_region(self):
        return self.sagemaker_session.boto_session.region_name


    @property
    def ecr_image_name(self):
        account = self.get_account()
        region = self.get_region()
        return '{}.dkr.ecr.{}.amazonaws.com/{}'.format(account, region, self.image.tagged_name)


    def s3_bucket(self):
        return "s3://{}".format(self.sagemaker_session.default_bucket())


    def s3_prefix(self):
        return "{}.docker-image".format(self.image.name)


    def upload_data(self, input_dir="data"):
        return self.sagemaker_session.upload_data(input_dir, key_prefix=self.s3_prefix())


    def create_estimator(self, needs_push=True, push_verbose=True,
                         train_instance_count=1, train_instance_type="ml.p2.xlarge",
                         **estimator_kwargs):
        if needs_push:
            self.image.push(verbose_build=push_verbose, verbose=push_verbose)

        return sagemaker.estimator.Estimator(
            self.ecr_image_name,
            sagemaker.get_execution_role(),
            train_instance_count,
            train_instance_type,
            sagemaker_session=self.sagemaker_session,
            **estimator_kwargs
        )
