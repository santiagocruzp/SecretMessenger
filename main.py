
import datetime, json, math, os, sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QStatusBar,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget
)
import copyPaste
import dialogs
from makePublicPrivateKeys import generateKey
import publicKeyCipher


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.basedir = os.path.dirname(__file__)

        """Call dialog box to load the app user"""
        user_manager = dialogs.UserSelectionDialog()
        user_manager.exec()

        """Class variables"""
        self.SYMBOLS = f"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 !?'.,-:;()$/&%+_@\n\\\t"
        self.user = user_manager.user
        self.privKey = 0
        self.pubKey = 0

        # load the user's address book
        self.address_book_file = os.path.join(self.basedir, user_manager.address_book)
        if not os.path.exists(self.address_book_file):
            with open(self.address_book_file, "w") as f:
                json.dump({}, f)

        with open(self.address_book_file, "r") as f:
            self.address_book = json.load(f)

        # load the user's private and public keys
        if os.path.exists(os.path.join(self.basedir, "keys.json")):
            try:
                key_data = self.loadData("keys.json")
                if self.user in key_data.keys():
                    self.privKey = key_data[self.user]["privKey"]
                    self.n = int(key_data[self.user]["privKey"][0])
                    self.d = int(key_data[self.user]["privKey"][1])
                    self.pubKey = key_data[self.user]["pubKey"]

                else:
                    self.createUserKeys()
                    key_data[self.user] = {
                        "privKey":[str(self.privKey[0]), str(self.privKey[1])],
                        "pubKey":[str(self.pubKey[0]), str(self.pubKey[1])]
                    }
                    self.privKey = key_data[self.user]["privKey"]
                    self.n = self.privKey[0]
                    self.d = self.privKey[1]
                    self.pubKey = key_data[self.user]["pubKey"]

                    with open(os.path.join(self.basedir,"keys.json"),"w") as o:
                        json.dump(key_data, o, indent=4, sort_keys=True)

            except json.JSONDecodeError or Exception as e:
                print(e)

        """Main window parameters"""
        self.setWindowTitle(f"""Secret Messenger --- {self.user}'s session""")
        self.setWindowIcon(QIcon(os.path.join(self.basedir, "images/lock--arrow.png")))
        self.setFixedSize(1100, 780)

        """Main widget and layout"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        container = QVBoxLayout(main_widget)

        """Widgets"""
        # Banner
        pixmap = QPixmap(os.path.join(self.basedir, "images/sm-banner.png"))
        banner_label = QLabel()
        banner_label.setFixedSize(1060, 100)
        banner_label.setPixmap(pixmap)
        banner_label.setScaledContents(True)

        # Status bar
        divider = QFrame()
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_label = QLabel("Status: ")
        #status_bar_layout.addStretch()
        status_bar.addWidget(status_label)
        self.state_label = QLabel("Ready")
        status_bar.addWidget(self.state_label)
        #status_bar_layout.addStretch()

        # top layer: radio buttons and other buttons
        top_layer_layout = QHBoxLayout()
        action_radio_layout = QHBoxLayout()
        action_radio_layout.setContentsMargins(10,0,0,0)
        self.action_option1 = QRadioButton("Encrypt a message")
        self.action_option1.setStyleSheet("font-size:14pt;")
        self.action_option1.setChecked(True)
        self.action_option1.toggled.connect(lambda state: self.toggleEditable(state, self.addressee_dropdown))
        self.action_option2 = QRadioButton("Decrypt a ciphertext")
        self.action_option2.setStyleSheet("font-size:14pt;")
        action_radio_layout.addWidget(self.action_option1)
        action_radio_layout.addWidget(self.action_option2)
        action_radio_layout.addStretch()
        action_radio_group = QButtonGroup()
        action_radio_group.addButton(self.action_option1)
        action_radio_group.addButton(self.action_option2)
        action_radio_group.setExclusive(True)
        top_layer_layout.addLayout(action_radio_layout)
        top_layer_layout.addStretch()
        share_button = QPushButton(" Share my public key")
        share_button.setIcon(QIcon(os.path.join(self.basedir, "images/share.png")))
        share_button.clicked.connect(self.sharePubKey)
        top_layer_layout.addWidget(share_button)
        addressbook_button = QPushButton()
        addressbook_button.setIcon(QIcon(os.path.join(self.basedir, "images/address-book.png")))
        addressbook_button.setToolTip("Manage my addresses")
        top_layer_layout.addWidget(addressbook_button)
        switch_button = QPushButton()
        switch_button.setIcon(QIcon(os.path.join(self.basedir, "images/users.png")))
        switch_button.clicked.connect(self.reset)
        switch_button.setToolTip("Change user")
        top_layer_layout.addWidget(switch_button)
        help_button = QPushButton()
        help_button.setIcon(QIcon(os.path.join(self.basedir, "images/question-button.png")))
        help_button.setToolTip("Help")
        top_layer_layout.addWidget(help_button)

        # input and output fields with buttons below, and encrypt/decrypt button
        input_output_layout = QHBoxLayout()

        input_layout = QVBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText(
            """Write or paste the text to encrypt\n\nAvoid using exotic symbols such as umlaut, tilde, and brackets.\n\nMake sure to select or add the public key of the message's recipient ("the addressee"). Use the dropdown below."""
        )
        paste_button = QPushButton(" Paste")
        paste_button.setFixedWidth(90)
        paste_button.setStyleSheet("font-size:11pt;")
        paste_button.setIcon(QIcon(os.path.join(self.basedir, "images/clipboard-list.png")))
        paste_button.clicked.connect(self.paste)
        add_addressee_button = QPushButton()
        add_addressee_button.setIcon((QIcon(os.path.join(self.basedir, "images/plus-button.png"))))
        add_addressee_button.setToolTip("Add a new addressee")
        add_addressee_button.clicked.connect(self.addAddressee)
        input_layout.addWidget(self.input_field)
        input_buttons_layout = QHBoxLayout()
        addressee_label = QLabel("Addressee ")
        addressee_label.setStyleSheet("font-size:11pt;")
        self.addressee_dropdown = QComboBox()
        self.addressee_dropdown.addItems(self.address_book.keys())
        self.addressee_dropdown.setFixedWidth(200)
        self.addressee_dropdown.setStyleSheet("font-size:11pt;")
        input_buttons_layout.addWidget(addressee_label)
        input_buttons_layout.addWidget(self.addressee_dropdown)
        input_buttons_layout.addWidget(add_addressee_button, alignment=Qt.AlignmentFlag.AlignLeft)
        input_buttons_layout.addStretch()
        input_buttons_layout.addWidget(paste_button, alignment=Qt.AlignmentFlag.AlignRight)
        input_layout.addLayout(input_buttons_layout)

        self.process_button = QToolButton()
        self.process_button.setText("Encrypt")
        self.process_button.setIcon(QIcon(os.path.join(self.basedir, "images/Lock-72.png")))
        self.process_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.process_button.setStyleSheet('font-size:13pt;')
        self.process_button.setIconSize(QSize(64,64))
        self.process_button.clicked.connect(self.onSubmit)

        output_layout = QVBoxLayout()
        self.output_field = QTextEdit()
        self.output_field.setPlaceholderText("Your ciphertext will appear here")
        self.output_field.setReadOnly(True)
        clear_button = QPushButton("Clear fields")
        clear_button.setFixedWidth(90)
        clear_button.setStyleSheet("font-size:11pt")
        clear_button.clicked.connect(self.clearText)
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
        output_buttons_layout = QHBoxLayout()
        output_layout.addWidget(self.output_field)
        output_buttons_layout.addWidget(clear_button, alignment=Qt.AlignmentFlag.AlignLeft)
        output_buttons_layout.addStretch()
        output_buttons_layout.addWidget(copy_button, alignment=Qt.AlignmentFlag.AlignRight)
        output_buttons_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)
        output_layout.addLayout(output_buttons_layout)

        input_output_layout.addLayout(input_layout)
        input_output_layout.addWidget(self.process_button)
        input_output_layout.addLayout(output_layout)

        # Add widgets and layouts to the main layout
        container.addWidget(banner_label, alignment=Qt.AlignmentFlag.AlignCenter)
        container.addLayout(top_layer_layout)
        container.addLayout(input_output_layout)
        container.addWidget(divider)
        container.setSpacing(10)
        container.setContentsMargins(20,0,20,0)

    """Class functions"""
    def addAddressee(self):
        new_addressee_dialog = dialogs.addAddresseeDialog(self.address_book, self.address_book_file)
        new_addressee_dialog.exec()

        if new_addressee_dialog.new_addressee == "":
            self.updateStatus("Failed to add a new addressee")
        else:
            self.updateStatus(f"Addressee {new_addressee_dialog.new_addressee} was added successfully")

        with open(self.address_book_file, "r") as f:
            self.address_book = json.load(f)

        self.addressee_dropdown.addItems(self.address_book.keys())


    def clearText(self):
        self.input_field.clear()
        self.output_field.clear()

    def copy(self):
        copyPaste.copy(self.output_field.toPlainText())
        self.updateStatus("Content copied to clipboard")

    def createUserKeys(self):
        self.privKey, self.pubKey = generateKey(1024)
        self.n = self.privKey[0]
        self.e = self.privKey[1]

    def loadData(self,document):
        file = os.path.join(self.basedir,document)
        try:
            with open(file, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            self.updateStatus(f"Error while loading data: {e}")
            pass

    def onSubmit(self):
        text = self.input_field.toPlainText()
        if self.action_option1.isChecked():
            self.updateStatus("Encrypting...")
            n, e = self.address_book[self.addressee_dropdown.currentText()]
            n, e = int(n), int(e)
            encrypted_blocks = publicKeyCipher.encryptMessage(text,(n,e),160)
            # convert the large in values to one string value
            for i in range(len(encrypted_blocks)):
                encrypted_blocks[i] = str(encrypted_blocks[i])  # needed for join function to work
            encrypted_content = ','.join(encrypted_blocks)
            self.output_field.setText(encrypted_content)
            self.updateStatus("Encryption successful!")

        elif self.action_option2.isChecked():
            blockSize = 160
            keySize = 1024
            ciphertext_length = len(self.input_field.toPlainText())
            encryptedMessage = self.input_field.toPlainText()
            if not (math.log(2 ** keySize, len(self.SYMBOLS)) >= blockSize):
                self.updateStatus(
                    'ERROR: Block size is too large for the key and symbol set size.')
                return
            # Encrypt the message:
            encryptedBlocks = []
            for block in encryptedMessage.split(','):
                encryptedBlocks.append(int(block))
            secret_message = publicKeyCipher.decryptMessage(encryptedBlocks,ciphertext_length,(self.n,self.d),blockSize)
            self.output_field.setText(secret_message)
            self.updateStatus("Secret message successfully decrypted!")

    def paste(self):
        text = copyPaste.paste()
        self.input_field.setText(text)

    def reset(self):
        # reset MainWindow
        window.close()
        new_window = MainWindow()
        new_window.show()

    def sharePubKey(self):
        share_dialog = dialogs.showPubKeyDialog(self.user, self.pubKey)
        share_dialog.exec()

    def toggleEditable(self, state, dropdown):
        if state:
            dropdown.setEnabled(True)
            self.process_button.setText("Encrypt")
            self.process_button.setIcon(QIcon(os.path.join(self.basedir, "images/Lock-72.png")))
            self.input_field.setPlaceholderText(
                """Write or paste the text to encrypt\n\nAvoid using exotic symbols such as umlaut, tilde, and brackets.\n\nMake sure to select or add the public key of the message's recipient ("the addressee"). Use the dropdown below."""
            )
            self.output_field.setPlaceholderText("Your ciphertext will appear here")
        else:
            dropdown.setEnabled(False)
            self.process_button.setText("Decrypt")
            self.process_button.setIcon(QIcon(os.path.join(self.basedir, "images/Unlock-72.png")))
            self.input_field.setPlaceholderText("Paste the ciphertext here")
            self.output_field.setPlaceholderText("The decrypted secret message will appear here")

    def updateStatus(self, message):
        self.state_label.setText(message)

    def write(self):
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

        current_daytime = datetime.datetime.now()
        formatted_datetime = current_daytime.strftime('_%Y%m%d_%H%M')
        if self.action_option1.isChecked():
            content = f"This message was encrypted for {self.addressee_dropdown.currentText()} on {formatted_datetime}.\n\n"
        else:
            content = f"This is a decrypted message for {self.user}'s eyes only.\n\n"
        content += self.output_field.toPlainText()

        try:
            with open(file, "w") as f:
                f.write(content)
            self.updateStatus(f"Content successfully exported with path: {file}")
        except Exception:
            self.updateStatus(Exception)

"""Start the event loop and instantiate the main window"""

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()