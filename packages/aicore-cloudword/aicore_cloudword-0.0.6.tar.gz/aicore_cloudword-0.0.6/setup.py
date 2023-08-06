import setuptools

setuptools.setup(
    name="aicore_cloudword",
    version="0.0.6",
    author="Ivan Ying",
    author_email="ivan@theaicore.com",
    description="A simple package to generate wordclouds from Google Sheets",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
          'wordcloud',
          'pandas',
          'numpy',
          'gspread',
          'oauth2client',
          'PyYaml']
)