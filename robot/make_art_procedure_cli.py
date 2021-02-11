import os

from .art_processor import make_procedure
from .processor_args import args

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
if not SQLALCHEMY_DATABASE_URI:
    SQLALCHEMY_DATABASE_URI = input('Enter Database Url: ')

num_pieces = 0
while num_pieces not in range(1,10):
    try:
        num_pieces = int(input("How much art? (1-9) "))
    except:
        num_pieces = 0

msg, file_loc = make_procedure(None
                              ,SQLALCHEMY_DATABASE_URI
                              ,num_pieces
                              ,args
                              )

print('\n'.join(msg))
pritn(f'Procedure location: {file_loc[0]}/{file_loc[1]}')