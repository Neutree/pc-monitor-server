from setuptools import setup

requirements = [
    "Flask",
    "pynvml"
]
requirements_win = [
    "wmi",
    "pythonnet"
]
requirements_unix = requirements

setup(
    name="pc_monitor",
    version="1.0.0",
    install_requires=[
        "Flask",  # This is a common requirement for all platforms
    ],
    extras_require={
        ':sys_platform == "win32"': requirements_win,
        ':sys_platform == "linux"': requirements_unix,
        # You can add more platform-specific requirements here
    },
)

