import sqlite3

CON = sqlite3.connect(':memory:')
CON.isolation_level = None

SCHEMA = [(
    'CREATE TABLE nfts '
    '(name text'
    ',token_id text'
    ',price number NULL'
    ',price_bch number NULL'
    ',is_sold boolean '
    ',is_for_sale boolean'
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

        for nft in nfts_groups:
            sql = (
                "INSERT INTO nfts "
                "(name, token_id, price, price_bch, is_sold, is_for_sale) "
                "values (?, ?, ?, ?, ?, ?)"
            )
            try:
                self.db_cursor.execute(sql, (
                    nfts_groups[nft][-1].name,
                    nft,
                    nfts_groups[nft][-1].price_satoshis,
                    nfts_groups[nft][-1].price_bch,
                    nfts_groups[nft][-1].is_sold,
                    nfts_groups[nft][-1].is_for_sale
                ))
            except BaseException:
                print(sql)
                raise

            for nft_info in nfts_groups[nft]:
                sql = (
                    "INSERT INTO nft_info "
                    "(token_id, price, price_bch, is_sold, is_for_sale)"
                    " values "
                    "(?, ?, ?, ?, ?)"
                )
                try:
                    self.db_cursor.execute(sql, (nft_info.token_id,
                                                 nft_info.price_satoshis,
                                                 nft_info.price_bch,
                                                 nft_info.is_sold,
                                                 nft_info.is_for_sale))
                except BaseException:
                    print(sql)
                    raise

    def get_nfts(self):
        sql = (
            'select name, token_id, price_bch, is_sold, is_for_sale'
            ' from nfts order by name'
        )
        return self.db_cursor.execute(sql).fetchall()

    def get_nft_history(self, token_id, only_one=False, is_sold=False,
                        is_for_sale=False, order_by='desc'):
        sql = (
            "select price, price_bch, is_sold, is_for_sale from nft_info "
            " where token_id = '{}' "
        )
        if is_sold:
            sql += " AND is_sold = 1"

        if is_for_sale:
            sql += "  AND is_for_sale = 1"

        sql += " order by price {}".format(order_by)

        try:
            if only_one:
                return self.db_cursor.execute(sql.format(token_id)).fetchone()

            return self.db_cursor.execute(sql.format(token_id))
        except BaseException:
            print(sql)
            raise
