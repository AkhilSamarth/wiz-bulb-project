import argparse
import logging
import logging.handlers

import controller


LOGFILE = "logs/wiz-bulb-project.log"
LOGLEVEL = logging.INFO

logger = logging.getLogger(__name__)


def parse_args() -> dict:
    parser = argparse.ArgumentParser()

    parser.add_argument("--temp", type=int, help="temperature of bulbs, must provide brightness if this is included")
    parser.add_argument("--brightness", type=int, help="brightness of bulbs, must provide temp if this is included")
    parser.add_argument("--bulbs-off", action="store_true", help="turn bulbs off")
    parser.add_argument("--bulbs-on", action="store_true", help="turns bulbs on")
    parser.add_argument("--auto-set", action="store_true", help="automatically determine correct options based on current time and config")

    return vars(parser.parse_args())


def config_log():
    logging.basicConfig(
        handlers=[
            logging.handlers.TimedRotatingFileHandler(
                filename=LOGFILE,
                when="midnight",
                backupCount=3
            )
        ],
        level=LOGLEVEL,
        format="[%(asctime)s] %(levelname)s - %(filename)s:%(lineno)s :: %(message)s"
    )


def main():
    args = parse_args()
    config_log()

    logger.info(f"Starting program with args: {args}")

    if args["bulbs_off"]:
        controller.set_state(False)
    elif args["bulbs_on"]:
        controller.set_state(True)
    elif args["temp"] and args["brightness"]:
        controller.set_temp_and_brightness(temp=args["temp"], brightness=args["brightness"])
    elif args["auto_set"]:
        controller.set_bulb_based_on_timeline()


if __name__ == "__main__":
    main()
