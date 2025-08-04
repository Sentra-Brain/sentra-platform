from setuptools import setup, find_packages

setup(
    name="sentra-rag",
    version="0.1.0",
    description="RAG-specific logic: embeddings, vector store, chunking",
    author="Juan G Carmona",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "httpx",
        "pydantic",
        "pydantic-settings", 
        "python-dotenv",
    ],
    extras_require={
        "ml": [
            "sentence-transformers==5.0.0",
            "chromadb==1.0.15",
        ],
        "dev": [
            "pytest==8.4.1",
            "pytest-cov==6.2.1", 
            "pytest-mock==3.14.1",
            "pytest-asyncio==1.1.0",
            "debugpy==1.8.15",
        ],
    },
)