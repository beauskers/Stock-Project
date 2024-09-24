from logic import *


def main():
    application = QApplication([])
    application.setStyle('Fusion')
    window = Logic()
    window.show()
    application.exec()


if __name__ == '__main__':
    main()
