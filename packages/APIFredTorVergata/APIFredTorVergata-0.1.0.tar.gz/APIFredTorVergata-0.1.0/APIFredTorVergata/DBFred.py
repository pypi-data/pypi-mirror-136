from datetime import datetime
import pandas as pd

class Datamanager:
    ''' Questa classe gestisce le interazioni tra utente e database. Permette di effettuare operazioni di scrittura, lettura e aggiornamento di determinate tabelle.'''

    def __init__(self,connection):
        ''' Costruttore della classe Datamanager.Il costruttore accetta come unico parametro la connessione con il database.
            Tale metodo crea anche una tabella nel database che memorizza tutte le operazioni che sono state effettuate.

            :param connection: connesione con il database.
        '''
        self.connection=connection

        self.category_str='Categorie'
        self.serie_str = 'Serie'
        self.osservazioni_str = 'Osservazioni'
        self.operazioni_str= 'Operazioni'
        self.scaricaCat='scarica sotto categorie da una categoria data'
        self.scaricaSer='Scarica serie da una categoria data'
        self.scaricaOss='Scarica osservazioni da una serie data'
        self.updateCat='aggiorna sotto categorie di una categoria data'
        self.updateSer='aggiorna serie di una categoria data'
        self.updateOss='aggiorna osservazioni di una serie data'
        self.analizza='Analizza osservabili'

        self.templateQuery="select * from {table} where {attribute} = '{value}'"
        self.templateOperazioni="INSERT INTO Operazioni(`tipo`,`nome`,`data`) VALUES ('{tipo}', '{nome}','{data}');"
        self.templateAllOp="select * from Operazioni"
        self.templateReadoperazioni="select * from Operazioni where tipo = '{value1}' and nome = '{value2}'"

        self.inizializeDB()


    def inizializeDB(self):
        ''' Questo metodo inizializza il database creando le 4 tabelle che conterranno le informazioni scaricate ed elaborate dagli altri metodi.
            Se le tabelle sono già esistenti non viene effettuata nessuna operazione.'''
        query=[]

        query.append( "create table if not exists Operazioni ( \
                    `tipo` enum('scarica sotto categorie da una categoria data','Scarica serie da una categoria data','Scarica osservazioni da una serie data','aggiorna sotto categorie di una categoria data','aggiorna serie di una categoria data','aggiorna osservazioni di una serie data','Analizza osservabili'),\
                    `nome` varchar(100),\
                    `data` date );")

        query.append('CREATE TABLE if not exists Categorie (' 
                 '`id` bigint(20) DEFAULT NULL,' 
                 '`name` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,' 
                 '`parent_id` bigint(20) DEFAULT NULL' 
                 ')')

        query.append('CREATE TABLE if not exists Osservazioni (' 
                  '`realtime_start` text COLLATE utf8_unicode_ci,' 
                  '`realtime_end` text COLLATE utf8_unicode_ci,' 
                  '`date` text COLLATE utf8_unicode_ci,' 
                  '`value` text COLLATE utf8_unicode_ci,' 
                  '`Serie` text COLLATE utf8_unicode_ci' 
                  ')')

        query.append('CREATE TABLE if not exists Serie ('
                 '`id` text COLLATE utf8_unicode_ci,'
                 '`title` text COLLATE utf8_unicode_ci,'
                 '`frequency` text COLLATE utf8_unicode_ci,'
                 '`observation_start` text COLLATE utf8_unicode_ci,'
                 '`observation_end` text COLLATE utf8_unicode_ci,'
                 '`Categoria` text COLLATE utf8_unicode_ci' 
                 ') ')

        for execute in query:
            self.connection.execute(execute)

    def writeSubCategoryByCategory(self, dataset,name_category,if_exists='append'):
        ''' Questo metodo permette di scrivere su una taballe sql un dataframe pandas contenente tutte le sottocategorie di una categorie data . Il metodo riceve in ingresso un dataset contenente la lista delle categorie figlie di una data categoria.

            :param dataset: Dataframe pandas da memorizzare nel database.
            :type dataset: pandas.core.frame.DataFrame
            :param name_category: nome della categoria padre
            :type name_category: str
            :param if_exists: Indica come deve avvenire la memorizzazione se la tabella in cui si vuole scrivere esiste già.Può assumere 3 valori: fail, append, replace. Di default è impostato append.
            :type if_exists: str
            :return: nessun valore
        '''

        dataset.to_sql(name=self.category_str, con=self.connection, if_exists=if_exists, index=False)
        self.logOperation(self.scaricaCat, name_category)


    def writeSeriesByCategory(self,dataset,name_category,if_exists='append'):
        ''' Questo metodo permette di scrivere un dataframe pandas contenente tutte le serie di una categorie data su
        una taballe sql. Il metodo riceve in ingresso un dataset contenente le informazioni relative a più serie.
        A tale dataset è aggiunta una colonna che indica il nome della categoria acui la serie appartiene.

             :param dataset: Dataframe pandas da memorizzare nel database.
             :type dataset: pandas.core.frame.DataFrame
             :param name_category: nome della categoria padre
             :type name_category: str
             :param if_exists: Indica come deve avvenire la memorizzazione se la tabella in cui si vuole scrivere esiste già.Può assumere 3 valori: fail, append, replace. Di default è impostato append.
             :type if_exists: str
             :return: nessun valore
         '''
        dataset = dataset.assign(Categoria=name_category)
        dataset.to_sql(name=self.serie_str, con=self.connection, if_exists=if_exists, index=False)
        self.logOperation(self.scaricaSer,name_category)

    def writeObservationBySeries(self,dataset,name_series,if_exists='append'):
        ''' Questo metodo permette di scrivere un dataframe pandas contenente tutte le osservazioni di una serie data
        su una taballe sql. Il metodo riceve in ingresso un dataset contenente le informazioni relative a più osservazioni.
         A tale dataset è aggiunta una colonna che indica il nome della serie di cui fanno parte quelle osservazioni.

             :param dataset: Dataframe pandas da memorizzare nel database.
             :type dataset: pandas.core.frame.DataFrame
             :param name_series: nome della serie
             :type name_series: str
             :param if_exists: Indica come deve avvenire la memorizzazione se la tabella in cui si vuole scrivere esiste già.Può assumere 3 valori: fail, append, replace. Di default è impostato append.
             :type if_exists: str
             :return: nessun valore
         '''

        dataset = dataset.assign(Serie=name_series)
        dataset.to_sql(name=self.osservazioni_str, con=self.connection, if_exists=if_exists, index=False)
        self.logOperation(self.scaricaOss, name_series)

    def readSubCategoryByCategory(self,name_category):
        ''' Questo metodo permette di leggere dal database la tabella contenente tutte le sottocategorie di una categoria data.

            :param name_category: nome della categoria di cui si vogliono leggere le categorie figlie.
            :type name_category: str
            :return: restituisce un dataframe pandas se la lettura va a buon fine.
            :rtype: pandas.core.frame.DataFrame
        '''

        query=self.templateQuery.format(table=self.category_str,attribute='parent_id', value=name_category)
        df = pd.read_sql(query, self.connection)
        return df



    def readSeriesByCategory(self,name_category):
        ''' Questo metodo permette di leggere dat database una tabella contenente tutte le serie di una categoria data.

            :param name_category: nome della categoria di cui si vogliono leggere le serie.
            :type name_category: str
            :return: restituisce un dataframe pandas se la lettura va a buon fine.
            :rtype: pandas.core.frame.DataFrame
        '''
        query=self.templateQuery.format(table=self.serie_str,attribute='Categoria', value=name_category)
        df = pd.read_sql(query, self.connection)
        return df

    def readObservationBySeries(self,name_series):
        ''' Questo metodo permette di leggere dal database una tabella contenente tutte le osservazioni di una serie data.

            :param name_series: nome della serie di cui si vogliono leggere le osservazioni.
            :type name_category: str
            :return: restituisce un dataframe pandas se la lettura va a buon fine.
            :rtype: pandas.core.frame.DataFrame
        '''
        query=self.templateQuery.format(table=self.osservazioni_str,attribute='Serie', value=name_series)
        df = pd.read_sql(query, self.connection)
        return df

    def updateSubCategoryByCategory(self, new_dataset, name_category):
        ''' Questo metodo permette di aggiornare una tabella sql se già esistente.In particolare si aggiorna la tabella contenente le sottocategorie di una categoria data.
        Il metodo aggiunge solo i nuovi record senza toccare le informazioni già presenti.

            :param new_dataset: Nuovo dataframe pandas da memorizzare nel database.
            :type new_dataset: pandas.core.frame.DataFrame
            :param name_category: Nome della categoria di cui si vuole aggiornare l'elenco delle categorie figlie.
            :type name_category: str
            :return: nessun valore
        '''

        dataframe = self.readSubCategoryByCategory(name_category)
        update_dataset = pd.concat([dataframe, new_dataset]).drop_duplicates(keep=False)

        self.writeSubCategoryByCategory(update_dataset, name_category)
        self.logOperation(self.updateCat, name_category)


    def updateSeriesByCategory(self,new_dataset,name_category):
        ''' Questo metodo permette di aggiornare una tabella sql se già esistente.
        In particolare si aggiorna la tabella contenente le serie di una categoria data.
        Il metodo aggiunge solo i nuovi record senza toccare le informazioni già presenti.

                :param new_dataset: Nuovo dataframe pandas da memorizzare nel database.
                :type new_dataset: pandas.core.frame.DataFrame
                :param name_category: Nome della categoria di cui si vuole aggiornare l'elenco delle serie.
                :type name_category: str
                :return: nessun valore
        '''

        dataframe=self.readSeriesByCategory(name_category)

        new_dataset = new_dataset.assign(Categoria=name_category)
        update_dataset=pd.concat([dataframe,new_dataset]).drop_duplicates(keep=False)

        self.writeSeriesByCategory(update_dataset,name_category)
        self.logOperation(self.updateSer, name_category)

    def updateObservationBySeries(self,new_dataset,name_series):
        ''' Questo metodo permette di aggiornare una tabella sql se già esistente.
        In particolare si aggiorna la tabella contenente le osservazioni di una serie data.
        Il metodo aggiunge solo i nuovi record senza toccare le informazioni già presenti.

                :param new_dataset: Nuovo dataframe pandas da memorizzare nel database.
                :type new_dataset: pandas.core.frame.DataFrame
                :param name_series: Nome della serie di cui si vuole aggiornare le informazioni dell osservazioni.
                :type name_series: str
                :return: nessun valore
        '''
        dataframe=self.readObservationBySeries(name_series)

        new_dataset = new_dataset.assign(Serie=name_series)
        update_dataset=pd.concat([dataframe,new_dataset]).drop_duplicates(keep=False)

        self.writeObservationBySeries(update_dataset,name_series)
        self.logOperation(self.updateOss, name_series)

    def logOperation(self,tipo,nome):
        ''' Questo metodo memorizza nella tabella 'Operazioni' del database l'operazione che è stata appena completata.

                :param tipo: tipo di operazione eseguita. Ci possono essere 7 diverse operazioni: scarica sotto categorie da una categoria data, Scarica serie da una categoria data ,Scarica osservazioni da una serie data , aggiorna sotto categorie di una categoria data ,aggiorna serie di una categoria data ,aggiorna osservazioni di una serie data ,Analizza osservabili.
                :type tipo: str
                :param nome: Nome della serie/categoria data che è stata scaricata/aggiornata/analizzata.
                :type name_series: str
                :return: nessun valore
        '''

        query=self.templateOperazioni.format(tipo=tipo,nome=nome,data=datetime.today())
        self.connection.execute(query)

    def readLogOperation(self,tipo,name):
        ''' Questo metodo ricerca nella tabella 'Operazioni' del database una determinata operazione eseguita in passato.

                :param tipo: tipo di operazione che si vuole cercare. Ci possono essere 7 diverse operazioni: scarica sotto categorie da una categoria data, Scarica serie da una categoria data ,Scarica osservazioni da una serie data , aggiorna sotto categorie di una categoria data ,aggiorna serie di una categoria data ,aggiorna osservazioni di una serie data ,Analizza osservabili.
                :type tipo: str
                :param nome: Nome della serie/categoria che si vuole ricercare.
                :type name_series: str
                :return: Dataframe pandas
        '''
        query=self.templateReadoperazioni.format(value1=tipo,value2=name)
        df = pd.read_sql(query, self.connection)
        return df

    def readAllOperation(self):
        '''Questo metodo ricerca nella tabella 'Operazioni' del database tutte le operazioni eseguite.

            :return: Dataframe pandas
        '''
        df = pd.read_sql(self.templateAllOp, self.connection)
        return df

