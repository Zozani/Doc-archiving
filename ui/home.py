#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QHBoxLayout, QGridLayout, QGroupBox, QIcon)

from model import Owner
from common.check_mac import get_mac, is_valide_mac
from configuration import Config
from common.ui.util import SystemTrayIcon
from common.ui.common import (F_Widget, F_PageTitle, FormLabel, PyTextViewer,
                              Button_menu, F_PageTitle, F_Label)
from ui.admin import AdminViewWidget
from ui.records import RecordsViewWidget
from ui.record_consultation import RecordConsultationViewWidget


class HomeViewWidget(F_Widget):
    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(HomeViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.root_permission = [u"admin", u"superuser"]

        blanck = 3 * " "
        self.parentWidget().setWindowTitle(Config.APP_NAME + blanck + "MENU GENERAL")

        self.title = F_PageTitle(u"{} MENU GENERAL {}".format(blanck, blanck))
        self.title.setStyleSheet("background: url({}logo) no-repeat scroll 20px 50px #CCCCCC;"
                                 "border-radius: 14px 14px 4px 4px;"
                                 "font: 15pt 'URW Bookman L';".format(Config.img_media))

        self.consultation = Button_menu(_("Consultation"))
        self.consultation.clicked.connect(self.goto_consultation)
        self.consultation.setIcon(QIcon.fromTheme('save', QIcon(u"{}archive.png".format(Config.img_media))))

        self.add_archiv = Button_menu(_("Archivage"))
        # Affiche sur le commentaire sur le status bar
        # add_archiv.setStatusTip("hhhhhh")
        self.add_archiv.setIcon(QIcon.fromTheme('save', QIcon(u"{}archive_add.png".format(Config.img_media))))
        self.add_archiv.clicked.connect(self.goto_archi)

        self.admin = Button_menu(_("Administration"))
        self.admin.clicked.connect(self.goto_admin)
        self.admin.setIcon(QIcon.fromTheme('save', QIcon(u"{}admin.png".format(Config.img_media))))
        self.label = F_Label(self)
        self.label.setStyleSheet("background: url('{}center.png') no-repeat scroll 0 0;"
                                 "height: 50px;width:50px; margin: 0; padding: 0;".format(Config.img_media))

        # editbox.setColumnStretch(50, 2)

        vbox = QHBoxLayout(self)
        vbox.addWidget(self.title)
        # vbox.addLayout(editbox)

        if Owner.get(islog=True).login_count > Config.tolerance:
            if not is_valide_mac(Config().license):
                self.createErroMsGroupBox()
                vbox.addWidget(self.chow_ms_err)
                self.setLayout(vbox)
                return
        self.createMenuMStockGroupBox()
        vbox.addWidget(self.mstockgbox)
        self.setLayout(vbox)

    def createErroMsGroupBox(self):
        self.chow_ms_err = QGroupBox()

        ms_err = PyTextViewer(u"<h3>Vous n'avez pas le droit d'utiliser ce \
                              logiciel sur cette machine, veuillez me contacté \
                              </h3> <ul><li><b>Tel:</b> {phone}</li>\
                              <li><b>{adress}</b></li><li><b>E-mail:</b> \
                              {email}</li></ul></br></br>{mac} \
                              ".format(email=Config.EMAIL_AUT,
                                       adress=Config.ADRESS_AUT,
                                       phone=Config.TEL_AUT,
                                       mac=get_mac().replace(":", ":")))

        gridbox = QGridLayout()
        gridbox.addWidget(F_PageTitle(_("Erreur de permission")), 0, 2)
        gridbox.addWidget(ms_err, 1, 2)
        self.chow_ms_err.setLayout(gridbox)

    def createMenuMStockGroupBox(self):
        self.mstockgbox = QGroupBox()

        editbox = QGridLayout()
        editbox.addWidget(self.consultation, 0, 1, 1, 1)
        editbox.addWidget(self.label, 1, 1, 1, 1)
        editbox.addWidget(self.admin, 1, 2, 1, 1)
        editbox.addWidget(self.add_archiv, 0, 3, 1, 1)
        self.mstockgbox.setLayout(editbox)


    def check_log(self, page, permiss=None):

        if not Config.LOGIN:
            self.parent.active_menu_ad()
            SystemTrayIcon((_(u"Avertissement de Securité"),
                            "({}) Il est vivement souhaité de securiser son "
                            "application".format(Config.APP_NAME)), parent=self)
        else:
            try:
                owner = Owner.get(islog=True)
                self.parent.active_menu_ad() if owner.group in self.root_permission else self.parent.active_menu()
            except:
                return False
        self.change_main_context(page)

    def goto_consultation(self):
        self.check_log(RecordConsultationViewWidget, permiss=self.root_permission)

    def goto_archi(self):
        self.root_permission.append("user")
        self.check_log(RecordsViewWidget, permiss=self.root_permission)

    def goto_admin(self):
        self.check_log(AdminViewWidget, permiss=self.root_permission)