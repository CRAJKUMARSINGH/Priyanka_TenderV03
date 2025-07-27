from setuptools import setup, find_packages

setup(
    name="priyanka_tenderv03",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'streamlit>=1.32.0',
        'pandas>=2.0.0',
        'openpyxl>=3.1.0',
        'python-docx>=0.8.11',
        'python-dateutil>=2.8.2',
        'PyPDF2>=3.0.0',
        'reportlab>=4.0.0',
        'python-magic>=0.4.27',
        'python-magic-bin>=0.4.14; platform_system=="Windows"',
    ],
    entry_points={
        'console_scripts': [
            'priyanka-tender=app:main',
        ],
    },
    python_requires='>=3.8',
)
