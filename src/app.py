import argparse
import logging

from bydle.gui import Application, MainFrame

parser = argparse.ArgumentParser()
parser.add_argument(
    "--log", help="display log messages in the console", action="store_true"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.log:
        logging.basicConfig(level=logging.INFO)
    app = Application()
    MainFrame(app)
    app.mainloop()
