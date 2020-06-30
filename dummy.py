import sys

from pytorch_wheel_installer.cli import entry_point

if __name__ == "__main__":
    sys.argv = [
        sys.argv[0],
        "-n",
        # "-b",
        # "cu101",
        "torch",
        "torchvision",
    ]
    entry_point()
