from setuptools import find_packages, setup


setup(
    name="codex-evidence-rag",
    version="0.1.0",
    description="Codex-compatible local RAG evidence and resume-claim auditor.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Zhane Grey",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.10",
    entry_points={"console_scripts": ["codex-evidence=codex_evidence_rag.cli:main"]},
)
