#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division, print_function)

import shutil
import os
import sqlite3

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QIcon, QVBoxLayout, QFileDialog, QGridLayout, QTextEdit,
                         QTableWidgetItem, QPushButton, QCompleter, QMessageBox)

from Common.ui.util import raise_success, raise_error
from Common.ui.table import FTableWidget
from Common.ui.common import (FWidget, FPageTitle, Button_save, FormLabel,
                              FLabel, LineEdit)
from configuration import Config
from model import Records, Category

from ui.record_edit import EditRecordsViewWidget

try:
    unicode
except:
    unicode = str

class RecordsViewWidget(FWidget):

    def __init__(self, record="", parent=0, *args, **kwargs):
        super(RecordsViewWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parentWidget().setWindowTitle(Config.APP_NAME +
                                           u"    GESTION D'ARCHIVE")

        self.parent = parent

        tablebox = QVBoxLayout()
        tablebox.addWidget(FPageTitle(u"Tableau document"))
        self.table_record = RecordsTableWidget(parent=self)
        tablebox.addWidget(self.table_record)

        self.description = QTextEdit()
        self.category = LineEdit()
        self.image = LineEdit()
        self.path_ = FormLabel("...")

        completion_values = [catg.name for catg in Category.all()]
        completer = QCompleter(completion_values, parent=self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.category.setCompleter(completer)

        gridbox = QGridLayout()
        gridbox.addWidget(FLabel(u"Désignation: "), 0, 0)
        gridbox.addWidget(self.description, 1, 0, 1, 2)
        gridbox.addWidget(FLabel(u"Categorie: "), 2, 0)
        gridbox.addWidget(self.category, 2, 1)
        butt_parco = QPushButton(QIcon.fromTheme('document-open', QIcon('')), "")
        butt_parco.clicked.connect(self.import_image)
        gridbox.addWidget(FLabel(u"Image: "), 3, 0)
        gridbox.addWidget(butt_parco, 3, 1)
        gridbox.addWidget(self.path_, 4, 0, 4, 2)
        butt = Button_save(u"Enregistrer")
        butt.clicked.connect(self.add_prod)
        gridbox.addWidget(butt, 7, 1)
        gridbox.setColumnStretch(3, 2)
        gridbox.setRowStretch(1, 1)

        gridbox.addLayout(tablebox, 0, 3, 6, 7)

        vbox = QVBoxLayout()
        vbox.addLayout(gridbox)
        self.setLayout(vbox)

    def import_image(self):

        self.path_filename = QFileDialog.getOpenFileName(self, "Open Image", "",
            "Documents ({})".format(Config.DOC_SUPPORT),)
        if self.path_filename:
            self.name_file = os.path.basename(u"{}".format(self.path_filename))
            self.path_.setText(unicode(self.name_file))

    def add_prod(self):
        ''' add operation '''
        description = str(self.description.toPlainText())
        category = str(self.category.text())
        print(description)

        self.description.setStyleSheet("")
        self.category.setStyleSheet("")
        if description == "":
            self.description.setStyleSheet("background-color: rgb(255, 235, 235);")
            self.description.setToolTip(u"Ce champs est obligatoire.")
            return False
        record = Records()
        record.description = description
        record.category = Category.get_or_create(category)

        try:
            record.doc_file_mane = str(self.name_file)
            record.doc_file_slug = record.import_doc(unicode(self.path_filename),
                                                     str(self.name_file))
        except IOError:
            raise
            raise_error(u"Problème d'import du fichier",
                        u"Changer le nom du fichier et reesayé \n \
                        si ça ne fonctionne pas contacté le developper")
            return
        except AttributeError:
            raise
            pass
        except:
            raise

        try:
            record.save()
            self.description.clear()
            self.category.clear()
            self.path_.clear()
            self.table_record.refresh_()
            raise_success(_(u"Confirmation"), _(u"Le document {} "
                            u" a été bien enregistré".format(record.description)))
        except sqlite3.IntegrityError as e:
            err = u"%s" % e
            if u"description" in err:
                self.description.setStyleSheet("background-color: "
                                               "rgb(255, 235, 235);")
                self.description.setToolTip(u"Le produit {} "
                                        u"document déjà dans la basse de "
                                        u"donnée.".format(record.description))
                return False


class RecordsTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.hheaders = [u"Category", u"Document", u"Modification", u"Suppression"]
        self.stretch_columns = [0, 1, ]
        self.align_map = {0: 'l', 1: 'l'}
        self.ecart = -250
        self.display_vheaders = True
        # self.display_fixed = True
        self.refresh_()

    def refresh_(self):
        """ """

        self._reset()
        self.set_data_for()
        self.refresh()

    def set_data_for(self):
        self.data = [(record.category, record.description, "", "")
                     for record in Records.select().where(Records.trash==False).order_by(Records.category.asc())]

    def _item_for_data(self, row, column, data, context=None):
        if column == 2:
            return QTableWidgetItem(QIcon(u"{}edit.png".format(Config.img_cmedia)), "")
        if column == 3:
            return QTableWidgetItem(QIcon(u"{}del.png".format(Config.img_cmedia)), "")
        return super(RecordsTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def click_item(self, row, column, *args):
        record = Records.filter(description=self.data[row][1]).get()
        modified_column = 2
        if column == modified_column:
            self.parent.open_dialog(EditRecordsViewWidget, modal=True, record=record)
            # self.parent.change_main_context(RecordsViewWidget)
        if column == 3:
            self.title = FPageTitle()
            reply = QMessageBox.question(self, 'Confirmation de le suppression',
                self.tr("<h4>Voulez vous vraiment le supprimer?<h4>"),
                 QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                record.istrash()
                self.refresh_()
        else:
            return
