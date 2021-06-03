
from PyQt5 import QtCore, QtGui, QtWidgets


def main():
    import sys

    app = QtWidgets.QApplication(sys.argv)

    label = QtWidgets.QPushButton("Stack Overflow")

    graphicsview = QtWidgets.QGraphicsView()
    scene = QtWidgets.QGraphicsScene(graphicsview)
    graphicsview.setScene(scene)

    proxy = QtWidgets.QGraphicsProxyWidget()
    proxy.setWidget(label)
    proxy.setTransformOriginPoint(proxy.boundingRect().center())
    scene.addItem(proxy)
    proxy.setRotation(360)

    slider = QtWidgets.QSlider(minimum=0, maximum=360, orientation=QtCore.Qt.Horizontal)
    #slider.valueChanged.connect(proxy.setRotation)

    label_text = QtWidgets.QLabel(
        "{}°".format(slider.value()), alignment=QtCore.Qt.AlignCenter
    )
    slider.valueChanged.connect(
        lambda value: label_text.setText("{}°".format(slider.value()))
    )

   # slider.setValue(45)

    w = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(w)
    lay.addWidget(graphicsview)
    lay.addWidget(slider)
    lay.addWidget(label_text)
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()