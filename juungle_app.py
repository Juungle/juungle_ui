"Module Juungle App"
import sys
import os

from datetime import datetime
import tempfile
import requests
from PyQt5.QtWidgets import QMainWindow, QComboBox  # pylint: disable= no-name-in-module
from PyQt5.QtWidgets import QApplication, QGridLayout  # pylint: disable= no-name-in-module

from PyQt5.QtWidgets import QLabel, QCompleter, QLineEdit, QWidget  # pylint: disable= no-name-in-module

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout  # pylint: disable= no-name-in-module

from PyQt5.QtGui import QPixmap  # pylint: disable= no-name-in-module

from PyQt5.QtCore import Qt  # pylint: disable= no-name-in-module


from nft import NFTDB
from juungle.nft import NFTs  # pylint: disable=import-error
from juungle import __version__ as juungle_version


CACHE_DIR_PATH = '{}/juungle-cache'.format(tempfile.gettempdir())
VERSION = '0.5.2'

MIN_JUUNGLE_VERSION = '0.6.2'


def version_tuple(version):
    """Convert string into version"""
    return tuple(map(int, version.split('.')))


if version_tuple(juungle_version) < version_tuple(MIN_JUUNGLE_VERSION):
    MSG = ('Juungle package should be higher than {}. Package version is'
           ' {}. \nRun "python3 -m pip install -U juungle"')
    print(MSG.format(MIN_JUUNGLE_VERSION, juungle_version))
    sys.exit(1)


def cache_exists(file_id):
    """
    Check if the file already exists.
    """
    if not os.path.isdir(CACHE_DIR_PATH):
        os.mkdir(CACHE_DIR_PATH)

    return os.path.isfile('{}/{}'.format(CACHE_DIR_PATH, file_id))


