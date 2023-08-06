from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = 'The package below creates a folder structure accepted by heroku for deployments. https://github.com/DK-denno/Flask-CLI-README'

setup(
        name ='dkFlaskStructure',
        version ='1.0.1',
        author ='Kamau Dennis Kihiu',
        author_email ='kamaukihiudennis@gmail.com',
        url ='https://github.com/DK-denno/Flask-CLI-README',
        description ='This is a package to create the flask folder structure used to deploy to heroku.',
        long_description = long_description,
        long_description_content_type ="text/markdown",
        license ='MIT',
        packages = find_packages(),
        entry_points ={
            'console_scripts': [
                'dkFlask = dkFlaskStructure.run:main'
            ]
        },
        classifiers =[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        keywords ='flask Structure, Flask, dkFlask',
        install_requires = requirements,
        zip_safe = False
)