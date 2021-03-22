import sys
import os

import requests
from PyQt5.QtWidgets import QWidget, QComboBox, QApplication, QGridLayout
from PyQt5.QtWidgets import QLabel, QCheckBox, QHBoxLayout, QTextBrowser
from PyQt5.QtGui import QIcon, QPixmap

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

    def UI(self):
        self.combo = QComboBox(self)
        grid_image = QGridLayout()

        self.combo.currentIndexChanged.connect(self.update_image)
        grid_image.addWidget(self.combo, 1, 0)

        self.lbl_image = QLabel(self)
        grid_image.addWidget(self.lbl_image, 1, 1)

        info_grid = QGridLayout()
        self.info_box = {
            "name": QLabel('NFTName', self),
            "price": QLabel('Price', self),
            "info1": QLabel('info1 desc', self),
            "info2": QLabel('info2 desc', self)
        }
        info_grid.addWidget(QLabel('Name', self), 0, 0)
        info_grid.addWidget(self.info_box['name'], 0, 1)
        info_grid.addWidget(QLabel('Price', self), 1, 0)
        info_grid.addWidget(self.info_box['price'], 1, 1)
        info_grid.addWidget(QLabel('Price history', self), 2, 0)
        info_grid.addWidget(self.info_box['info1'], 2, 1)
        self.info_box['info1'].setOpenExternalLinks(True)

        cb_grid = QGridLayout()
        box_layout = QHBoxLayout()
        box_layout.addLayout(cb_grid)
        box_layout.addLayout(grid_image)
        box_layout.addLayout(info_grid)

        grid_image.addWidget(self.lbl_image, 1, 1)

        self.options = QComboBox(self)
        self.options.currentIndexChanged.connect(self.update_options)

        self.options.addItem('All')
        self.options.addItem('For Sale')
        self.options.addItem('Sold')
        cb_grid.addWidget(self.options, 0, 0)

        self.setLayout(box_layout)
        title = ('Juungle.net UI v0.1 BETA '
                 '- Number of NFTs: {}').format(len(self.nfts))
        self.setWindowTitle(title)
        self.show()

    def update_options(self, index):
        self.combo.clear()

        if index == 0:
            for i in self.nfts.keys():
                nft = self.nfts[i][-1]
                self.combo.addItem(nft.name, nft.token_id)

        if index == 1:
            for i in self.nfts.keys():
                nft = self.nfts[i][-1]
                if nft.is_for_sale:
                    self.combo.addItem(nft.name, nft.token_id)

        if index == 2:
            for i in self.nfts.keys():
                nft = self.nfts[i][-1]
                if nft.is_sold:
                    self.combo.addItem(nft.name, nft.token_id)

    def update_image(self, index):
        pixmap = QPixmap()
        nft = None

        for i in self.nfts.keys():
            nft = self.nfts[i][0]
            nfts = self.nfts[i]
            if self.combo.itemData(index) == nft.token_id:
                break
        if not nft:
            print(self.combo.currentText())

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

        self.info_box['info2'].setText('')

        msg = ''
        for n in nfts:
            if n.is_sold:
                msg += ('Sold for {} BCH<br/>'.format(n.price_bch))
                continue

            if n.is_for_sale:
                msg += ('<a href="https://juungle.net/#/assets/{}">'
                        '{}</a>{} BCH<br/>').format(n.token_id,
                                                    'Click to buy for ', n.price_bch)

            self.info_box['info1'].setText(msg)


def main():
    app = QApplication([])
    nfts = NFTs()
    nfts.token_group = 'WAIFU'
    nfts.get_nfts()
    ex = PyQtLayout(nfts.group_ids)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