class PyQtLayout(QMainWindow):
    def __init__(self, nfts):
        super().__init__()
        self.nfts = NFTDB(nfts)
        self.info_nfts = nfts
        self.initUI()
        self.id_names = {}
        title = ('Juungle.net UI v{} BETA '
                 '- Last update: {}').format(VERSION, datetime.now())

        self.setWindowTitle(title)

    def initUI(self):
        """initUI"""
        widget = QWidget()

        # main_menu = self.menuBar()
        # main_menu.addMenu('Options')

        vbox = QVBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Search by name...')
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

        def add_combo(label, items):
            hbox = QHBoxLayout()
            l_label = QLabel(label)
            l_label.adjustSize()
            hbox.addWidget(l_label)
            combo = QComboBox(widget)

            for i in items:
                combo.addItem(i[0], i[1])
            combo.currentIndexChanged.connect(self.update_options)
            hbox.addWidget(combo)

            return hbox, combo

        hbox, self.own_nft = add_combo(
            'Types',
            [('All', None), ('Only mine', True), ('Not mine', False)]
        )
        vbox.addLayout(hbox)

        hbox, self.options = add_combo(
            'For sale?',
            [('All', None), ('For Sale', None), ('Sold/Not for sale', None)]
        )
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        l_label = QLabel('NFT Group')
        hbox.addWidget(l_label)
        self.cb_group = QComboBox(widget)
        self.update_group_cb()
        self.cb_group.currentIndexChanged.connect(self.update_options)
        hbox.addWidget(self.cb_group)
        vbox.addLayout(hbox)

        filter_gb = QGroupBox('Filters')
        filter_gb.setLayout(vbox)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        l_label = QLabel('NFT name:')
        hbox.addWidget(l_label)
        self.lbl_n_nfts = QLabel('')
        hbox.addWidget(self.lbl_n_nfts)
        self.cb_nfts = QComboBox(widget)
        self.cb_nfts.currentIndexChanged.connect(self.update_image)
        hbox.addWidget(self.cb_nfts)
        vbox.addLayout(hbox)

        self.lbl_image = QLabel(widget)
        vbox.addWidget(self.lbl_image)
        image_gb = QGroupBox('Image')
        image_gb.setLayout(vbox)

        vbox = QVBoxLayout()
        self.info_box = {
            "name": QLabel('NFTName', widget),
            "price": QLabel('Price', widget),
            "price_history": QLabel('', widget),
        }
        self.info_box['price_history'].setFixedWidth(200)

        vbox.addWidget(self.info_box['name'])
        vbox.addWidget(self.info_box['price'])
        vbox.addWidget(self.info_box['price_history'])
        info_gb = QGroupBox('Info')
        info_gb.setLayout(vbox)

        main_grid = QGridLayout(widget)
        main_grid.addWidget(filter_gb, 0, 0)
        main_grid.addWidget(image_gb, 0, 1)
        main_grid.addWidget(info_gb, 0, 2)

        widget.setLayout(main_grid)

        self.setCentralWidget(widget)

        self.update_options(0)
        self.show()

    def update_search(self):
        self.cb_nfts.setCurrentText(self.search_edit.text())
        self.search_edit.clear()

    def update_search_price(self):
        self.update_options(self.options.currentIndex())

    def update_group_cb(self):
        self.cb_group.clear()
        self.cb_group.addItem('All', None)
        for group in self.nfts.get_groups():
            self.cb_group.addItem(group[0], group[1])

    def update_options(self, _):
        self.cb_nfts.clear()
        self.id_names = {}
        self.search_edit.clear()
        cb_index = self.options.currentIndex()

        for nft in self.nfts.get_nfts(mine=self.own_nft.currentData(),
                                      group_id=self.cb_group.currentData()):
            if cb_index == 0:
                prices_nft = self.nfts.get_nft_history(nft[1], True)
                price_bch = prices_nft[1]

                if self.min_value.text():
                    if not price_bch or price_bch and \
                            price_bch <= float(self.min_value.text()):
                        continue
                if self.max_value.text():
                    if not price_bch or price_bch and \
                            price_bch >= float(self.max_value.text()):
                        continue

                self.id_names[nft[0]] = nft[1]

            if cb_index == 1:
                if not nft[4]:
                    continue
                prices_nft = self.nfts.get_nft_history(nft[1], True)
                price_bch = prices_nft[1]

                if self.min_value.text():
                    if not price_bch or price_bch and \
                            price_bch <= float(self.min_value.text()):
                        continue

                if self.max_value.text():
                    if not price_bch or price_bch and \
                            price_bch >= float(self.max_value.text()):
                        continue

                self.id_names[nft[0]] = nft[1]

            if cb_index == 2:
                if not nft[3]:
                    continue
                self.id_names[nft[0]] = nft[1]

        names = sorted(self.id_names.keys())

        completer = QCompleter(names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.search_edit.setCompleter(completer)

        for i in names:
            self.cb_nfts.addItem(i, self.id_names[i])

        msg = "1/{} listed".format(len(names))
        self.lbl_n_nfts.setText(msg)
        self.cb_nfts.setFocus()

    def update_image(self, index):
        pixmap = QPixmap()
        nft = None

        for i in self.info_nfts:
            nft = self.info_nfts[i][-1]
            if self.cb_nfts.itemData(index) == i:
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

        img_height = 500
        pixmap_resized = pixmap
        if pixmap.height() > img_height:
            pixmap_resized = pixmap.scaledToHeight(img_height)

        self.lbl_image.setPixmap(pixmap_resized)

        self.info_box['name'].setText('Name: {}'.format(nft.name))

        if nft.price_satoshis:
            price = '{} {}'.format(nft.price_bch, 'BCH')
        else:
            price = '-'
        self.info_box['price'].setText('Price: {}'.format(price))

        msg = 'Price history: <br/><br/>'
        for n in self.nfts.get_nft_history(nft.token_id, order_by='asc'):
            if n[2]:
                msg += ('Sold for {} BCH<br/>'.format(n[1]))

            if n[3]:
                msg += ('<a href="https://juungle.net/#/assets/{}">'
                        '{}</a>{} BCH<br/>').format(
                            nft.token_id,
                            'Click to buy for ', n[1])

            self.info_box['price_history'].setText(msg)
            self.info_box['price_history'].setOpenExternalLinks(True)

        self.cb_nfts.setFixedWidth(300)
        msg = "{}/{} listed".format(index, self.cb_nfts.count())
        self.lbl_n_nfts.setText(msg)


def main():
    app = QApplication([])
    nfts = NFTs()
    nfts.get_nfts()
    ex = PyQtLayout(nfts.group_ids)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
