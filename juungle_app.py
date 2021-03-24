import sys
import os

import requests
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QComboBox, QApplication, QGridLayout
from PyQt5.QtWidgets import QLabel, QCompleter, QLineEdit
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from juungle.nft import NFTs


CACHE_DIR_PATH = '/tmp/juungle-cache'
VERSION = '0.1'


def cache_exists(file_id):
    if not os.path.isdir(CACHE_DIR_PATH):
        os.mkdir(CACHE_DIR_PATH)

    return os.path.isfile('{}/{}'.format(CACHE_DIR_PATH, file_id))


class PyQtLayout(QWidget):
    def __init__(self, nfts):
        super().__init__()
        self.nfts = nfts
        self.UI()
        self.id_names = {}

    def UI(self):

        vbox = QVBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Search...')
        self.search_edit.returnPressed.connect(self.update_search)
        vbox.addWidget(self.search_edit)

        self.min_value = QLineEdit()
        self.min_value.setPlaceholderText('Min value in BCH')
        self.min_value.returnPressed.connect(self.update_search_price)
        vbox.addWidget(self.min_value)

        self.max_value = QLineEdit()
        self.max_value.setPlaceholderText('Max value in BCH')
        self.max_value.returnPressed.connect(self.update_search_price)
        vbox.addWidget(self.max_value)

        self.options = QComboBox(self)
        self.options.addItem('All')
        self.options.addItem('For Sale')
        self.options.addItem('Sold/Not for sale')
        self.options.currentIndexChanged.connect(self.update_options)
        vbox.addWidget(self.options)

        self.cb_nfts = QComboBox(self)
        self.cb_nfts.currentIndexChanged.connect(self.update_image)
        vbox.addWidget(self.cb_nfts)

        filter_gb = QGroupBox('Filters')
        filter_gb.setLayout(vbox)

        vbox = QVBoxLayout()
        self.lbl_image = QLabel(self)
        vbox.addWidget(self.lbl_image)
        image_gb = QGroupBox('Image')
        image_gb.setLayout(vbox)

        vbox = QVBoxLayout()
        self.info_box = {
            "name": QLabel('NFTName', self),
            "price": QLabel('Price', self),
            "price_history": QLabel('', self),
        }
        vbox.addWidget(self.info_box['name'])
        vbox.addWidget(self.info_box['price'])
        vbox.addWidget(self.info_box['price_history'])
        info_gb = QGroupBox('Info')
        info_gb.setLayout(vbox)

        main_grid = QGridLayout()
        main_grid.addWidget(filter_gb, 0, 0)
        main_grid.addWidget(image_gb, 0, 1)
        main_grid.addWidget(info_gb, 0, 2)

        self.setLayout(main_grid)

        title = ('Juungle.net UI v0.1 BETA '
                 '- Number of NFTs: {} '
                 '- Last update: {}').format(len(self.nfts),
                                             datetime.now())
        self.setWindowTitle(title)
        self.update_options(0)
        self.show()

    def update_search(self):
        self.cb_nfts.setCurrentText(self.search_edit.text())
        self.search_edit.clear()

    def update_search_price(self):
        self.update_options(self.options.currentIndex())

    def update_options(self, cb_index):
        self.cb_nfts.clear()
        self.id_names = {}
        self.search_edit.clear()

        if cb_index == 0:
            for nft in self.nfts.keys():
                price_bch = self.nfts[nft][-1].price_bch
                if self.min_value.text():
                    if not price_bch or price_bch and \
                            price_bch < float(self.min_value.text()):
                        continue
                if self.max_value.text():
                    if not price_bch or price_bch and \
                            price_bch > float(self.max_value.text()):
                        continue

                self.id_names[self.nfts[nft][0].name] = nft

        if cb_index == 1:
            for nft in self.nfts.keys():
                price_bch = self.nfts[nft][-1].price_bch
                if self.nfts[nft][-1].is_for_sale:
                    if self.min_value.text():
                        if not price_bch or price_bch and \
                                price_bch < float(self.min_value.text()):
                            continue
                    if self.max_value.text():
                        if not price_bch or price_bch and \
                                price_bch > float(self.max_value.text()):
                            continue

                    self.id_names[self.nfts[nft][0].name] = nft

        if cb_index == 2:
            for nft in self.nfts.keys():
                if self.nfts[nft][-1].is_sold:
                    self.id_names[self.nfts[nft][0].name] = nft

        names = sorted(self.id_names.keys())

        completer = QCompleter(names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.search_edit.setCompleter(completer)

        for i in names:
            self.cb_nfts.addItem(i, self.id_names[i])

    def update_image(self, index):
        pixmap = QPixmap()
        nft = None

        for i in self.nfts.keys():
            nft = self.nfts[i][-1]
            nfts = self.nfts[i]
            if self.cb_nfts.itemData(index) == nft.token_id:
                break
        if not nft:
            print(self.cb_nfts.currentText())

        image = None
        if not cache_exists(nft.token_id):
            image = requests.get(nft.image, stream=True).content
            with open('{}/{}'.format(CACHE_DIR_PATH,
                                     nft.token_id), 'wb+') as f_image:
                f_image.write(image)
        else:
            with open('{}/{}'.format(CACHE_DIR_PATH,
                                     nft.token_id), 'rb') as f_image:
                image = f_image.read()

        pixmap.loadFromData(image)

        self.lbl_image.setPixmap(pixmap)
        self.info_box['name'].setText(nft.name)

        if nft.price_satoshis:
            price = '{} {}'.format(nft.price_bch, 'BCH')
        else:
            price = '-'
        self.info_box['price'].setText(price)

        msg = ''
        for n in nfts:
            if n.is_sold:
                msg += ('Sold for {} BCH<br/>'.format(n.price_bch))

            if n.is_for_sale:
                msg += ('<a href="https://juungle.net/#/assets/{}">'
                        '{}</a>{} BCH<br/>').format(n.token_id,
                                                    'Click to buy for ', n.price_bch)

            self.info_box['price_history'].setText(msg)


def main():
    app = QApplication([])
    nfts = NFTs()
    nfts.token_group = 'WAIFU'
    nfts.get_nfts()
    ex = PyQtLayout(nfts.group_ids)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
