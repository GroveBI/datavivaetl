from helpers import *
import re
import os
""" Extract RAIS database. Maps and conversions

The separation is done every year, because Python needs to have an accuracy in headers, 
which does not happen with qlkview. So the extraction is done every year by applying the specific maps.


MapRetiraTextosLixo:
df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLAS CNAE']= ''
df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLASSE']= ''
df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLASS']= ''
df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLAS']= ''
df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CBO']= ''
df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == '0000-1']= '-1'

MapInstrucao:
df['Escolaridade após 2005'] [df['Escolaridade após 2005'] == 10]= 9
df['Escolaridade após 2005'] [df['Escolaridade após 2005'] == 11]= 9

MapGenero:
df['SEXO_Fonte'] [df['SEXO_Fonte'] == "MASCULINO"]= 1
df['SEXO_Fonte'] [df['SEXO_Fonte'] == "FEMININO"]= 0
df['SEXO_Fonte'] [df['SEXO_Fonte'] == "2" ]= 0
df['SEXO_Fonte'] [df['SEXO_Fonte'] == "02" ]= 0
df['SEXO_Fonte'] [df['SEXO_Fonte'] == "01" ]= 1

Map Tamanho Estabelecimento:
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "1"]= "1"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "2"]= "1"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "3"]= "2"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "4"]= "3"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "5"]= "4"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "6"]= "5"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "7"]= "6"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "8"]= "7"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "9"]= "8"
df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "10"]= "9"

MapCor:
df['Raça Cor'] [df['Raça Cor'] == 99 ] = -1

MapIgnorado:
cbo['CBO94'] [cbo['CBO94'] == "IGNORADO"]= '-1'
cbo['CBO94'] = cbo.apply(lambda f: to_int(f['CBO94']) , axis = 1)
cbo['CBO2002'] = cbo.apply(lambda f: to_int(f['CBO2002']) , axis = 1)

"""
#####

""" Open file to CBO conversion"""
def openCBO94x2002():
    return read_from_csv('docs/classificacao/CBO/Conversion_CBO94_CBO2002.csv', 1, ';', ['CBO94', 'CBO2002'])

""" Open File for CNAE conversion"""
def openCNAE10x20():
    return read_from_csv('docs/classificacao/CNAE/CNAE20_Correspondencia10x20.csv', 1, ';', ['CNAE 10', 'CNAE 20'], converters={'CNAE 20':int, 'CNAE 10':int})

