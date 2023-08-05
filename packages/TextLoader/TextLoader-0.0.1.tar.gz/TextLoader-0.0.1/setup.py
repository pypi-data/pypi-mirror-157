import setuptools

with open("README.md", "r", encoding='utf-16') as fh:
    long_description = fh.read()

setuptools.setup(
    # 프로젝트 명을 입력합니다.
    name="TextLoader",

    # 프로젝트 버전을 입력합니다.
    version="0.0.1",

    # 프로젝트 담당자 혹은 작성자를 입력합니다.
    author="SoByungJun",
    author_email="so686so@gmail.com",

    # 프로젝트에 대한 간단한 설명을 입력합니다.
    description="Load text in any encoding and convert each line to a list",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # 홈페이지 주소를 입력합니다.
    url="https://github.com/so686so/TextLoader",

    # 기본 프로젝트 폴더 외에 추가로 입력할 폴더를 입력합니다.
    packages=setuptools.find_packages(exclude=['tests']),

    # 설치시 설치할 라이브러리를 지정합니다.
    install_requires=['chardet'],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)