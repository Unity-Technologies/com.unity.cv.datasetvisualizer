import argparse
import os
import streamlit.bootstrap as bootstrap
from streamlit import config as _config
import pathlib

cli = argparse.ArgumentParser()
cli.add_argument('--data', type=str,
                 help='path to dataset', default="")


def preview(args):
    """Previews the dataset in a streamlit app."""
    dirname = pathlib.Path(os.path.dirname(__file__))
    filename = dirname / "Preview.py"

    data_arg = args.data if "data" in args else ""

    config = {
        "theme.primaryColor": "#7792E3",
        "theme.backgroundColor": "#273346",
        "theme.secondaryBackgroundColor": "#B9F1C0",
        "theme.textColor": "#FFFFFF",
        "theme.font": "sans serif"
    }

    for config_key in config.keys():
        _config.set_option(config_key, config[config_key], where_defined="unity_override")

    bootstrap.run(str(filename), "", [data_arg], {})


def main():
    preview(cli.parse_args())


if __name__ == "__main__":
    main()
