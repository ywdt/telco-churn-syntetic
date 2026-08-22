"""
Python 3.14+ compatibility patch for Hydra 1.3.
Fixes argparse LazyCompletionHelp container check in Python 3.14+.
"""
import sys

def apply_hydra_patch():
    try:
        import hydra._internal.utils as hydra_utils
        import hydra.main as hydra_main
        from hydra import __version__
        import argparse

        def _patched_get_args_parser() -> argparse.ArgumentParser:
            parser = argparse.ArgumentParser(add_help=False, description="Hydra")
            parser.add_argument("--help", "-h", action="store_true", help="Application's help")
            parser.add_argument("--hydra-help", action="store_true", help="Hydra's help")
            parser.add_argument(
                "--version",
                action="version",
                help="Show Hydra's version and exit",
                version=f"Hydra {__version__}",
            )
            parser.add_argument(
                "overrides",
                nargs="*",
                help="Any key=value arguments to override config values (use dots for.nested=overrides)",
            )
            parser.add_argument(
                "--cfg",
                "-c",
                choices=["job", "hydra", "all"],
                help="Show config instead of running [job|hydra|all]",
            )
            parser.add_argument(
                "--resolve",
                action="store_true",
                help="Used in conjunction with --cfg, resolve config interpolations before printing.",
            )
            parser.add_argument("--package", "-p", help="Config package to show")
            parser.add_argument("--run", "-r", action="store_true", help="Run a job")
            parser.add_argument(
                "--multirun",
                "-m",
                action="store_true",
                help="Run multiple jobs with the configured launcher and sweeper",
            )
            parser.add_argument(
                "--shell-completion",
                "-sc",
                action="store_true",
                help="Install or Uninstall shell completion",
            )
            parser.add_argument(
                "--config-path",
                "-cp",
                help="""Overrides the config_path specified in hydra.main().
                            The config_path is absolute or relative to the Python file declaring @hydra.main()""",
            )
            parser.add_argument(
                "--config-name",
                "-cn",
                help="Overrides the config_name specified in hydra.main()",
            )
            parser.add_argument(
                "--config-dir",
                "-cd",
                help="Adds an additional config dir to the config search path",
            )
            parser.add_argument(
                "--experimental-rerun",
                help="Rerun a job from a previous config pickle",
            )
            info_choices = [
                "all",
                "config",
                "defaults",
                "defaults-tree",
                "plugins",
                "searchpath",
            ]
            parser.add_argument(
                "--info",
                "-i",
                const="all",
                nargs="?",
                action="store",
                choices=info_choices,
                help=f"Print Hydra information [{'|'.join(info_choices)}]",
            )
            return parser

        hydra_utils.get_args_parser = _patched_get_args_parser
        if "hydra.main" in sys.modules:
            sys.modules["hydra.main"].__dict__["get_args_parser"] = _patched_get_args_parser
    except Exception:
        pass

apply_hydra_patch()
