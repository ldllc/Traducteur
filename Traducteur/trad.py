import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QDialog,
    QSizePolicy, QHeaderView, QMessageBox, QSpacerItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from googletrans import Translator
import sqlite3

class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_db()

        self.translator = Translator()

        # Mise en page principale
        main_layout = QVBoxLayout(self)

        # Section supérieure
        top_layout = QHBoxLayout()

        # Zone de texte à gauche
        left_text_layout = QVBoxLayout()
        left_title_label = QLabel('Détection Automatique :', self)
        left_title_label.setAlignment(Qt.AlignLeft)
        left_text_layout.addWidget(left_title_label)
        self.left_text_box = QTextEdit(self)
        left_text_layout.addWidget(self.left_text_box)
        default_text = "Entrez votre texte ici"
        self.left_text_box.setPlaceholderText(default_text)
        self.left_text_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Zone de texte à droite
        right_text_layout = QVBoxLayout()

        self.language_combo = QComboBox(self)
        languages = {
            'Français': 'French',
            'Anglais': 'English',
            'Espagnol': 'Spanish',
            'Allemand': 'German',
            'Russe': 'Russian',
            'Portugais': 'Portuguese',
            'Italien': 'Italian',
            'Chinois': 'zh-CN',
            'Arabe': 'Arabic',
            'Japonais': 'Japanese'
        }
        for lang_name, lang_code in languages.items():
            self.language_combo.addItem(lang_name, lang_code)
        right_text_layout.addWidget(self.language_combo)

        self.language_combo.setStyleSheet('margin-top: -0px;')
        # Définir l'alignement pour la mise en page contenant le QComboBox
        right_text_layout.setAlignment(Qt.AlignLeft)

        self.right_text_box = QTextEdit(self)
        self.right_text_box.setReadOnly(True)
        self.right_text_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_text_layout.addWidget(self.right_text_box)
        default_text = "traduction"
        self.right_text_box.setPlaceholderText(default_text)

        # Ajouter les zones de texte gauche et droite au même layout horizontal
        top_layout.addLayout(left_text_layout)
        top_layout.addLayout(right_text_layout)

        main_layout.addLayout(top_layout)

        # Section inférieure
        bottom_layout = QHBoxLayout()

        # Ajouter un espaceur extensible pour centrer les boutons
        bottom_layout.addStretch(1)

        # Bouton Historique
        history_button = QPushButton('Historique', self)
        history_button.setStyleSheet('background-color: #0077b6; color: white; border: none; height: 40px; width: 90px;')
        bottom_layout.addWidget(history_button)

        # Bouton Traduire
        self.translate_button = QPushButton('Traduire', self)
        self.translate_button.setStyleSheet('background-color: #0077b6; color: white; border: none; height: 40px; width: 90px;')
        bottom_layout.addWidget(self.translate_button)

        # Bouton Effacer
        clear_button = QPushButton('Effacer', self)
        clear_button.setStyleSheet('background-color: #0077b6; color: white; border: none; height: 40px; width: 90px;')
        bottom_layout.addWidget(clear_button)

        self.translation_label = QLabel('', self)
        self.translation_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.translation_label)

        # Ajouter un autre espaceur extensible pour centrer les boutons
        bottom_layout.addStretch(1)

        main_layout.addLayout(bottom_layout)

        # Connecter les boutons
        self.translate_button.clicked.connect(self.translate_text)
        history_button.clicked.connect(self.show_history)
        clear_button.clicked.connect(self.clear_text_boxes)

        # Définir la police d'écriture Poppins pour tous les textes de l'application
        font = QFont("Poppins")
        self.setFont(font)

    def init_db(self):
        self.conn = sqlite3.connect('Database/translation_history.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT,
                translated_text TEXT
            )
        ''')
        self.conn.commit()

    def save_translation_to_db(self, original_text, translated_text):
        self.cursor.execute('''
            INSERT INTO translations (original_text, translated_text) VALUES (?, ?)
        ''', (original_text, translated_text))
        self.conn.commit()

    def show_history(self):
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("Historique")
        history_dialog.setFixedSize(550, 307)

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['Textes Originaux', 'Traductions'])

        # Redimensionnez automatiquement les colonnes de la table pour remplir l'espace disponible
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.cursor.execute('SELECT original_text, translated_text FROM translations')
        translations = self.cursor.fetchall()

        for row, translation in enumerate(translations):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(translation[0]))
            table.setItem(row, 1, QTableWidgetItem(translation[1]))

        layout = QVBoxLayout()
        layout.addWidget(table)
        history_dialog.setLayout(layout)

        button_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(button_spacer)

        # Add the "Retour" button
        back_button = QPushButton('Retour', history_dialog)
        back_button.setStyleSheet('background-color: #0077b6; color: white; border: none; height: 40px; width: 70px;')
        back_button.clicked.connect(history_dialog.reject)  # Close the dialog on button click
        layout.addWidget(back_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        # Ajouter un bouton "Vider l'historique"
        clear_history_button = QPushButton('Vider l\'historique', history_dialog)
        clear_history_button.setStyleSheet('background-color: #0077b6; color: white; border: none; height: 40px; width: 70px;')
        clear_history_button.clicked.connect(self.clear_history)

        button_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Ajouter les boutons à un layout horizontal
        button_layout = QHBoxLayout()
        button_layout.addWidget(clear_history_button)
        button_layout.addWidget(back_button)

        # Ajouter le layout horizontal à la disposition verticale existante
        layout.addLayout(button_layout)

        history_dialog.exec_()

    def clear_history(self):
        # Vérifier si l'historique est déjà vide
        self.cursor.execute('SELECT COUNT(*) FROM translations')
        count = self.cursor.fetchone()[0]

        if count == 0:
            QMessageBox.information(self, 'Information', 'L\'historique est déjà vide.', QMessageBox.Ok)
            return

        # Demander une confirmation avant d'effacer l'historique
        confirmation = QMessageBox.question(self, 'Confirmation', 'Êtes-vous sûr de vouloir vider l\'historique?', 
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirmation == QMessageBox.Yes:
            # Effacer le contenu de la base de données
            self.cursor.execute('DELETE FROM translations')
            self.conn.commit()
            
            # Afficher un message indiquant que l'historique a été vidé
            QMessageBox.information(self, 'Confirmation', 'L\'historique a été vidé.', QMessageBox.Ok)
            
            # Fermer la fenêtre du dialogue
            history_dialog = self.sender().parent()
            history_dialog.accept()


    def translate_text(self):
        text = self.left_text_box.toPlainText()
        dest_language = self.language_combo.currentData() 
        translation = self.translator.translate(text, dest=dest_language)
        self.right_text_box.setPlainText(translation.text)

        # Save translation to the database
        self.save_translation_to_db(text, translation.text)

    def clear_text_boxes(self):
        self.left_text_box.clear()
        self.right_text_box.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.setWindowTitle("Traducteur")

    app_icon = QIcon("Img/traducteur-2.png")
    app.setWindowIcon(app_icon)

    window.show()
    sys.exit(app.exec_())
