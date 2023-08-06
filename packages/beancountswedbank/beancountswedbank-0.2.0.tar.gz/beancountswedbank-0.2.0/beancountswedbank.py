#!/usr/bin/env python3
"""Beancount importer for Swedbanken"""

import datetime
import csv
import re
from decimal import Decimal

from beancount.ingest import importer
from beancount.core import data
from beancount.core.amount import Amount


VERSION = '0.2.0'


class CSVImporter(importer.ImporterProtocol):
    """The actual importer protocol for CSV exported reports from Swedbanken online banking"""
    ENCODING = 'iso-8859-15'
    HEAD = re.compile(r'^\* Transaktioner Period ([0-9]{4}-[0-9]{2}-[0-9]{2}).([0-9]{4}-[0-9]{2}-[0-9]{2}) Skapad ([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}) ([+-][0-9]{2}:[0-9]{2}|CES?T)$')

    FIELDS = ['Radnummer',
              'Clearingnummer',
              'Kontonummer',
              'Produkt',
              'Valuta',
              'Bokföringsdag',
              'Transaktionsdag',
              'Valutadag',
              'Referens',
              'Beskrivning',
              'Belopp',
              ]

    def __init__(self, accounts, *args, encoding=None, **kwargs):
        self.accounts = accounts
        self.encoding = encoding or CSVImporter.ENCODING
        super().__init__(*args, **kwargs)

    def name(self):
        return "SwebankImporter.vonshednob.cc"

    def file_date(self, file):
        with open(file.name, 'rt', encoding=self.encoding) as fd:
            match = CSVImporter.HEAD.match(fd.readline())
            if not match:
                raise RuntimeError()

            return datetime.datetime.strptime(match.group(3), "%Y-%m-%d").date()

    def file_account(self, file):
        with open(file.name, 'rt', encoding=self.encoding) as fd:
            fd.readline()
            fd.readline()
            reader = csv.reader(fd, delimiter=',', quotechar='"')
            for row in reader:
                return self.accounts.get(row[4], None)
            return None

    def identify(self, file):
        with open(file.name, 'rt', encoding=self.encoding) as fd:
            try:
                line = fd.readline()
                if not CSVImporter.HEAD.match(line):
                    return False
            except:
                pass

            line = fd.readline().strip()
            return line.startswith(','.join(CSVImporter.FIELDS))

    def extract(self, file_, *_):
        transactions = []
        with open(file_.name, 'rt', encoding=self.encoding) as fd:
            fd.readline()
            reader = csv.DictReader(fd, delimiter=',', quotechar='"')
            for lineno, row in enumerate(reader):
                meta = data.new_metadata(file_.name, lineno+2)
                date = datetime.datetime.strptime(row['Valutadag'], "%Y-%m-%d").date()
                account = self.accounts.get(row['Produkt'], None)
                amount = Amount(Decimal(row['Belopp']), row['Valuta'])
                payee = None
                links = set()
                tags = set()
                narration = row['Beskrivning'].lower()
                if row['Referens'].lower() != row['Beskrivning'].lower():
                    narration += " " + row['Referens'].lower()
                postings = [
                    data.Posting(account,
                                 amount,
                                 None,  # cost
                                 None,  # price
                                 None,  # flag
                                 None,  # meta
                                 )
                ]
                transaction = data.Transaction(meta,
                                               date,
                                               '*',
                                               payee,
                                               narration.title(),
                                               tags,
                                               links,
                                               postings)
                transactions.append(transaction)
        return transactions
