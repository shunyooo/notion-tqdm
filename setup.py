from setuptools import setup

readme = ""
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="notion-tqdm",
    python_requires=">=3.6",
    version="0.3.0",
    description="Progress Bar displayed in Notion like tqdm for Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=["progress", "tqdm", "notion"],
    author="shunyooo",
    author_email="shunyo.kawamoto@gmail.com",
    license="MIT License",
    packages=["notion_tqdm/",],
    url="https://github.com/shunyooo/notion-tqdm",
    install_requires=["tqdm", "notion @ git+https://github.com/shunyooo/notion-py.git"],
)
