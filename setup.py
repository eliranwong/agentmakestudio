from setuptools import setup
import os, shutil

package = "agentmakestudio"
version="0.0.10"

# update version info
info_file = os.path.join(package, "version.txt") # package readme
with open(info_file, "w", encoding="utf-8") as fileObj:
    fileObj.write(version)

# update package readme
latest_readme = "README.md" # github repository readme
package_readme = os.path.join(package, "README.md") # package readme
shutil.copy(latest_readme, package_readme)
with open(package_readme, "r", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

# get required packages
install_requires = []
with open(os.path.join(package, "requirements.txt"), "r") as fileObj:
    for line in fileObj.readlines():
        mod = line.strip()
        if mod and not mod.startswith("#"):
            install_requires.append(mod)

# make sure config.py is empty
#open(os.path.join(package, "config.py"), "w").close()

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name="agentmakestudio",
    version=version,
    python_requires=">=3.8, <3.13",
    description="WebUI for AgentMake AI; AgentMake AI: a software developement kit for developing agentic AI applications that support 16 AI backends and work with 7 agentic components, such as tools and agents. (Developer: Eliran Wong)",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@toolmate.ai",
    packages=[
        package,
    ],
    package_data={
        package: ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    extras_require={
        'genai': ["google-genai>=1.1.0"],  # Dependencies for running Vertex AI
    },
    entry_points={
        "console_scripts": [
            f"agentmakestudio={package}.main:main",
        ],
    },
    keywords="agentmake mesop toolmate ai sdk anthropic azure chatgpt cohere deepseek genai github googleai groq llamacpp mistral ollama openai vertexai xai",
    url="https://github.com/eliranwong/agentmakestudio",
    project_urls={
        "Source": "https://github.com/eliranwong/agentmakestudio",
        "Tracker": "https://github.com/eliranwong/agentmakestudio/issues",
        "Documentation": "https://github.com/eliranwong/agentmakestudio/wiki",
        "Funding": "https://www.paypal.me/toolmate",
    },
    classifiers=[
        # Reference: https://pypi.org/classifiers/

        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
