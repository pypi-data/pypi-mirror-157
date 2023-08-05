from setuptools import setup, find_packages, glob


VERSION = '1.1.6'
DESCRIPTION = "easyTDV: Train, Deploy and Vizualisation"
LONG_DESCRIPTION = "Framwork pour l'entrainement, deploiement et la visualisation à temps réel des modèles ML sur AWS"

# Setting up
setup(
    name="easyTDV",
    version=VERSION,
    author="HADJALI Lounas",
    author_email="<hadjalilounas@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['boto3', 'pandas'],
    keywords=['python', 'ML', 'Deployment', 'Train', 'AWS'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ], 
    package_data={'easyTDV': ['resources/clf_deployment_stack.json', 'resources/clf_train_stack.json', 'resources/lambda_deployment.zip', 'resources/lambda_train.zip']},
    include_package_data=True
)