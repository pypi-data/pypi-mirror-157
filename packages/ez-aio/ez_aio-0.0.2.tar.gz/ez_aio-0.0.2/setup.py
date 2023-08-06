from setuptools import setup

with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
   name='ez_aio',
   version='0.0.2',
   description='Easiest way to make tons of get/post requests with aiohttp.',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='E',
   author_email='18771051812@qq.com',
   url="https://www.github.com/wangyi041228/ez_aio",
   packages=['ez_aio'],
   install_requires=['aiohttp'],
   scripts=[]
)
