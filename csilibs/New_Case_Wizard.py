import sys
import os
import shutil
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWizard, QFileDialog
from PySide6 import QtCore, QtGui, QtWidgets
import json
from csilibs.utils import pathme, CaseDirMe
from csilibs.config import create_case_folder
from csilibs.assets import icons
import qdarktheme

class Ui_QWizard(object):
    def __init__(self):
        self.font = QtGui.QFont()
        self.font.setPointSize(8)

    def setupUi(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(684, 200)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icons.CSI_BLACK), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Wizard.setWindowIcon(icon)

        self.wizardPage1 = QtWidgets.QWizardPage()
        self.wizardPage1.setObjectName("wizardPage1")
        self.gridLayout = QtWidgets.QGridLayout(self.wizardPage1)
        self.gridLayout.setObjectName("gridLayout")
        
        self.headlabel = QtWidgets.QLabel("Starting a Case")
        self.headlabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QFont("Arial", 16, QFont.Bold) 
        self.headlabel.setFont(font)
        self.gridLayout.addWidget(self.headlabel,0, 0, 1, 5)
        
        
        self.create_label(self.gridLayout, "Case Name", 1, 0)
        self.lineEdit = self.create_line_edit(self.gridLayout, 1, 1, 1, 3)

        self.create_label(self.gridLayout, "Investigator Name", 2, 0)
        self.lineEdit_2 = self.create_line_edit(self.gridLayout, 2, 1, 1, 3)

        self.calendarWidget = QtWidgets.QCalendarWidget(self.wizardPage1)
        self.calendarWidget.setFont(self.font)  # Set the desired font and point size
        self.calendarWidget.setObjectName("calendarWidget")
        self.gridLayout.addWidget(self.calendarWidget, 1, 4, 5, 1)

        self.create_label(self.gridLayout, "Case Type", 3, 0)
        self.lineEdit_3 = self.create_line_edit(self.gridLayout, 3, 1, 1, 3)

        self.create_label(self.gridLayout, "Case Priority", 4, 0)
        self.priorityme = self.create_combobox(self.gridLayout, 4, 1, 1, 3, ["Informational", "Low", "Medium", "High", "Critical"])

        self.create_label(self.gridLayout, "Case Classification", 5, 0)
        self.classme = self.create_combobox(self.gridLayout, 5, 1, 1, 3, ["Sensitive But Unclassified // SBU", "Confidential // C", "For Official Use Only // FOUO", "Secret // S", "Top Secret // TS"])

        self.line = QtWidgets.QFrame(self.wizardPage1)

        Wizard.addPage(self.wizardPage1)

        self.retranslateUi(Wizard)
        self.setup_connections(Wizard)
        QtCore.QMetaObject.connectSlotsByName(Wizard)
        Wizard.setTabOrder(self.lineEdit, self.lineEdit_2)
        Wizard.setTabOrder(self.lineEdit_2, self.lineEdit_3)
        Wizard.setTabOrder(self.lineEdit_3, self.priorityme)
        Wizard.setTabOrder(self.priorityme, self.classme)
        Wizard.setTabOrder(self.classme, self.calendarWidget)

    def create_label(self, layout, text, row, column):
        label = QtWidgets.QLabel(self.wizardPage1)
        label.setTextFormat(QtCore.Qt.PlainText)
        label.setObjectName(f"label_{row}_{column}")
        label.setText(text)
        layout.addWidget(label, row, column, 1, 1)
        return label

    def create_line_edit(self, layout, row, column, rowspan, colspan):
        line_edit = QtWidgets.QLineEdit(self.wizardPage1)
        line_edit.setObjectName(f"lineEdit_{row}_{column}")
        layout.addWidget(line_edit, row, column, rowspan, colspan)
        return line_edit

    def create_combobox(self, layout, row, column, rowspan, colspan, items):
        combobox = QtWidgets.QComboBox(self.wizardPage1)
        combobox.setObjectName(f"combobox_{row}_{column}")
        combobox.addItems(items)
        layout.addWidget(combobox, row, column, rowspan, colspan)
        return combobox

    def retranslateUi(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "New Case Wizard"))

    def save_data(self):

        case_name = self.lineEdit.text()
    
        cdata = {
            "case_name": case_name,
            "investigator_name": self.lineEdit_2.text(),
            "case_type": self.lineEdit_3.text(),
            "case_priority": self.priorityme.currentText(),
            "case_classification": self.classme.currentText(),
            "case_date": self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        }
            
        case_directory = os.path.join(CaseDirMe().cases_folder, case_name)
        create_case_folder(case_directory)
        json_path = os.path.join(case_directory, "case_data.json")
        with open(json_path, 'w') as f:
            json.dump(cdata, f)
        print(case_directory)

    def setup_connections(self, wizard):
        wizard.button(QWizard.WizardButton.FinishButton).clicked.connect(self.save_data)
    
    
    def change_theme(self, mode):
        if mode == 'dark':
            os.environ['CSI_DARK'] = 'enable'
            qdarktheme.setup_theme()
        else:
            os.environ['CSI_DARK'] = 'disable'
            qdarktheme.setup_theme("light")

def load_data():
    global cases_folder    
    cases_folder = CaseDirMe().cases_folder
    
class CustomQWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)

class CustomGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(CustomGraphicsView, self).__init__(parent)
        self.setScene(QtWidgets.QGraphicsScene(self))

    # def mousePressEvent(self, event):
    #     if event.button() == QtCore.Qt.LeftButton:
    #         self.open_image()

    # def open_image(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.ReadOnly
    #     file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)

    #     if file_name:
    #         dest_path = pathme("assets/fingerprint.png")
    #         shutil.copyfile(file_name, dest_path)
    #         # Display the copied and scaled image in the QGraphicsView
    #         pixmap = QtGui.QPixmap(dest_path)
    #         scaled_pixmap = pixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    #         self.scene().clear()
    #         self.scene().addPixmap(scaled_pixmap)
    #         self.setScene(self.scene())

app = QApplication(sys.argv)
if os.environ.get("CSI_DARK") == 'disable':
    qdarktheme.setup_theme("light")
else:
    qdarktheme.setup_theme()

QWizard = CustomQWizard()
ui = Ui_QWizard()
ui.setupUi(QWizard)
load_data()
QWizard.show()
sys.exit(app.exec_())

