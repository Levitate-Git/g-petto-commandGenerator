# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\buttons.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_buttons(object):
    def setupUi(self, buttons):
        buttons.setObjectName("buttons")
        buttons.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(buttons.sizePolicy().hasHeightForWidth())
        buttons.setSizePolicy(sizePolicy)
        buttons.setMinimumSize(QtCore.QSize(800, 600))
        buttons.setMaximumSize(QtCore.QSize(800, 600))
        self.layoutWidget = QtWidgets.QWidget(buttons)
        self.layoutWidget.setGeometry(QtCore.QRect(640, 10, 151, 581))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_dur_label = QtWidgets.QLabel(self.layoutWidget)
        self.frame_dur_label.setObjectName("frame_dur_label")
        self.verticalLayout.addWidget(self.frame_dur_label)
        self.frame_dur_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.frame_dur_line.setObjectName("frame_dur_line")
        self.verticalLayout.addWidget(self.frame_dur_line)
        self.next_f_but = QtWidgets.QPushButton(self.layoutWidget)
        self.next_f_but.setObjectName("next_f_but")
        self.verticalLayout.addWidget(self.next_f_but)
        self.clear_f_but = QtWidgets.QPushButton(self.layoutWidget)
        self.clear_f_but.setObjectName("clear_f_but")
        self.verticalLayout.addWidget(self.clear_f_but)
        self.clear_all_but = QtWidgets.QPushButton(self.layoutWidget)
        self.clear_all_but.setObjectName("clear_all_but")
        self.verticalLayout.addWidget(self.clear_all_but)
        self.rth_but = QtWidgets.QPushButton(self.layoutWidget)
        self.rth_but.setObjectName("rth_but")
        self.verticalLayout.addWidget(self.rth_but)
        self.done_but = QtWidgets.QPushButton(self.layoutWidget)
        self.done_but.setObjectName("done_but")
        self.verticalLayout.addWidget(self.done_but)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.import_but = QtWidgets.QPushButton(self.layoutWidget)
        self.import_but.setObjectName("import_but")
        self.verticalLayout_2.addWidget(self.import_but)
        self.mot2_label = QtWidgets.QLabel(self.layoutWidget)
        self.mot2_label.setObjectName("mot2_label")
        self.verticalLayout_2.addWidget(self.mot2_label)
        self.mot2_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.mot2_line.setObjectName("mot2_line")
        self.verticalLayout_2.addWidget(self.mot2_line)
        self.mot3_label = QtWidgets.QLabel(self.layoutWidget)
        self.mot3_label.setObjectName("mot3_label")
        self.verticalLayout_2.addWidget(self.mot3_label)
        self.mot3_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.mot3_line.setObjectName("mot3_line")
        self.verticalLayout_2.addWidget(self.mot3_line)
        self.mot4_label = QtWidgets.QLabel(self.layoutWidget)
        self.mot4_label.setObjectName("mot4_label")
        self.verticalLayout_2.addWidget(self.mot4_label)
        self.mot4_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.mot4_line.setObjectName("mot4_line")
        self.verticalLayout_2.addWidget(self.mot4_line)
        self.height_label = QtWidgets.QLabel(self.layoutWidget)
        self.height_label.setObjectName("height_label")
        self.verticalLayout_2.addWidget(self.height_label)
        self.height_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.height_line.setText("")
        self.height_line.setObjectName("height_line")
        self.verticalLayout_2.addWidget(self.height_line)
        self.solo_duo_box = QtWidgets.QComboBox(self.layoutWidget)
        self.solo_duo_box.setObjectName("solo_duo_box")
        self.solo_duo_box.addItem("")
        self.solo_duo_box.addItem("")
        self.solo_duo_box.addItem("")
        self.solo_duo_box.addItem("")
        self.solo_duo_box.addItem("")
        self.verticalLayout_2.addWidget(self.solo_duo_box)
        self.draw_back_but = QtWidgets.QPushButton(self.layoutWidget)
        self.draw_back_but.setObjectName("draw_back_but")
        self.verticalLayout_2.addWidget(self.draw_back_but)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.status_label = QtWidgets.QLabel(self.layoutWidget)
        self.status_label.setObjectName("status_label")
        self.verticalLayout_3.addWidget(self.status_label)
        self.warn_label = QtWidgets.QLabel(self.layoutWidget)
        self.warn_label.setObjectName("warn_label")
        self.verticalLayout_3.addWidget(self.warn_label)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.retranslateUi(buttons)
        self.next_f_but.clicked.connect(buttons.next_frame)
        self.clear_f_but.clicked.connect(buttons.clear_frame)
        self.clear_all_but.clicked.connect(buttons.clear_all)
        self.rth_but.clicked.connect(buttons.rth_func)
        self.done_but.clicked.connect(buttons.done_func)
        self.draw_back_but.clicked.connect(buttons.draw_frame_background)
        self.import_but.clicked.connect(buttons.import_last_values)
        self.mot2_line.textEdited['QString'].connect(buttons.motor2_text_edit)
        self.mot3_line.textEdited['QString'].connect(buttons.motor3_text_edit)
        self.mot4_line.textEdited['QString'].connect(buttons.motor4_text_edit)
        self.height_line.textEdited['QString'].connect(buttons.height_text_edit)
        self.solo_duo_box.editTextChanged['QString'].connect(buttons.solo_duo_edit)
        self.frame_dur_line.editingFinished.connect(buttons.frame_dur_line_edit)
        QtCore.QMetaObject.connectSlotsByName(buttons)

    def retranslateUi(self, buttons):
        _translate = QtCore.QCoreApplication.translate
        buttons.setWindowTitle(_translate("buttons", "Form"))
        self.frame_dur_label.setText(_translate("buttons", "Frame Duration"))
        self.next_f_but.setText(_translate("buttons", "Next Frame"))
        self.clear_f_but.setText(_translate("buttons", "Clear Frame"))
        self.clear_all_but.setText(_translate("buttons", "Clear All"))
        self.rth_but.setText(_translate("buttons", "RTH"))
        self.done_but.setText(_translate("buttons", "Done"))
        self.import_but.setText(_translate("buttons", "Import Last Values"))
        self.mot2_label.setText(_translate("buttons", "Motor2 Dist"))
        self.mot3_label.setText(_translate("buttons", "Motor3 Dist"))
        self.mot4_label.setText(_translate("buttons", "Motor4 Dist"))
        self.height_label.setText(_translate("buttons", "Height"))
        self.solo_duo_box.setItemText(0, _translate("buttons", "Solo-Solo-Solo-Solo"))
        self.solo_duo_box.setItemText(1, _translate("buttons", "Solo-Solo-Duo"))
        self.solo_duo_box.setItemText(2, _translate("buttons", "Solo-Duo-Solo"))
        self.solo_duo_box.setItemText(3, _translate("buttons", "Duo-Solo-Solo"))
        self.solo_duo_box.setItemText(4, _translate("buttons", "Duo-Duo"))
        self.draw_back_but.setText(_translate("buttons", "Draw BackGround"))
        self.status_label.setText(_translate("buttons", "TextLabel"))
        self.warn_label.setText(_translate("buttons", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    buttons = QtWidgets.QWidget()
    ui = Ui_buttons()
    ui.setupUi(buttons)
    buttons.show()
    sys.exit(app.exec_())

