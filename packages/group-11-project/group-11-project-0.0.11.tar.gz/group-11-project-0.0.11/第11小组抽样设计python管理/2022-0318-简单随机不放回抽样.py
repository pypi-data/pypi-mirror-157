import setuptools

setuptools.setup(
    name='group-11-python-project', #库的名字
    version='0.0.11',#库的版本号，后续更新的时候只需要改版本号
    author='lyyyyyyy',#名字
    author_email='liangying0354@163.com',#邮箱
    description='第11小组抽样设计',#介绍
    long_descroption_content_type='text/markdown',
    url='https://github.com/',
    packages=setuptools.find_packages(),
    cassifiers=[
        'Programming language:: Python ::3',
        'License :: OSI Approved :: MIT License',
        'OPerating System :: OS Independent'
    ],
)