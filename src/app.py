import logging

from bydle.gui import Application, MainFrame

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = Application()
    MainFrame(app)
    app.mainloop()
