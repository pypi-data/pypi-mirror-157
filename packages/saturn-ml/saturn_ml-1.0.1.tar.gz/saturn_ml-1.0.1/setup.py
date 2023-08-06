from setuptools import setup 
import pathlib


HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
setup(
  name="saturn_ml",
  version="1.0.1",
  description="This will do your repetitive tasks in AI / ML projets ",
  long_description=README,
  long_description_content_type="text/markdown",
  url = "https://github.com/loriscience/SaTurN_ML",
  author="Canberk Özkan",
  author_email="canberk.ozkann@gmail.com",
  license="MIT",
  packages=["saturn_ml"],
  zip_safe=False,
  include_package_data=True
)