import ast, json,os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QErrorMessage,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget
)
import copyPaste

class UserSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.basedir = os.path.dirname(__file__)
        data_filename = os.path.join(self.basedir, "keys.json")
        if not os.path.exists(data_filename):
            with open(data_filename, 'w') as d:
                json.dump({}, d)

        self.users = self.loadData("keys.json").keys()
        self.user = ''
        self.address_book = ''

        self.setWindowTitle("Select username")
        self.setWindowIcon(QIcon(os.path.join(self.basedir, "images/users.png")))
        self.setFixedSize(250, 300)
        self.setStyleSheet("font-size: 14px;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        dropdown_label = QLabel("Select username: ")
        dropdown_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.users_dropdown = QComboBox()
        self.users_dropdown.addItems(self.users)
        self.users_dropdown.setMinimumWidth(200)
        self.users_dropdown.setMaximumWidth(200)

        spacer_label = QLabel("OR")

        # Define widgets needed for the option to create a new database
        create_label = QLabel("Register new user: ")
        create_layout = QHBoxLayout()
        self.checkbox = QCheckBox("")
        self.text_field = QLineEdit()
        self.text_field.setStyleSheet('background-color: #E0E0E0; color: #808080;')
        self.text_field.setReadOnly(True)
        self.text_field.setPlaceholderText("Enter your username")
        self.text_field.setMinimumWidth(200)
        self.text_field.setMaximumWidth(200)
        create_layout.addWidget(self.checkbox)
        create_layout.addWidget(self.text_field)

        # Define the submit button
        self.submit_button = QPushButton("OK", self)
        self.submit_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.submit_button.clicked.connect(self.getData)
        self.submit_button.clicked.connect(self.accept)

        # Add the widgets to the layout
        main_layout.addWidget(dropdown_label)
        main_layout.addWidget(self.users_dropdown)
        main_layout.addStretch(1)
        main_layout.addWidget(spacer_label)
        main_layout.addStretch(1)
        main_layout.addWidget(create_label)
        main_layout.addLayout(create_layout)
        main_layout.addStretch(1)
        main_layout.addWidget(self.submit_button)

        # checkbox signal to toggle editability
        self.checkbox.stateChanged.connect(lambda state: self.toggleEditable(state, self.text_field))

        # Error message dialog
        self.error_dialog = QErrorMessage(self)

    def loadData(self, document):
        try:
            with open(document, "r") as f:
                data = json.load(f)
            return data
        except Exception:
            print("Error while loading data")
            pass

    def toggleEditable(self, state, text_field):
        if state:
            text_field.setStyleSheet('')
            text_field.setReadOnly(False)
        else:
            text_field.setStyleSheet('background-color: #E0E0E0; color: #808080;')

    def getData(self):
        if self.checkbox.isChecked():
            self.user = self.text_field.text()
        else:
            self.user = self.users_dropdown.currentText()

        self.address_book = f"{self.user}s_address_book.json"

class showPubKeyDialog(QDialog):
    def __init__(self, user, public_key):
        super().__init__()

        self.basedir = os.path.dirname(__file__)
        self.user = user

        self.setWindowTitle("Share your public key")
        self.setWindowIcon(QIcon(os.path.join(self.basedir, "images/share.png")))
        self.setFixedSize(400, 400)

        keystring = "['" + public_key[0] + "', '" + public_key[1] + "']"

        main_layout = QVBoxLayout()
        title = QLabel("Your public key is: ")
        self.content = QTextEdit()
        self.content.setText(keystring)
        self.content.setReadOnly(True)
        buttons_layout = QHBoxLayout()
        copy_button = QPushButton(" Copy")
        copy_button.setFixedWidth(90)
        copy_button.setStyleSheet("font-size:11pt")
        copy_button.setIcon(QIcon(os.path.join(self.basedir, "images/document-copy.png")))
        copy_button.clicked.connect(self.copy)
        save_button = QPushButton(" Save")
        save_button.setFixedWidth(90)
        save_button.setStyleSheet("font-size:11pt")
        save_button.setIcon(QIcon(os.path.join(self.basedir, "images/disk.png")))
        save_button.clicked.connect(self.write)
        done_button = QPushButton("Done")
        done_button.setFixedWidth(90)
        done_button.setStyleSheet("font-size:11pt")
        done_button.clicked.connect(self.accept)
        buttons_layout.addWidget(copy_button)
        buttons_layout.addWidget(save_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(done_button)
        main_layout.addWidget(title)
        main_layout.addWidget(self.content)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def copy(self):
        copyPaste.copy(self.content.toPlainText())

    def write(self):
        #filename = f"{self.user}s_pubkey.txt"
        #file = os.path.join(self.basedir, filename)
        FILE_FILTERS = ["Text files (*.txt)"]
        caption = ""
        initial_dir = ""
        filters = ";;".join(FILE_FILTERS)  # this is the format of the argument required by the save file dialog
        file, selected_filter = QFileDialog.getSaveFileName(
            self,
            caption=caption,
            directory=initial_dir,
            filter=filters,
        )
        content = f"This public key is a list or array containing two large integers stored as strings.\n\n"
        content += "Here is {self.user}'s public key:\n\n"
        content += self.content.toPlainText()
        try:
            with open(file, "w") as f:
                f.write(content)
        except Exception as e:
            print(e)


class addAddresseeDialog(QDialog):
    def __init__(self, address_book, address_book_filename):
        super().__init__()

        self.basedir = os.path.dirname(__file__)
        self.address_book = address_book
        self.address_book_filename = address_book_filename
        self.new_addressee = ""

        self.setWindowTitle("Add an addressee")
        self.setWindowIcon(QIcon(os.path.join(self.basedir, "images/plus-button.png")))
        self.setFixedSize(400, 400)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        name_label = QLabel("Name: ")
        self.name_field = QLineEdit()
        pubkey_label = QLabel("Public Key: ")
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText(
            f"Paste the addressee's public key here.\n\nThe key pair must be formatted as a list of two strings delimited by a comma and enclosed in square brackets."
        )
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(90)
        cancel_button.setStyleSheet("font-size:11pt;")
        cancel_button.clicked.connect(self.reject)
        paste_button = QPushButton(" Paste")
        paste_button.setFixedWidth(90)
        paste_button.setStyleSheet("font-size:11pt;")
        paste_button.setIcon(QIcon(os.path.join(self.basedir, "images/clipboard-list.png")))
        paste_button.clicked.connect(self.paste)
        add_button = QPushButton("Add")
        add_button.setFixedWidth(90)
        add_button.setStyleSheet("font-size:11pt;")
        add_button.clicked.connect(self.addAddressee)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(paste_button)
        buttons_layout.addWidget(add_button)

        main_layout.addWidget(name_label)
        main_layout.addWidget(self.name_field)
        main_layout.addWidget(pubkey_label)
        main_layout.addWidget(self.input_field)
        main_layout.addLayout(buttons_layout)

    def addAddressee(self):
        new_addressee_name = self.name_field.text()
        new_addressee_pubkey = self.input_field.toPlainText()
        new_addressee_pubkey = ast.literal_eval(new_addressee_pubkey)

        if new_addressee_name in self.address_book.keys():
            print("This addressee already exists.")
            return
        elif not isinstance(new_addressee_pubkey,list) or not isinstance(new_addressee_pubkey[0],str) or not isinstance(new_addressee_pubkey[1],str):
            print("The pubkey is invalid.")
            return
        else:
            self.address_book[new_addressee_name] = new_addressee_pubkey
            self.new_addressee = new_addressee_name
            try:
                with open(self.address_book_filename, "w") as f:
                    json.dump(self.address_book, f, indent=4, sort_keys=True)
            except Exception:
                print("Error while writing json data: ", Exception)
            self.accept()

    def loadData(self,document):
        try:
            with open(document, "r") as f:
                data = json.load(f)
            return data
        except Exception:
            print("Error while loading data")
            pass

    def paste(self):
        text = copyPaste.paste()
        self.input_field.setText(text)