""" Extract CSV file by year """
def extract(year):

    if year == 2002:

        source_file = 'dados/rais/raw/' + str(year) + '/' + 'RAIS2002TOTAL_CORTE' + '.txt'

        cols =  ('CAUSA DESLI', 'CAUSA DESLI_Fonte', 'OCUPACAO', 'OCUPACAO_desc', 'IND CEI VINC', 'CLAS CNAE 95', 'CLAS CNAE 95_Fonte', 'GRAU INSTR', 'GRAU INSTR_Fonte', 'HORAS CONTR', 'IDADE', 'IDENTIFICAD', 'IND PAT', 'IND PAT_Fonte', 'IND SIMPLES', 'IND SIMPLES_Fonte', 'MUNICIPIO', 'MUNICIPIO_Fonte', 'NACIONALIDAD', 'NACIONALIDAD_Fonte', 'NATUR JUR', 'NATUR JUR_Fonte', 'PIS', 'RACA_COR OR', 'RACA_COR OR_Fonte', 'RADIC CNPJ', 'REM DEZ (R$)', 'REM DEZEMBRO', 'REM MED (R$)', 'SUBS IBGE', 'SEXO', 'SEXO_Fonte', 'TAMESTAB', 'TAMESTAB_Fonte', 'TEMP EMPR', 'TIPO ADM', 'TIPO ADM_Fonte', 'TIPO ESTBL', 'TIPO ESTBL_Fonte', 'TP VINCL', 'DT NASCIMENT', 'MES DESLIG', 'MES DESLIG_Fonte', 'DT ADMISSAO' )

        useCols = ('OCUPACAO', 'CLAS CNAE 95_Fonte', 'GRAU INSTR_Fonte', 'IDADE', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR OR_Fonte', 'REM DEZ (R$)', 'REM MED (R$)', 'SEXO_Fonte', 'TAMESTAB_Fonte')

        separator = "|"

        df = read_from_csv(source_file, 1, separator, cols, None, useCols)


        """ Convert CBO094 to CBO2002 """
        cbo = openCBO94x2002()

        # MapIgnorado
        cbo['CBO94'] [cbo['CBO94'] == "IGNORADO"]= '-1'
        cbo['CBO94'] = cbo.apply(lambda f: to_int(f['CBO94']) , axis = 1)
        cbo['CBO2002'] = cbo.apply(lambda f: to_int(f['CBO2002']) , axis = 1)


        """ Make CBO Conversion """
        def CBOConversion(row):
            converted = cbo['CBO2002'][cbo['CBO94'] == row['OCUPACAO']]

            if len(converted) > 1:
                return int(converted.head(1))

            return int(converted)

        # MapRetiraTextosLixo
        df['OCUPACAO'] [df['OCUPACAO'] == "CLAS CNAE"]= ''
        df['OCUPACAO'] [df['OCUPACAO'] == "CLASSE"]= ''
        df['OCUPACAO'] [df['OCUPACAO'] == "CLASS"]= ''
        df['OCUPACAO'] [df['OCUPACAO'] == "CLAS"]= ''
        df['OCUPACAO'] [df['OCUPACAO'] == "CBO"]= ''
        df['OCUPACAO'] [df['OCUPACAO'] == "0000-1"]= -1

        """ remove string from field OCUPACAO (CBO)"""
        df['OCUPACAO'] = df.apply(lambda f : re.findall('\d+', f['OCUPACAO'])[0], axis = 1)

        df['OCUPACAO'] = df.apply(lambda f : to_number(f['OCUPACAO']), axis = 1)

        df['OCUPACAO'] = df.apply(CBOConversion, axis=1)

        #Make CNAE Conversion
        cnae = openCNAE10x20()

        def cnaeConversion(row):
            converted = cnae['CNAE 20'][cnae['CNAE 10'] == row['CLAS CNAE 95_Fonte']]
            if len(converted) > 0:
                return int(converted.head(1))
            return int(converted)

        df['CLAS CNAE 95_Fonte'] = df.apply(cnaeConversion, axis=1)

        df['SEXO_Fonte'] = df.apply(lambda x : str(x['SEXO_Fonte']), axis=1)

        # MapGenero
        df['SEXO_Fonte'] [df['SEXO_Fonte'] == "MASCULINO"]= 1
        df['SEXO_Fonte'] [df['SEXO_Fonte'] == "FEMININO"]= 0
        df['SEXO_Fonte'] [df['SEXO_Fonte'] == "2" ]= 0
        df['SEXO_Fonte'] [df['SEXO_Fonte'] == "02" ]= 0
        df['SEXO_Fonte'] [df['SEXO_Fonte'] == "01" ]= 1

        export_file = 'dados/rais/sent/' + str(year) + '_extractCORTE.csv'

        df_to_csv(df, export_file, None)

    elif year == 2003:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO 2002_Fonte', 'CLAS CNAE 95_Fonte', 'GRAU INSTR_Fonte', 'IDADE', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR_Fonte', 'REM DEZ (R$)', 'REM MED (R$)', 'SEXO_Fonte', 'TAMESTAB_Fonte')

            cols = ('CAUSA DESLIG', 'CAUSA DESLIG_Fonte', 'CBO 2002', 'CB0 2002_fonte', 'CEI VINC', 'CLAS CNAE 95', 'CLAS CNAE 95_Fonte', 'EMP  EM 31/12', 'EMP EM 31/12_Fonte', 'GRAU INSTR', 'GRAU INSTR_Fonte', 'HORAS CONTR', 'IDADE', 'IDENTIFICAD', 'IND CEI VINC', 'IND CEI VINC_Fonte', 'IND PAT', 'IND PAT_Fonte', 'IND SIMPLES', 'IND SIMPLES_Fonte', 'MUNICIPIO', 'MUNICIPIO_Fonte', 'NACIONALIDAD', 'NACIONALIDAD_Fonte', 'NATUR JUR', 'NATUR JUR_Fonte', 'PIS', 'RACA_COR', 'RACA_COR_Fonte', 'RADIC CNPJ', 'REM DEZ (R$)', 'REM DEZEMBRO', 'REM MED (R$)', 'REM MEDIA', 'SUBS IBGE', 'SEXO', 'SEXO_Fonte', 'TAMESTAB', 'TAMESTAB_Fonte', 'TEMP EMPR', 'TIPO ADM', 'TIPO ADM_Fonte', 'TIPO ESTBL', 'TIPO ESTBL_Fonte', 'TP VINCULO', 'TP VINCULO_Fonte', 'DT NASCIMENT', 'DT_ADMISSAO', 'MES DESLIG', 'MES DESLIG_Fonte')


            df = read_from_csv(source_file, 2,"|", cols, None, useCols)

            #Make CNAE Conversion
            cnae = openCNAE10x20()

            def cnaeConversion(row):
                converted = cnae['CNAE 20'][cnae['CNAE 10'] == row['CLAS CNAE 95_Fonte']]
                if len(converted) > 0:
                    return int(converted.head(1))
                return int(converted)

            df['CLAS CNAE 95_Fonte'] = df.apply(cnaeConversion, axis=1)

            df['SEXO_Fonte'] = df.apply(lambda x : str(x['SEXO_Fonte']), axis=1)

            # MapGenero
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "MASCULINO"]= 1
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "FEMININO"]= 0
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "2" ]= 0
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "02" ]= 0
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "01" ]= 1

            export_file = 'dados/rais/sent/' + str(year) + '_extract.csv'

            df_to_csv(df, export_file, None)


    elif year == 2004:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO 2002_Fonte', 'CLAS CNAE 95_Fonte', 'GRAU INSTR_Fonte', 'IDADE', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR_Fonte', 'REM DEZ (R$)', 'REM MED (R$)', 'SEXO_Fonte', 'TAMESTAB_Fonte')

            cols = ('MUNICIPIO', 'CLAS CNAE 95', 'EMP EM 31/12', 'TP VINCULO', 'CAUSA DESLIG', 'MES DESLIG', 'IND ALVARA', 'TIPO ADM', 'TIPO SAL', 'OCUPACAO 94', 'GRAU INSTR', 'SEXO', 'NACIONALIDAD', 'RACA_COR', 'PORT DEFIC', 'TAMESTAB', 'NATUR JUR', 'IND CEI VINC', 'TIPO ESTBL', 'IND PAT', 'IND SIMPLES', 'DT ADMISSAO', 'REM MED ($)', 'REM DEZ ($)', 'TEMP EMPR', 'HORAS CONTR', 'ULT REM', 'SAL CONTR', 'PIS', 'DT NASCIMENT', 'NUME CTPS', 'CPF', 'CEI VINC', 'IDENTIFICAD', 'RADIC CNPJ', 'TIPO ESTB ID', 'NOME', 'DIA DESL', 'OCUP 2002')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)

            #Make CNAE Conversion
            cnae = openCNAE10x20()

            def cnaeConversion(row):
                converted = cnae['CNAE 20'][cnae['CNAE 10'] == row['CLAS CNAE 95_Fonte']]
                if len(converted) > 0:
                    return int(converted.head(1))
                return int(converted)

            df['CLAS CNAE 95_Fonte'] = df.apply(cnaeConversion, axis=1)

            df['SEXO_Fonte'] = df.apply(lambda x : str(x['SEXO_Fonte']), axis=1)

            # MapGenero
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "MASCULINO"]= 1
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "FEMININO"]= 0
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "2" ]= 0
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "02" ]= 0
            df['SEXO_Fonte'] [df['SEXO_Fonte'] == "01" ]= 1

            export_file = 'dados/rais/sent/' + str(year) + '_extract.csv'

            df_to_csv(df, export_file, None)

    elif year == 2005:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO 2002_Fonte', 'CLAS CNAE 95_Fonte', 'GRAU INSTR_Fonte', 'IDADE', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR_Fonte', 'REM DEZ (R$)', 'REM MED (R$)', 'GENERO', 'TAMESTAB_Fonte')

            cols = ('MUNICIPIO', 'CLAS CNAE 95', 'EMP EM 31/12', 'TP VINCULO', 'CAUSA DESLIG', 'MES DESLIG', 'IND ALVARA', 'TIPO ADM', 'TIPO SAL', 'OCUPACAO 94', 'GRAU INSTR', 'GENERO', 'NACIONALIDAD', 'RACA_COR', 'PORT DEFIC', 'TAMESTAB', 'NATUR JUR', 'IND CEI VINC', 'TIPO ESTBL', 'IND PAT', 'IND SIMPLES', 'DT ADMISSAO', 'REM MEDIA', 'REM MED ($)', 'REM DEZEMBRO', 'REM DEZ (R$)' 'TEMP EMPR', 'HORAS CONTR', 'ULT REM', 'SAL CONTR', 'PIS', 'DT NASCIMENT', 'NUME CTPS', 'CPF', 'CEI VINC', 'IDENTIFICAD', 'RADIC CNPJ', 'TIPO ESTB ID', 'NOME', 'DIA DESL', 'OCUP 2002')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)

            """ CNAE CONVERSION """
            def cnaeConversion(row):
                converted = cnae['CNAE 20'][cnae['CNAE 10'] == row['CLAS CNAE 95_Fonte']]
                if len(converted) > 1:
                    converted = converted.head(1)

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['GENERO'] [df['GENERO'] == "MASCULINO"]= 1
            df['GENERO'] [df['GENERO'] == "FEMININO"]= 0
            df['GENERO'] [df['GENERO'] == "2" ]= 0
            df['GENERO'] [df['GENERO'] == "02" ]= 0
            df['GENERO'] [df['GENERO'] == "01" ]= 1

            df['CLAS CNAE 95_Fonte'] = df.apply(cnaeConversion, axis=1)


            df_to_csv(df, export_file, None)

    elif year == 2006:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO 2002_Fonte', 'CLAS CNAE 95_Fonte', 'GRAU INSTR_Fonte', 'IDADE', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR_Fonte', 'REM DEZ (R$)', 'REM MED (R$)', 'GENERO', 'TAMESTAB_Fonte')

            cols = ('MUNICIPIO', 'CLAS CNAE 95', 'EMP EM 31/12', 'TP VINCULO', 'CAUSA DESLIG', 'MES DESLIG', 'IND ALVARA', 'TIPO ADM', 'TIPO SAL', 'OCUPACAO 94', 'GRAU INSTR', 'GENERO', 'NACIONALIDAD', 'RACA_COR', 'PORT DEFIC', 'TAMESTAB', 'NATUR JUR', 'IND CEI VINC', 'TIPO ESTBL', 'IND PAT', 'IND SIMPLES', 'DT ADMISSAO', 'REM MEDIA', 'REM MED (R$)', 'REM DEZEMBRO', 'REM DEZ (R$)', 'TEMP EMPR', 'HORAS CONTR', 'ULT REM', 'SAL CONTR', 'PIS', 'DT NASCIMENTO', 'NUME CTPS', 'CPF', 'CEI VINC', 'IDENTIFICAD', 'RADIC CNPJ', 'TIPO ESTAB ID', 'NOME', 'DIA DESLIG', 'OCUP 2002', 'CLAS CNAE 20', 'SB CLAS 20', 'TP DEFIC')


            df = read_from_csv(source_file, 2,";", cols, None, useCols)

            """Map instrucao"""
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 10]= 9
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 11]= 9

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['GENERO'] [df['GENERO'] == "MASCULINO"]= 1
            df['GENERO'] [df['GENERO'] == "FEMININO"]= 0
            df['GENERO'] [df['GENERO'] == "2" ]= 0
            df['GENERO'] [df['GENERO'] == "02" ]= 0
            df['GENERO'] [df['GENERO'] == "01" ]= 1

            df['CLAS CNAE 95_Fonte'] = df.apply(cnaeConversion, axis=1)

            df_to_csv(df, export_file, None)

    elif year == 2007:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            cols = ('MUNICIPIO', 'CLAS CNAE 95', 'EMP EM 31/12', 'TP VINCULO', 'CAUSA DESLI', 'MES DESLIG', 'IND ALVARA', 'TIPO ADM', 'TIPO SAL', 'OCUPACAO 94', 'GR INSTRUCAO', 'GENERO', 'NACIONALIDAD', 'RACA_COR', 'PORT DEFIC', 'TAMESTAB', 'NATUR JUR', 'IND CEI VINC', 'TIPO ESTBL', 'IND PAT', 'IND SIMPLES', 'DT ADMISSAO', 'REM DEZ (R$)', 'REM DEZEMBRO', 'REM MED (R$)', 'REM MEDIA', 'TEMP EMPR', 'HORAS CONTR', 'ULT REM', 'SAL CONTR', 'PIS', 'DT_NASCIMENT', 'NUME CTPS', 'CPF', 'CEI VINC', 'IDENTIFICAD', 'RADIC CNPJ', 'TIPO ESTB ID', 'NOME',  'OCUP 2002', 'CLAS CNAE 20', 'SB CLAS 20', 'TP DEFIC', 'CAU AFAST 1', 'DIA INI AF 1', 'DIA INI AF 1', 'MES INI AF 1', 'DIA FIM AF 1', 'MES FIM AF 1', 'CAUS AFAST 2', 'DIA INI AF 2', 'MES INI AF 2', 'DIA FIM AF 2', 'MES FIM AF 2', 'CAUS AFAST 3', 'DIA INI AF 3', 'MES INI AF 3', 'DIA FIM AF 3', 'MES FIM AF 3', 'QT DIAS AFAS', 'IDADE')

            useCols = ('OCUP 2002', 'CLAS CNAE 20', 'GR INSTRUCAO', 'EMP EM 31/12', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR_Fonte', 'REM DEZ (R$)', 'REM MED (R$)', 'GENERO', 'TAMESTAB_Fonte')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)

            def toStringOcup(row):
                return str(row['OCUP 2002'])

            df['OCUP 2002'] = df.apply(toStringOcup, axis=1)
            df['OCUP 2002'] [cbo['OCUP 2002'] == "IGNORADO"]= '-1'

            """Map instrucao"""
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 10]= 9
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 11]= 9

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['GENERO'] [df['GENERO'] == "MASCULINO"]= 1
            df['GENERO'] [df['GENERO'] == "FEMININO"]= 0
            df['GENERO'] [df['GENERO'] == "2" ]= 0
            df['GENERO'] [df['GENERO'] == "02" ]= 0
            df['GENERO'] [df['GENERO'] == "01" ]= 1

            df['CLAS CNAE 95_Fonte'] = df.apply(cnaeConversion, axis=1)


            df_to_csv(df, export_file, None)

    elif year == 2008:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO 2002_Fonte', 'CLAS CNAE 20_Fonte', 'GR INSTRUCAO_Fonte', 'IDADE', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR', 'REM DEZ (R$)', 'REM MED (R$), GENERO', 'TAMESTAB_Fonte' )

            cols = ('MUNICIPIO', 'CLAS CNAE 95', 'EMP EM 31/12', 'TP VINCULO', 'CAUSA DESLIG', 'IND ALVARA', 'TIPO ADM', 'TIPO SAL', 'OCUPACAO 94', 'GRAU INSTR', 'GENERO', 'NACIONALIDAD', 'RACA_COR', 'PORT DEFIC', 'TAMESTAB', 'NAT JURIDICA', 'IND CEI VINC', 'TIPO ESTBL', 'IND PAT', 'IND SIMPLES', 'DT ADMISSAO', 'REM MEDIA', 'REM MED (R$)', 'REM DEZEMBRO', 'REM DEZ (R$)', 'TEMP EMPR', 'HORAS CONTR', 'ULT REM', 'SAL CONTR', 'PIS', 'DT NASCIMENT', 'NUME CTPS', 'CPF', 'CEI VINC', 'IDENTIFICAD', 'RADIC CNPJ', 'TIPO ESTB ID', 'NOME', 'DIA DESL', 'OCUP 2002', 'CLAS CNAE 20', 'SB CLAS 20', 'TP DEFIC', 'CAUS AFAST 1', 'DIA INI AF 1', 'MES INI AF 1', 'DIA FIM AF 1', 'MES FIM AF 1', 'CAUS AFAST 2', 'DIA INI AF 2', 'MES INI AF 2', 'DIM FIM AF 2', 'MES FIM AF 2', 'CAUS AFAST 3', 'DIA INI AF 3', 'MES INI AF 3', 'DIA FIM AF 3', 'MES FIM AF 3', 'QT DIAS AFAS')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)

            """Map instrucao"""
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 10]= 9
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 11]= 9

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['GENERO'] [df['GENERO'] == "MASCULINO"]= 1
            df['GENERO'] [df['GENERO'] == "FEMININO"]= 0
            df['GENERO'] [df['GENERO'] == "2" ]= 0
            df['GENERO'] [df['GENERO'] == "02" ]= 0
            df['GENERO'] [df['GENERO'] == "01" ]= 1

            df_to_csv(df, export_file, None)

    elif year == 2009:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO 2002_Fonte', 'CLAS CNAE 20_Fonte', 'GR INSTRUCAO_Fonte', 'IDADE', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR', 'REM DEZ (R$)', 'REM MED (R$), GENERO', 'TAMESTAB_Fonte' )

            cols = ('MUNICIPIO', 'CLAS CNAE 95', 'EMP EM 31/12', 'TP VINCULO','CAUSA DESLIG', 'MES DESLIG', 'IND ALVARA', 'TIPO ADM', 'TIPO SAL', 'OCUPACAO 94', 'GR INSTRUCAO', 'GENERO', 'NACIONALIDADE', 'RACA_COR', 'PORT DEFIC', 'TAMESTAB', 'NAT JURIDICA', 'IND CEI VINC', 'TIPO ESTBL', 'IND PAT', 'IND SIMPLES', 'DT ADMISSAO', 'REM MEDIA', 'REM MED (R$)', 'REM DEZEMBRO', 'REM DEZ (R$)', 'TEMP EMPREG', 'HORAS CONTR', 'ULT REM', 'SAL CONTR', 'PIS', 'DT NASCIMENT', 'NUME CTPS', 'CPF', 'CEI VINC', 'IDENTIFICAD', 'RADIC CNPJ', 'TIPO ESTB ID', 'NOME', 'DIA DESL', 'OCUP 2002', 'CLAS CNAE 20', 'SB CLAS 20', 'TP DEFIC', 'CAU AFAST 1', 'DIA INI AF 1', 'MES INI AF 1', 'DIA FIM AF 1', 'MES FIM AF1', 'CAUS AFAST 2', 'DIA INI AF 2', 'MES INI AF 2', 'DIA FIM AF 2', 'MES FIM AF 2', 'CAUS AFAST 3', 'DIA INI AF 3', 'MES INI AF 3', 'DIA FIM AF 3', 'MES FIM AF 3', 'QT DIAS AFAS')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)

            """Map instrucao"""
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 10]= 9
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 11]= 9

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['GENERO'] [df['GENERO'] == "MASCULINO"]= 1
            df['GENERO'] [df['GENERO'] == "FEMININO"]= 0
            df['GENERO'] [df['GENERO'] == "2" ]= 0
            df['GENERO'] [df['GENERO'] == "02" ]= 0
            df['GENERO'] [df['GENERO'] == "01" ]= 1

            df_to_csv(df, export_file, None)

    elif year == 2010:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO 2002_Fonte', 'CLAS CNAE 20_Fonte', 'GR INSTRUCAO_Fonte', 'IDADE', 'IDENTIFICAD', 'IND SIMPLES_Fonte', 'MUNICIPIO_Fonte', 'PIS', 'RACA_COR', 'REM DEZ (R$)', 'REM MED (R$), GENERO', 'TAMESTAB_Fonte' )

            cols = ('MUNICIPIO', 'CLAS CNAE 95', 'EMP EM 31/12', 'TP VINCULO','CAUSA DESLIG', 'MES DESLIG', 'IND ALVARA', 'TIPO ADM', 'TIPO SAL', 'OCUPACAO 94', 'GR INSTRUCAO', 'GENERO', 'NACIONALIDADE', 'RACA_COR', 'PORT DEFIC', 'TAMESTAB', 'NAT JURIDICA', 'IND CEI VINC', 'TIPO ESTBL', 'IND PAT', 'IND SIMPLES', 'DT ADMISSAO', 'REM MEDIA', 'REM MED (R$)', 'REM DEZEMBRO', 'REM DEZ (R$)', 'TEMP EMPR', 'HORAS CONTR', 'ULT REM', 'SAL CONTR', 'DT NASCIMENT', 'NUME CTPS', 'CPF', 'CEI VINC', 'IDENTIFICAD', 'RADIC CNPJ', 'TIPO ESTB ID', 'NOME', 'DIA DESL', 'OCUP 2002', 'CLAS CNAE 20', 'SB CLAS 20', 'TP DEFIC', 'CAU AFAST 1', 'DIA INI AF 1', 'MES INI AF 1', 'DIA FIM AF 1', 'MES FIM AF1', 'CAUS AFAST 2', 'DIA INI AF 2', 'MES INI AF 2', 'DIA FIM AF 2', 'MES FIM AF 2', 'CAUS AFAST 3', 'DIA INI AF 3', 'MES INI AF 3', 'DIA FIM AF 3', 'MES FIM AF 3', 'QT DIAS AFAS')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)

            """Map instrucao"""
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 10]= 9
            df['GRAU INSTR_Fonte'] [df['GRAU INSTR_Fonte'] == 11]= 9

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['GENERO'] [df['GENERO'] == "MASCULINO"]= 1
            df['GENERO'] [df['GENERO'] == "FEMININO"]= 0
            df['GENERO'] [df['GENERO'] == "2" ]= 0
            df['GENERO'] [df['GENERO'] == "02" ]= 0
            df['GENERO'] [df['GENERO'] == "01" ]= 1

            df_to_csv(df, export_file, None)

    elif year == 2011:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO Ocupação 2002', 'CNAE 2.0 Classe', 'Escolaridade após 2005', 'Vínculo Ativo 31/12', 'Idade', 'CNPJ / CEI', 'Ind Simples', 'Município', 'PIS', 'Raça Cor', 'Vl Remun Dezembro Nom', 'Vl Remun Média Nom', 'Sexo Trabalhador', 'Tamanho Estabelecimento')

            cols = ('Município', 'CNAE 95 Classe', 'Vínculo Ativo 31/12', 'Tipo Vinculo','Motivo Desligamento', 'Mês Desligamento', 'Ind Vínculo Alvará', 'Tipo Admissão', 'Tipo Salário', 'CBO 94 Ocupação', 'Escolaridade após 2005', 'Sexo trabalhador', 'Nacionalidade', 'Raça Cor', 'Ind Portador Defic', 'Tamanho Estabelecimento', 'Natureza Jurídica', 'Ind CEI Vinculado', 'Tipo Estab', 'Ind Estab Participa PAT', 'Ind Simples', 'Data Admissão Declarada', 'Vl Remun Média Nom', 'Vl Remun Média (SM)', 'Vl Remun Dezembro Nom ', 'Vl Remun Dezembro (SM)', 'Tempo Emprego', 'Qtd Hora Contr', 'Vl Última Remuneração Ano', 'Vl Salário Contratual', 'PIS', 'Número CTPS', 'CPF', 'CEI Vinculado', 'CNPJ / CEI', 'CNPJ Raiz', 'Nome Trabalhador', 'CBO Ocupação 2002', 'CNAE 2.0 Classe', 'CNAE 2.0 Subclasse', 'Tipo Defic', 'Causa Afastamento 1', 'Dia Ini AF 1', 'Mês Ini AF1', 'Dia Fim AF1', 'Mês Fim AF1', 'Causa Afastamento 2', 'Dia Ini AF2', 'Mês Ini AF2', 'Dia Fim AF2', 'Mês Fim AF2', 'Causa Afastamento 3', 'Dia Ini AF3', 'Mês Ini AF3', 'Dia Fim AF3', 'Mês Fim AF3', 'Qtd Dias Afastamento', 'Idade')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)

            """Map textosLixo"""
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLAS CNAE']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLASSE']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLASS']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLAS']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CBO']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == '0000-1']= '-1'



            """Map instrucao"""
            df['Escolaridade após 2005'] [df['Escolaridade após 2005'] == 10]= 9
            df['Escolaridade após 2005'] [df['Escolaridade após 2005'] == 11]= 9

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "MASCULINO"]= 1
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "FEMININO"]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "2" ]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "02" ]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "01" ]= 1


            """Map Cor"""
            df['Raça Cor'] [df['Raça Cor'] == 99 ] = -1


            df_to_csv(df, export_file, None)

    elif year == 2012:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO Ocupação 2002', 'CNAE 2.0 Classe', 'Escolaridade após 2005', 'Vínculo Ativo 31/12', 'Idade', 'CNPJ / CEI', 'Ind Simples', 'Município', 'PIS', 'Raça Cor', 'Vl Remun Dezembro Nom', 'Vl Remun Média Nom', 'Sexo Trabalhador', 'Tamanho Estabelecimento')

            cols = ('Município', 'CNAE 95 Classe', 'Vínculo Ativo 31/12', 'Tipo Vinculo','Motivo Desligamento', 'Mês desligamento', 'Ind Vínculo Alvará', 'Tipo Admissão', 'Tipo Salário', 'CBO 94 Ocupação', 'Escolaridade após 2005', 'Sexo trabalhador', 'Nacionalidade', 'Raça Cor', 'Ind Portador Defic', 'Tamanho Estabelecimento', 'Natureza Jurídica', 'Ind CEI Vinculado', 'Tipo Estab', 'Ind Estab Participa PAT', 'Ind Simples', 'Data Admissão Declarada', 'Vl Remun Média Nom', 'Vl Remun Média (SM)', 'Vl Remun Dezembro Nom ', 'Vl Remun Dezembro (SM)', 'Tempo Emprego', 'Qtd Hora Contr', 'Vl Última Remuneração Ano', 'Vl Salário Contratual', 'PIS', 'Número CTPS', 'CPF', 'CEI Vinculado', 'CNPJ / CEI', 'CNPJ Raiz', 'Nome Trabalhador', 'CBO Ocupação 2002', 'CNAE 2.0 Classe', 'CNAE 2.0 Subclasse', 'Tipo Defic', 'Causa Afastamento 1', 'Dia Ini AF 1', 'Mês Ini AF1', 'Dia Fim AF1', 'Mês Fim AF1', 'Causa Afastamento 2', 'Dia Ini AF2', 'Mês Ini AF2', 'Dia Fim AF2', 'Mês Fim AF2', 'Causa Afastamento 3', 'Dia Ini AF3', 'Mês Ini AF3', 'Dia Fim AF3', 'Mês Fim AF3', 'Qtd Dias Afastamento', 'Idade')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)


            """Map textosLixo"""
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLAS CNAE']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLASSE']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLASS']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLAS']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CBO']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == '0000-1']= '-1'



            """Map instrucao"""
            df['Escolaridade após 2005'] [df['Escolaridade após 2005'] == 10]= 9
            df['Escolaridade após 2005'] [df['Escolaridade após 2005'] == 11]= 9

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "MASCULINO"]= 1
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "FEMININO"]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "2" ]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "02" ]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "01" ]= 1


            """Map Cor"""
            df['Raça Cor'] [df['Raça Cor'] == 99 ] = -1


            df_to_csv(df, export_file, None)

    elif year == 2013:

        folder = "dados/rais/raw/" + str(year) + '/'

        arr = get_files_in_folder(folder, 'TXT')

        for x in arr:

            source_file = x
            export_file =  os.path.splitext(x)[0] + '.csv'

            useCols = ('CBO Ocupação 2002', 'CNAE 2.0 Classe', 'Escolaridade após 2005', 'Vínculo Ativo 31/12', 'Idade', 'CNPJ / CEI', 'Ind Simples', 'Município', 'PIS', 'Raça Cor', 'Vl Remun Dezembro Nom', 'Vl Remun Média Nom', 'Sexo Trabalhador', 'Tamanho Estabelecimento')

            cols = ('Município', 'CNAE 95 Classe', 'Vínculo Ativo 31/12', 'Tipo Vinculo','Motivo Desligamento', 'Mês desligamento', 'Ind Vínculo Alvará', 'Tipo Admissão', 'Tipo Salário', 'CBO 94 Ocupação', 'Escolaridade após 2005', 'Sexo trabalhador', 'Nacionalidade', 'Raça Cor', 'Ind Portador Defic', 'Tamanho Estabelecimento', 'Natureza Jurídica', 'Ind CEI Vinculado', 'Tipo Estab', 'Ind Estab Participa PAT', 'Ind Simples', 'Data Admissão Declarada', 'Vl Remun Média Nom', 'Vl Remun Média (SM)', 'Vl Remun Dezembro Nom ', 'Vl Remun Dezembro (SM)', 'Tempo Emprego', 'Qtd Hora Contr', 'Vl Última Remuneração Ano', 'Vl Salário Contratual', 'PIS', 'Número CTPS', 'CPF', 'CEI Vinculado', 'CNPJ / CEI', 'CNPJ Raiz', 'Nome Trabalhador', 'CBO Ocupação 2002', 'CNAE 2.0 Classe', 'CNAE 2.0 Subclasse', 'Tipo Defic', 'Causa Afastamento 1', 'Dia Ini AF 1', 'Mês Ini AF1', 'Dia Fim AF1', 'Mês Fim AF1', 'Causa Afastamento 2', 'Dia Ini AF2', 'Mês Ini AF2', 'Dia Fim AF2', 'Mês Fim AF2', 'Causa Afastamento 3', 'Dia Ini AF3', 'Mês Ini AF3', 'Dia Fim AF3', 'Mês Fim AF3', 'Qtd Dias Afastamento', 'Idade')

            df = read_from_csv(source_file, 2,";", cols, None, useCols)


            """Map textosLixo"""
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLAS CNAE']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLASSE']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLASS']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CLAS']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == 'CBO']= ''
            df['CBO Ocupação 2002'] [df['CBO Ocupação 2002'] == '0000-1']= '-1'

            """Map instrucao"""
            df['Escolaridade após 2005'] [df['Escolaridade após 2005'] == 10]= 9
            df['Escolaridade após 2005'] [df['Escolaridade após 2005'] == 11]= 9

            def toString(row):
                return str(row['GENERO'])

            df['GENERO'] = df.apply(toString, axis=1)

            """MapGenero"""
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "MASCULINO"]= 1
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "FEMININO"]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "2" ]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "02" ]= 0
            df['Sexo Trabalhador'] [df['Sexo Trabalhador'] == "01" ]= 1

            """Map Cor"""
            df['Raça Cor'] [df['Raça Cor'] == 99 ] = -1

            """Map Tamanho Estabelecimento"""
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "1"]= "1"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "2"]= "1"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "3"]= "2"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "4"]= "3"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "5"]= "4"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "6"]= "5"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "7"]= "6"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "8"]= "7"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "9"]= "8"
            df['Tamanho Estabelecimento'] [df['Tamanho Estabelecimento'] == "10"]= "9"

            df_to_csv(df, export_file, None)


if __name__ == '__main__':
    start = time.time()
    extract(2003)
    total_run_time = time.time() - start
    print "Total runtime: " + format_runtime(total_run_time)
