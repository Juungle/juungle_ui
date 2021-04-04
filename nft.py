"""Module NFT"""
import sqlite3
from juungle.user import User


CON = sqlite3.connect(':memory:')
CON.isolation_level = None

SCHEMA = [(
    'CREATE TABLE nfts '
    '(name text'
    ',token_id text'
    ',user_id'
    ',price number NULL'
    ',price_bch number NULL'
    ',is_sold boolean '
    ',is_for_sale boolean'
    ',group_id text'
    ',token_symbol text'
    '); '),
    ('CREATE TABLE nft_info '
     '(token_id text'
     ',price number NULL'
     ',price_bch number NULL'
     ',is_sold boolean '
     ',is_for_sale boolean'
     ');'
     )]


class NFTDB():
    def __init__(self, nfts_groups):
        self.db_cursor = CON.cursor()
        for i in SCHEMA:
            self.db_cursor.execute(i)

        l_nft = list()
        l_nft_info = list()
        for nft in nfts_groups:
            l_nft.append((
                nfts_groups[nft][-1].name,
                nft,
                nfts_groups[nft][-1].user_id,
                nfts_groups[nft][-1].price_satoshis,
                nfts_groups[nft][-1].price_bch,
                nfts_groups[nft][-1].is_sold,
                nfts_groups[nft][-1].is_for_sale,
                nfts_groups[nft][-1].group_tokenid,
                nfts_groups[nft][-1].token_symbol
            ))
            for nft_info in nfts_groups[nft]:
                l_nft_info.append((
                    nft_info.token_id,
                    nft_info.price_satoshis,
                    nft_info.price_bch,
                    nft_info.is_sold,
                    nft_info.is_for_sale
                ))

        sql = (
            "INSERT INTO nfts "
            "(name, token_id, user_id, price, price_bch, "
            "is_sold, is_for_sale, group_id, token_symbol) "
            "values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        try:
            self.db_cursor.executemany(sql, l_nft)
        except BaseException:
            print(sql)
            raise

        sql = (
            "INSERT INTO nft_info "
            "(token_id, price, price_bch, is_sold, is_for_sale "
            ")"
            " values "
            "(?, ?, ?, ?, ?)"
        )
        try:
            self.db_cursor.executemany(sql, l_nft_info)
        except BaseException:
            print(sql)
            raise

    def get_groups(self):
        sql = (
            'SELECT token_symbol, group_id from '
            'nfts group by token_symbol '
            ' order by token_symbol')

        return self.db_cursor.execute(sql).fetchall()

    def get_nfts(self, mine=None, group_id=None):
        sql = 'select name, token_id, price_bch, is_sold, is_for_sale'
        sql += ' from nfts '

        if mine is not None or group_id is not None:
            sql += ' WHERE 1'

        if mine is not None:
            user = User()
            if mine:
                sql += ' AND user_id = {}'.format(user.user_id)
            else:
                sql += ' AND user_id <> {}'.format(user.user_id)

        if group_id:
            sql += " AND group_id = '{}'".format(group_id)

        sql += ' order by name'

        return self.db_cursor.execute(sql).fetchall()

    def get_nft_history(self, token_id, only_one=False, is_sold=False,
                        is_for_sale=False, order_by='desc'):
        sql = (
            "select price, price_bch, is_sold, is_for_sale from nft_info "
            " where token_id = '{}' "
        )
        if is_sold:
            sql += " AND (is_sold = 1 OR is_sold is NULL) "

        if is_for_sale:
            sql += "  AND is_for_sale = 1"

        sql += " order by price {}".format(order_by)

        try:
            if only_one:
                return self.db_cursor.execute(sql.format(token_id)).fetchone()

            return self.db_cursor.execute(sql.format(token_id)).fetchall()
        except BaseException:
            print(sql)
            raise
