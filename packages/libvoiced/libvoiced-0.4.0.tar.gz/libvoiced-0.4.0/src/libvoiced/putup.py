import logging
import subprocess


def putup(project_path):
    cmd = [
        "putup",
        "--pre-commit",
        "--venv",
        ".venv",
        f"{project_path.resolve()}",
    ]
    logging.debug(cmd)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        outs, errs = proc.communicate(timeout=15)
        logging.debug(outs.decode())
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        logging.warning(errs.decode())

    if errs:
        logging.warning(f"failed to run {' '.join(cmd)}, error: {errs.decode()}")
    else:
        logging.debug(f"ran ok: {' '.join(cmd)}")
