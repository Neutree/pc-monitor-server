from setuptools import setup, find_packages

requirements = [
    "Flask",
    "pynvml",
    "qrcode"
]
requirements_win = [
    "wmi",
    "pythonnet"
]
requirements_unix = requirements

with open("pc_monitor_server/version.py", "r", encoding="utf-8") as f:
    vars = {}
    exec(f.read(), vars)
    __version__ = vars["__version__"]

setup(
    name = "pc-monitor-server",
    version = __version__,
    author = 'Neucrack',
    license='MIT',
    url='https://github.com/Neutree/pc-monitor',
    packages = find_packages(),
    install_requires = requirements,
    extras_require={
        ':sys_platform == "win32"': requirements_win,
        ':sys_platform == "linux"': requirements_unix,
        # You can add more platform-specific requirements here
    },
    entry_points={
        'console_scripts': [
            'pc-monitor-server=pc_monitor_server.main:main_cli',
        ],
        # 'gui_scripts': [
        # ],
    }
)

