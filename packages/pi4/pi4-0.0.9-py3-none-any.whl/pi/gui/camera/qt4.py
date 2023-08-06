# \camera\pyqt4 install>pip install PyQt4-4.11.4-cp37-cp37m-win_amd64.whl

from PyQt4 import QtCore, QtGui
import cv2
from PIL import Image, ImageTk, ImageQt
import sys

cap = cv2.VideoCapture(0)

class CameraViewer(QtGui.QMainWindow):

    def __init__(self):

        super(CameraViewer, self).__init__()

        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setScaledContents(True)
        
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.setWindowTitle("Image Viewer")
        self.resize(640, 480)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.open)
        timer.start(50) #20 Hz

    def open(self):
        #get data and display

        cv2image= cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        
        # if not img: # img.isNull():
        #     QtGui.QMessageBox.information(self, "Image Viewer","Cannot load %s." % fileName)
        #     return

        pixmap = ImageQt.toqpixmap(img)

        self.imageLabel.setPixmap(pixmap) #( QtGui.QPixmap.fromImage(img) )
        self.imageLabel.adjustSize()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    camv = CameraViewer()
    camv.show()
    sys.exit(app.exec_())