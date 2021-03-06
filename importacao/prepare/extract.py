from helpers import *

''' Extract CSV file by year'''
def extract(year):

    source_file = 'dados/importacao/raw/' + 'MDIC_' + str(year) + '.csv'
    export_file = 'dados/importacao/sent/' + str(year) + '_extract.csv'

    cols = ('ANO', 'MES', 'PAIS', 'ESTADO', 'PORTO', 'MUNICIPIO', 'UNIDADE', 'QUANTIDADE', 'KGLIQUIDO', 'VALORFOB', 'HS2007')

    df = read_from_csv(source_file, 1,"|", cols, None)

    df_to_csv(df, export_file, None)

    print df

if __name__ == '__main__':
    for x in xrange(2002, 2011):
        print "execute year: " + str(x)
        extract(x)
