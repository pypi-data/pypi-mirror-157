from easyTDV.UserAwsAuth import UserAwsAuth
from botocore.exceptions import ClientError
from easyTDV.DeploymentNomenclature import *
from easyTDV.deployment_helper import generate_job_id, upload_file_to_s3, create_train_clf_stack, progress_bar, get_api_endpoint
from pathlib import Path
import boto3, logging, time


class Deploy:
    dir = Path(__file__).parent
    template_stack_local_path = (dir / "clf_deployment_stack.json").__str__()
    deployment_lbd_local_path = (dir / "lambda_deployment.zip").__str__()
    
    def __init__(self,
                 bucket: str,
                 model_s3_key: str,
                 input_model_type,
                 auth_object: UserAwsAuth,
                 region = "eu-west-3"
                 ):
        self.bucket = bucket
        self.model_s3_key = model_s3_key
        self.input_model_type = input_model_type
        self.access_key_id = auth_object.secret_key_id
        self.secret_access_key = auth_object.secret_access_key
        self.region = region
        self.job_id = generate_job_id()
        self.nomenclature_object = DeploymentNomenclature(self.job_id, self.bucket, self.region)


    def prepare_deployment(self):
        """
        Charger vers s3 le template CloudFormation et le code la Lambda RequestProcesssor
        :return: les keys S3 des fichiers chargés vers S3
        """
        print(f"JOBID: {self.job_id}")
        s3_client = boto3.client('s3', aws_access_key_id=self.access_key_id,
                                 aws_secret_access_key=self.secret_access_key, region_name=self.region)

        s3_lbd_request_processor_location = self.nomenclature_object.get_s3_lbd_location()
        s3_stack_template_location = self.nomenclature_object.get_s3_stack_template_location()

        try:
            upload_file_to_s3(s3_client, self.deployment_lbd_local_path, self.bucket, s3_lbd_request_processor_location)
            upload_file_to_s3(s3_client, self.template_stack_local_path, self.bucket, s3_stack_template_location["s3_key"])
        except ClientError as cle:
            logging.error("[DEPLOYMENT]:preparation d'enveronement echouée...")
            raise Exception(cle)
        return {
            "s3_lbd_key" : s3_lbd_request_processor_location,
            "url_s3_stack_template": s3_stack_template_location["s3_url"]
        }


    def create_stack(self, prepare_env_response, invoke_mode=0):
        if invoke_mode not in [0, 1]:
            raise Exception("valeurs acceptées pour invoke_mode: [0:synchrone, 1: asynchrone]")

        request_processor_s3_key = prepare_env_response["s3_lbd_key"]
        url_s3_stack_template = prepare_env_response["url_s3_stack_template"]

        deployment_stack_name = self.nomenclature_object.get_deployment_stack_name()
        lbd_request_processor_name = self.nomenclature_object.get_lbd_deployment_name()
        api_name = self.nomenclature_object.get_api_name()
        deployment_role_name = self.nomenclature_object.get_role_deployment_name()

        list_parameters = [
            {
                'ParameterKey': 'JobID',
                'ParameterValue': self.job_id
            },
            {
                'ParameterKey': 'Bucket',
                'ParameterValue': self.bucket
            },
            {
                'ParameterKey': 'LbdS3keyParameter',
                'ParameterValue': request_processor_s3_key
            },
            {
                'ParameterKey': 'ModelS3KeyParameter',
                'ParameterValue': self.model_s3_key
            },
            {
                'ParameterKey': 'InputModelTypeParameter',
                'ParameterValue': self.input_model_type
            },
            {
                'ParameterKey': 'DepFunctionName',
                'ParameterValue': lbd_request_processor_name
            },
            {
                'ParameterKey': 'Region',
                'ParameterValue': self.region
            },
            {
                'ParameterKey': 'ApiDeploymentName',
                'ParameterValue': api_name
            },
            {
                'ParameterKey': 'RoleDeploymentNameParameter',
                'ParameterValue': deployment_role_name
            }
        ]
        try:
            clf_client = boto3.client('cloudformation', aws_access_key_id=self.access_key_id,
                                      aws_secret_access_key=self.secret_access_key, region_name=self.region)

            stack_id = create_train_clf_stack(clf_client, deployment_stack_name, url_s3_stack_template, list_parameters)
            if invoke_mode==1:
                create_ressources_response = {}
                create_ressources_response['StackId'] = stack_id
                create_ressources_response['StackName'] = deployment_stack_name
                return create_ressources_response
            if invoke_mode==0:
                quit = True
                iter = 1
                while(quit):
                    time.sleep(2)
                    clf_stack_status = self.get_clf_stack_status(deployment_stack_name)
                    if clf_stack_status == 'CREATE_COMPLETE':
                        logging.info(f"[DEPLOYMENT]:statut creation CloudFormation: {clf_stack_status}")
                        return clf_stack_status
                    elif clf_stack_status == 'CREATE_IN_PROGRESS':
                        progress_bar(iter)
                        iter+=1
                    else:
                        logging.error(f"[DEPLOYMENT]:statut creation CloudFormation: {clf_stack_status}")
                        raise Exception("Creation stack CloudFormation echoué")

        except ClientError as cle:
            logging.error(f"[DEPLOYMENT]:creation ressources echouée!")
            raise Exception(cle)


    def get_clf_stack_status(self, stack_name):
        """
        :param stack_name: le nom de la stack CloudFormation
        :return: le status en cours
        """
        clf_client = boto3.client('cloudformation', aws_access_key_id=self.access_key_id,
                                  aws_secret_access_key=self.secret_access_key, region_name=self.region)

        try:
            clf_response = clf_client.describe_stacks(
                StackName=stack_name
            )
            return clf_response['Stacks'][0]['StackStatus']
        except ClientError as cle:
            logging.error(f"[DEPLOYMENT]:impossible d'obtenir le statut pour la stack: {stack_name}")
            raise Exception(cle)


    def deploy(self, prepare_env_response, invoke_mode=0):
        self.create_stack(prepare_env_response, invoke_mode=invoke_mode)
        return get_api_endpoint(self.job_id, self.access_key_id, self.secret_access_key, self.region)


