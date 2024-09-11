from logic import *


def main():
    application = QApplication([])
    application.setStyle('Fusion')
    # QApplication::setStyle()
    window = Logic()
    window.show()
    application.exec()


if __name__ == '__main__':
    main()
