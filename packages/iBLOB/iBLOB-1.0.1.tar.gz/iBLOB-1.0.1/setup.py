from setuptools import setup

setup(name='iBLOB',
      version='1.0.1',
      description='Convert any file to/from binary format',
      long_description="""
      Demo:
      driver = iBLOB()
      blob = driver.convert_to_blob('file_name.jpg')
      print(blob)
      driver.convert_from_blob(blob, 'png')
      """,
      author='Eden Dadon',
      packages=['iBLOB'],
      zip_safe=False)
