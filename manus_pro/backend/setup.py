# FILE: setup.py
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ملف setup.py لحزمة manus_pro_server                      ║
║                                                                              ║
║  الوصف:                                                                     ║
║  - يسمح بتثبيت manus_pro_server كحزمة Python                               ║
║  - يمكن استخدامه مع pip install -e .                                       ║
║  - يحل مشكلة ModuleNotFoundError                                            ║
║                                                                              ║
║  التاريخ: ديسمبر 2025                                                       ║
║  الإصدار: 2.0                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from setuptools import setup, find_packages
from pathlib import Path

# قراءة محتوى README
readme_file = Path(__file__).parent.parent.parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# قراءة المتطلبات
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="manus_pro_server",
    ,
    description="خادم mkh_Manus المحسّن - نظام إدارة المهام والوكلاء الذكية",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="mkh_Manus Team",
    author_email="support@example.com",
    url="https://github.com/your-org/mkh_Manus",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "pylint>=2.17.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "manus-server=manus_pro_server.api:main",
            "manus-worker=manus_pro_server.worker:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="manus ai agent task automation llm",
    project_urls={
        "Bug Reports": "https://github.com/your-org/mkh_Manus/issues",
        "Source": "https://github.com/your-org/mkh_Manus",
        "Documentation": "https://mkh-manus.example.com/docs",
    },
)
