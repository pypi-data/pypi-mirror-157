import setuptools

setuptools.setup(
     name='reel44',  
     version='1.0.1',
     author="Keshri-InfoTech",
     author_email="keshrinfotech@gmail.com",
     description="A Python Encryption Library BY-Keshri-InfoTech",
     long_description='''
     A Python Password and Important Textual Based Encryption Library Made For A Fast, Secure and Reliable Encryption.
     This Library Uses A Custom Algorightim Made By Us. It Can Be Used As A Trusted Encryption Library.
     We Also Provide Premium Version Of The Library. To Get That Contact Us On Our Email-Id.
     ''',
   long_description_content_type="text/markdown",
   install_requires=[
        'pyjwt'
    ],
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )