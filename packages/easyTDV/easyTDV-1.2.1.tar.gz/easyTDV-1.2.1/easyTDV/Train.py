import boto3, logging, time, json
from botocore.exceptions import ClientError
from easyTDV.TrainNomenclature import *
from easyTDV.train_helper import generate_job_id, upload_file_to_s3, create_train_clf_stack, progress_bar, get_train_ec2_instance_status, run_ec2_command, get_command_status, terminate_instance, delete_clf_stack
from pathlib import Path


"""
Classe pyhton pour la création des ressources AWS d'entrainement via une pile CloudFormation
Les ressources créées sont: 
        * pile CloudFormation
        * roles IAM
        * InstanceProfil
        * Lambda
        * EC2
offre plusieurs methodes de classe :
        * prepare_env()
        * create_clf_stack()
        * get_clf_stack_status()
        * lunch_train_ec2()
        * install_requerments()
        * lunch_train_script()
        * delete_ressources()
"""
class Train:
    dir = Path(__file__).parent
    template_stack_local_path = (dir / "resources/clf_train_stack.json").__str__()
    train_lbd_local_path = (dir / "resources/lambda_train.zip").__str__()
    
    def __init__(self,
                     bucket,
                     auth_object,
                     train_script_local_path,
                     requirements_local_path,
                     instance_type,
                     device_size,
                     ami = "ami-0d9858aa3c6322f73",
                     region = "us-west-1"
                     ):
        self.bucket = bucket
        self.train_script_local_path = train_script_local_path
        self.requirements_local_path = requirements_local_path
        self.instance_type = instance_type
        self.ami = ami
        self.device_size = device_size
        self.region = region
        self.access_key_id = auth_object.secret_key_id
        self.secret_access_key = auth_object.secret_access_key
        self.job_id = generate_job_id()
        self.nomenclature_object = TrainNomenclature(self.job_id, self.bucket, self.region)


    def prepare_env(self):
        """
            charger les fichiers suivants vers S3:
                        * train.py : script d'entrainement
                        * requirements.txt : fichier contanant les lib necessaires pour l'execution de <train.py>
                        * stack_template.json : template CloudFormation pour les ressources d'entrainement
                        * lbd_train.py vers S3 : code source de la lambda d'entrainement
            :return: dict
                        les keys S3 des fichiers chargés vers S3
            génère une exception en cas d'échec de chargement des fichiers vers s3
        """
        s3_client = boto3.client('s3', aws_access_key_id=self.access_key_id,
                                 aws_secret_access_key=self.secret_access_key, region_name=self.region)
        s3_lbd_location = self.nomenclature_object.get_s3_lbd_location()
        s3_train_script_location = self.nomenclature_object.get_s3_train_script_location()
        s3_requirements_location = self.nomenclature_object.get_s3_requirements_location()
        s3_stack_template_location = self.nomenclature_object.get_s3_stack_template_location()
        try:
            upload_file_to_s3(s3_client, self.train_lbd_local_path, self.bucket, s3_lbd_location)
            upload_file_to_s3(s3_client, self.train_script_local_path, self.bucket, s3_train_script_location)
            upload_file_to_s3(s3_client, self.requirements_local_path, self.bucket, s3_requirements_location)
            upload_file_to_s3(s3_client, self.template_stack_local_path, self.bucket, s3_stack_template_location["s3_key"])
        except ClientError as cle:
            logging.error("[TRAIN]:preparation d'enveronement echouée...")
            raise Exception(cle)
        return {
            "s3_lbd_key": s3_lbd_location,
            "s3_train_script_key": s3_train_script_location,
            "s3_requirements_key": s3_requirements_location,
            "url_s3_stack_template": s3_stack_template_location["s3_url"]
        }


    def create_clf_stack(self, prepare_env_response, invoke_mode=0):
        """
            :param prepare_env_response: l'objet retourné par prepare_env()
            :param invoke_mode : mode d'invocation [0:synchrone, 1: asynchrone]
            :return: dict
                    * stack_id: ID de la stack créée pour les appels synchrones
                    * stack_status : le statut de la création de la stack pour les appels asynchrones
            génère une exception en cas d'échec de création de la pile CloudFormation
        """
        if invoke_mode not in [0, 1]:
            raise Exception("valeurs acceptées pour invoke_mode: [0:synchrone, 1: asynchrone]")
        s3_lbd_key = prepare_env_response["s3_lbd_key"]
        s3_train_script_key = prepare_env_response["s3_train_script_key"]
        s3_requirements_key = prepare_env_response["s3_requirements_key"]
        url_s3_stack_template = prepare_env_response["url_s3_stack_template"]

        stack_name = self.nomenclature_object.get_train_stack_name()
        lbd_train_name = self.nomenclature_object.get_lbd_train_name()
        role_train_name = self.nomenclature_object.get_role_train_name()
        profil_iam_name = self.nomenclature_object.get_profil_iam_name()

        list_parameters = [
            {
                'ParameterKey': 'JobID',
                'ParameterValue': self.job_id
            },
            {
                'ParameterKey': 'LbdTrainNameParameter',
                'ParameterValue': lbd_train_name
            },
            {
                'ParameterKey': 'InstanceProfilNameParameter',
                'ParameterValue': profil_iam_name
            },
            {
                'ParameterKey': 'RoleTrainNameParameter',
                'ParameterValue': role_train_name
            },
            {
                'ParameterKey': 'S3BucketParameter',
                'ParameterValue': self.bucket
            },
            {
                'ParameterKey': 'S3KeyParameter',
                'ParameterValue': s3_lbd_key
            },
            {
                'ParameterKey': 'InstanceTypeParameter',
                'ParameterValue': self.instance_type
            },
            {
                'ParameterKey': 'AmiParameter',
                'ParameterValue': self.ami
            },
            {
                'ParameterKey': 'regionParameter',
                'ParameterValue': self.region
            },
            {
                'ParameterKey': 'TrainScriptKeyParameter',
                'ParameterValue': s3_train_script_key
            },
            {
                'ParameterKey': 'RequirementScriptKeyParameter',
                'ParameterValue': s3_requirements_key
            },
            {
                'ParameterKey': 'DeviceSizeParameter',
                'ParameterValue': self.device_size
            }
        ]
        try:
            clf_client = boto3.client('cloudformation', aws_access_key_id=self.access_key_id,
                                      aws_secret_access_key=self.secret_access_key, region_name=self.region)
            stack_id = create_train_clf_stack(clf_client, stack_name, url_s3_stack_template, list_parameters)
            if invoke_mode==0:
                quit = True
                iter = 1
                while(quit):
                    time.sleep(2)
                    clf_stack_status = self.get_clf_stack_status(stack_name)
                    if clf_stack_status == 'CREATE_COMPLETE':
                        logging.info(f"[TRAIN]:statut creation CloudFormation: {clf_stack_status}")
                        return clf_stack_status
                    elif clf_stack_status == 'CREATE_IN_PROGRESS':
                        progress_bar(iter, "Création stack...")
                        iter+=1
                    else:
                        logging.error(f"[TRAIN]:statut creation CloudFormation: {clf_stack_status}")
                        raise Exception("[TRAIN]:Creation stack CloudFormation echoué")
            if invoke_mode==1:
                create_ressources_response = {}
                create_ressources_response['StackId'] = stack_id
                create_ressources_response['StackName'] = stack_name
                return create_ressources_response
        except ClientError as cle:
            logging.error(f"[TRAIN]:creation ressources echouée!")
            raise Exception(cle)


    def get_clf_stack_status(self, stack_name):
        """
        :param stack_name: le nom de la stack CloudFormation
        :return: str
                    le status en cours de la stack <stack_name>
        génère une exception en cas d'échec à l'appel <boto3.client.describe_stacks()>
        """
        clf_client = boto3.client('cloudformation', aws_access_key_id=self.access_key_id,
                                  aws_secret_access_key=self.secret_access_key, region_name=self.region)
        try:
            clf_response = clf_client.describe_stacks(
                StackName=stack_name
            )
            return clf_response['Stacks'][0]['StackStatus']
        except ClientError as cle:
            logging.error(f"[TRAIN]:impossible d'obtenir le statut pour la stack: {stack_name}")
            raise Exception(cle)


    def lunch_train_ec2(self, invoke_mode=0):
        """
            :param invoke_mode : mode d'invocation [0:synchrone, 1: asynchrone]
            :return: str
                        l'id unique de l'instance d'entrainement si le lancement de l'ec2 est OK
            excecute la lambda de création d'instance d'entraienemt et configure la VM
            génère une exception en cas où la création de l'instance est KO
        """
        if invoke_mode not in [0, 1]:
            raise Exception("valeurs acceptées pour invoke_mode: [0:synchrone, 1: asynchrone]")

        lbd_client = boto3.client('lambda', aws_access_key_id=self.access_key_id,
                                  aws_secret_access_key=self.secret_access_key, region_name=self.region)
        lbd_train_name = self.nomenclature_object.get_lbd_train_name()
        try:
            invoke_lbd_response = lbd_client.invoke(
                FunctionName=lbd_train_name,
                InvocationType='RequestResponse'
            )
            instance_id = json.loads(invoke_lbd_response['Payload'].read())["instance_id"]
            if invoke_mode == 1:
                return instance_id
            if invoke_mode == 0:
                iter=1
                while(True):
                    time.sleep(2)
                    instance_status = get_train_ec2_instance_status(instance_id, self.access_key_id, self.secret_access_key, self.region)
                    if instance_status == 'running':
                        return instance_id
                    elif instance_status == 'pending':
                        progress_bar(iter, "Lancement EC2...")
                        iter+=1
                    else:
                        raise Exception(f"status de l'instance d'entrainement en erreur : {instance_status}")
        except ClientError as cle:
            logging.error("impossible de lancer l'instance d'entrainement!")
            raise Exception(cle)


    def install_requerments(self, instance_id, invoke_mode=0):
        """
                :param invoke_mode : mode d'invocation [0:synchrone, 1: asynchrone]
                :return: str
                            l'id unique de la commande SSM lancée sur l'instance d'entraiment
                Installe les lib necessaires pour l'entrainement du modèle
                génère une exception dans le cas où la commande est KO
        """
        if invoke_mode not in [0, 1]:
            raise Exception("valeurs acceptées pour invoke_mode: [0:synchrone, 1: asynchrone]")
        requirements_file_name = "requirements.txt"
        commands = [f"pip3.8 install -r /appli/{requirements_file_name}"]
        cmd_exec_response = run_ec2_command(instance_id, commands, self.access_key_id, self.secret_access_key,
                                            self.region)
        if invoke_mode == 1:
            return cmd_exec_response
        command_id = cmd_exec_response['Command']['CommandId']
        iter = 0
        while(True):
            time.sleep(2)
            cmd_status = get_command_status(instance_id, command_id, self.access_key_id, self.secret_access_key, self.region)
            if cmd_status["status"] == "Success":
                return cmd_status
            if cmd_status["status"] in ['Pending', 'InProgress', 'Delayed']:
                progress_bar(iter, "Installation requirements...")
                iter+=1
                continue
            logging.error("l'installation des librairies a echoué...")
            raise Exception(cmd_status["status_details"])


    def lunch_train_script(self, instance_id, invoke_mode=0):
        """
                excecute le script d'entrainement dans la machine d'id : <instance_id>
                :param invoke_mode : mode d'invocation [0:synchrone, 1: asynchrone]
                :param instance_id: l'id unique de l'instance d'entrainement
                :return: str
                            le status d'execution du script d'entrainement
                génère une exception en cas où l'entrainement est KO
        """
        if invoke_mode not in [0, 1]:
            raise Exception("valeurs acceptées pour invoke_mode: [0:synchrone, 1: asynchrone]")

        train_script_name = "train_script.py"
        commands = [f"sudo python3.8 /appli/{train_script_name}"]
        cmd_exec_response = run_ec2_command(instance_id, commands, self.access_key_id, self.secret_access_key,
                                            self.region)

        if invoke_mode == 1:
            return cmd_exec_response
        command_id = cmd_exec_response['Command']['CommandId']
        iter = 0
        while (True):
            time.sleep(2)
            cmd_status = get_command_status(instance_id, command_id, self.access_key_id, self.secret_access_key,
                                            self.region)
            if cmd_status["status"] == "Success":
                return cmd_status
            if cmd_status["status"] in ['Pending', 'InProgress', 'Delayed']:
                progress_bar(iter, "Entrainement modèle...")
                iter += 1
                continue
            logging.error("l'execution du script d'entrainemet a echoué...")
            raise Exception(cmd_status["status_details"])



    def delete_resources(self, instance_id):
        """
        :param instance_id: l'id unique de l'instance d'entrainement
            * supprimer la stack CloudFormation
            * Resilier l'instance d'entrainement à la fin du process
        :return None
        """
        stack_name = self.nomenclature_object.get_train_stack_name()
        terminate_instance(instance_id, self.access_key_id, self.secret_access_key, self.region)
        delete_clf_stack(stack_name, self.access_key_id, self.secret_access_key, self.region)





