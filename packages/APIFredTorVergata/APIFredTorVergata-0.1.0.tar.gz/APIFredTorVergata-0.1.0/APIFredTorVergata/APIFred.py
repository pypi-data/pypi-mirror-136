import datetime
import os
import sys
import time

import numpy as np
import pandas as pd
import requests
import seaborn as sns
from pandas import json_normalize

from APIFredTorVergata.DBFred import Datamanager
import matplotlib.pyplot as plt

class Fred:
    ''' Questa classe è il client che invia richieste all'API Fred. Tale classe fornisce anche un supporto ad un database mysql.
    Tutte le informazioni scaricate o analizzate vengono memorizzate nel database. Quando l'utente chiede dei dati se essi sono presenti
    in locale vengono prelevati direttamente dal database senza scaricarli nuovamente. E' prevista anche una funzionalità per
    aggiornare le informazioni scaricate in precedenza sotto richieste dell'utente.
    '''

    def __init__(self,connection,api_key):
        ''' Costruttore della classe Fred. Nel costruttore viene istanziato un oggetto di tipo 'Datamanager' che si occuperà di gestire le scritture e le letture nel database.
        Ovviamente la connesione ad database deve essere fornita dall'utente.

            :param connection: connesione con il database.
            :param api_key: api key utilizzata per contattare l'Api fred
        '''


        self.datamanager=Datamanager(connection)
        self.urlTemplateChildren='https://api.stlouisfed.org/fred/category/children?category_id={id}&api_key='+api_key+'&file_type=json'
        self.urlTemplateSeries='https://api.stlouisfed.org/fred/category/series?category_id={id}&api_key='+api_key+'&file_type=json'
        self.urlTemplateObs = 'https://api.stlouisfed.org/fred/series/observations?series_id={id}&api_key=' + api_key + '&file_type=json'

    def dowloadSubCategoryByCategory(self,name_category):
        ''' Questo metodo fornisce all'utente un Dataframe pandas contenente tutte le categorie figlie di una categoria data.
        Se i dati sono presenti in locale, vengono prelevati dal database. Altrimenti vengono scaricati.

            :param name_category: nome della categoria padre
            :type name_category: str
            :return: Dataframe pandas. Il Dataframe avrà 3 colonne: id della categoria figlia, nome della categoria figlia, id della categoria padre.
            :rtype: pandas.core.frame.DataFrame
        '''

        #Se ho già scaricato dati dall'Api per quella categoria ,la variabile log conterrà un certo numero di record.
        log=self.datamanager.readLogOperation(self.datamanager.scaricaCat,name_category)
        dataset=None
        json={}

        try:
            #Se ho già scaricato i dati li leggo dal database
            if(len(log)>0):
                dataset=self.datamanager.readSubCategoryByCategory(name_category)
            else:
                url=self.urlTemplateChildren.format(id=name_category)
                response = requests.get(url)
                json = response.json()

                # converto lista di json in un dataset
                dataset = json_normalize(json['categories'])
                self.datamanager.writeSubCategoryByCategory(dataset,name_category)

        except Exception :
            message="Si è verificato un errore con la comunicazione con il server." \
                    "\nRiprovare o modificare il nome della categoria.Il nome '{nome}' potrebbe non esistere. Verrà restituito valore nullo." \
                    "\nIl server ha restituito il seguente errore: '{json}' "

            print(message.format(nome=name_category,json=json), file=sys.stderr)

        finally:
            return dataset

    def dowloadSeriesByCategory(self,name_category):
        ''' Questo metodo fornisce all'utente un Dataframe pandas contenente tutte le serie di una categoria data.
        Se i dati sono presenti in locale, vengono prelevati dal database. Altrimenti vengono scaricati.

            :param name_category: nome della categoria
            :type name_category: str
            :return: Dataframe pandas. Il Dataframe avrà 6 colonne: id della serie, id della categoria, titolo della serie, frequenza , inizio osservazione , fine osservazione.
            :rtype: pandas.core.frame.DataFrame
        '''

        # Se ho già scaricato dati dall'Api per quella categoria ,la variabile log conterrà un certo numero di record.
        log = self.datamanager.readLogOperation(self.datamanager.scaricaSer, name_category)
        dataset = None
        json = {}

        try:
            # Se ho già scaricato i dati li leggo dal database
            if (len(log) > 0):
                dataset = self.datamanager.readSeriesByCategory(name_category)
            else:
                url = self.urlTemplateSeries.format(id=name_category)
                response = requests.get(url)
                json = response.json()

                # converto lista di json in un dataset
                dataset_full = json_normalize(json['seriess'])
                dataset = dataset_full[['id', 'title','frequency','observation_start','observation_end']]
                self.datamanager.writeSeriesByCategory(dataset, name_category)

        except Exception:
            message = "Si è verificato un errore con la comunicazione con il server." \
                      "\nRiprovare o modificare il nome della categoria.Il nome '{nome}' potrebbe non esistere. Verrà restituito valore nullo." \
                      "\nIl server ha restituito il seguente errore: '{json}' "

            print(message.format(nome=name_category, json=json), file=sys.stderr)

        finally:
            return dataset


    def dowloadObservationBySeries(self,name_series):
        ''' Questo metodo fornisce all'utente un Dataframe pandas contenente tutte le osservazioni di una serie data.
        Se i dati sono presenti in locale, vengono prelevati dal database. Altrimenti vengono scaricati.

            :param name_series: nome della serie
            :type name_category: str
            :return: Dataframe pandas. Il Dataframe avrà 5 colonne: id della serie,valore dell'osservazione,data , tempo di inizio , tempo di fine.
            :rtype: pandas.core.frame.DataFrame
        '''

        # Se ho già scaricato dati dall'Api per quella serie ,la variabile log conterrà un certo numero di record.
        log = self.datamanager.readLogOperation(self.datamanager.scaricaOss, name_series)
        dataset = None
        json = {}

        try:
            # Se ho già scaricato i dati li leggo dal database
            if (len(log) > 0):
                dataset = self.datamanager.readObservationBySeries(name_series)
            else:
                url = self.urlTemplateObs.format(id=name_series)
                response = requests.get(url)
                json = response.json()

                # converto lista di json in un dataset
                dataset = json_normalize(json['observations'])
                self.datamanager.writeObservationBySeries(dataset, name_series)

        except Exception:
            message = "Si è verificato un errore con la comunicazione con il server." \
                      "\nRiprovare o modificare il nome della serie.Il nome '{nome}' potrebbe non esistere. Verrà restituito valore nullo." \
                      "\nIl server ha restituito il seguente errore: '{json}' "

            print(message.format(nome=name_series, json=json), file=sys.stderr)

        finally:
            return dataset

    def updateSubCategoryByCategory(self,name_category):
        ''' Questo metodo scarica le categorie figlie di una categoria data.
        Il metodo scaricherà sempre dati tramite API in quanto il suo obiettivo è quello di aggiornare i valori già presenti nel database.

            :param name_category: nome della categoria padre
            :type name_category: str
            :return: Nessun valore.
        '''
        json={}

        try:
            url = self.urlTemplateChildren.format(id=name_category)
            response = requests.get(url)
            json = response.json()

            # converto lista di json in un dataset
            dataset = json_normalize(json['categories'])
            self.datamanager.updateSubCategoryByCategory(dataset,name_category)
        except Exception:
            message = "Si è verificato un errore con la comunicazione con il server.Aggiornamento fallito." \
                      "\nRiprovare o modificare il nome della categoria.Il nome '{nome}' potrebbe non esistere." \
                      "\nIl server ha restituito il seguente errore: '{json}' "

            print(message.format(nome=name_category, json=json), file=sys.stderr)

    def updateSeriesByCategory(self,name_category):
        ''' Questo metodo scarica le serie di una categoria data.
        Il metodo scaricherà sempre dati tramite API in quanto il suo obiettivo è quello di aggiornare i valori già presenti nel database.

            :param name_category: nome della categoria padre
            :type name_category: str
            :return: Nessun valore.
        '''
        json = {}

        try:
            url = self.urlTemplateSeries.format(id=name_category)
            response = requests.get(url)
            json = response.json()

            # converto lista di json in un dataset
            dataset_full = json_normalize(json['seriess'])
            dataset = dataset_full[['id', 'title', 'frequency', 'observation_start', 'observation_end']]
            self.datamanager.updateSeriesByCategory(dataset, name_category)
        except Exception:
            message = "Si è verificato un errore con la comunicazione con il server.Aggiornamento fallito." \
                      "\nRiprovare o modificare il nome della categoria.Il nome '{nome}' potrebbe non esistere." \
                      "\nIl server ha restituito il seguente errore: '{json}' "

            print(message.format(nome=name_category, json=json), file=sys.stderr)

    def updateOservationbySeries(self,name_series):
        ''' Questo metodo scarica le osservazioni di una serie data.
        Il metodo scaricherà sempre dati tramite API in quanto il suo obiettivo è quello di aggiornare i valori già presenti nel database.

            :param name_series: nome della serie
            :type name_series: str
            :return: Nessun valore.
        '''

        json = {}

        try:
            url = self.urlTemplateObs.format(id=name_series)
            response = requests.get(url)

            #converto lista di json in un dataset
            json = response.json()
            dataset = json_normalize(json['observations'])
            self.datamanager.updateObservationBySeries(dataset, name_series)
        except Exception:
            message = "Si è verificato un errore con la comunicazione con il server.Aggiornamento fallito." \
                      "\nRiprovare o modificare il nome della serie.Il nome '{nome}' potrebbe non esistere." \
                      "\nIl server ha restituito il seguente errore: '{json}' "

            print(message.format(nome=name_series, json=json), file=sys.stderr)

    def plotOservationBySeries(self,name_series):
        '''Questo metodo restituisce un grafico delle osservazioni di una serie data.
        Per visionare il grafico è sufficiente invocare il metodo show() sull'output.

            :param name_series: Nome della serie di cui si vuole graficare l'andamento delle osservazioni.
            :type name_series: str
            :return: Grafico generato dalla libreria matplotlib
            :rtype: matplotlib.pyplot
        '''

        x, y = self.giveDataPlotOservationBySeries(name_series)

        plt.figure(figsize=(16, 9))
        plt.subplots_adjust(bottom=0.25)
        plt.grid()

        step = int(len(x) / 15)

        plt.plot(x, y)
        plt.xticks(x[::step], x[::step],rotation=-45)
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.title("Osservazioni della serie "+name_series)

        self.datamanager.logOperation(self.datamanager.analizza,name_series)
        return plt


    def plotMovingAverage(self,n,name_series):
        '''Questo metodo restituisce un grafico della media mobile delle osservazioni di una serie data.
        Per visionare il grafico è sufficiente invocare il metodo show() sull'output.

            :param name_series: Nome della serie di cui si vuole graficare l'andamento delle osservazioni.
            :type name_series: str
            :param n: parametro attraverso cui calcolare la media mobile. Si consiglia di scegliere un valore minore di 50.
            :type n: int
            :return: Grafico generato dalla libreria matplotlib
            :rtype: matplotlib.pyplot
        '''

        if(n<=0 or n>50):
            message =   "\nPer ragioni di ottimizzazione si consiglia di scegliere il parametro 'n' comppreso tra 1 e 50." \
                        "\nVerrà restituito un grafico spoglio."

            print(message, file=sys.stderr)
            return plt.plot()

        else:
            xlbl, average, x, _ = self.giveDataPlotMovingAVBySeries(name_series,n)

            #riutilizzo il grafico delle osservazioni della stessa serie a cui sovrappongo il grafico della media mobile.
            plot=self.plotOservationBySeries(name_series)
            plot.plot(xlbl, average)

            #Se n<10 sull'asse delle x compaiono troppi valori.Graficamente è un brutto effetto. Rendo costante il numero di valori da visualizzare
            if(n<10 ):
                step = int(len(x) / 15)
                plt.xticks(x[::step], x[::step])

            plt.xticks(rotation=-45)
            plt.xlabel("Date")
            plt.ylabel("Value")
            plt.title("Media mobile della serie: "+name_series)
            self.datamanager.logOperation(self.datamanager.analizza, name_series)

        return plt

    def plotPrimeDifferenceSeries(self,name_series):
        """Questo metodo permette di graficare la serie delle differenze prime di una data serie.

            :param name_series: nome della serie di cui si vogliono i dati grezzi.
            :type name_series: str
            :return: grafico generato dalla libreria Matplotlib
            :rtype: matplotlib.pyplot
        """
        data=self.giveDataPrimeDifferenceSeries(name_series)
        plt.figure(figsize=(16, 9))
        plt.subplots_adjust(bottom=0.25)
        plt.plot(data)

        plt.xlabel("Differenza n-esima")
        plt.ylabel("Differenze prime")
        plt.title("Serie delle differenze prime: " + name_series)

        return plt

    def plotPrimeDifferencePercSeries(self,name_series):
        """Questo metodo permette di graficare la serie delle differenze prime percentuali di una data serie.

             :param name_series: nome della serie di cui si vogliono i dati grezzi.
             :type name_series: str
             :return: grafico generato dalla libreria Matplotlib
             :rtype: matplotlib.pyplot
         """
        data=self.giveDataPrimeDifferencePercSeries(name_series)
        plt.figure(figsize=(16, 9))
        plt.subplots_adjust(bottom=0.25)
        plt.plot(data)

        plt.xlabel("Differenza n-esima")
        plt.ylabel("Differenze prime %")
        plt.title("Serie delle differenze prime percentuali: " + name_series)

        return plt

    def plotCovarianceMatrix(self,array_series):
        '''Questo metodo permette di graficare la matrice delle covarianze delle osservazioni di un certo numero di serie passate come parametri. Il metodo accetta in ingresso un array contenente i nomi delle serie da analizzare.
        La matrice è realizzata in particolare usando la libreria Seaborn.
        Nello specifico il metodo vuole creare un dataset formato da tante colonne quanti sono i paramatri di input.
        Ogni colonna conterrà le osservazioni per quella serie.
        Se ad esempio i parametri di ingresso sono A B C allora il dataset ottenuto sarà:

                A    B    C\n
                num1 num2 num3\n
                num4 num5 num6\n
                ...

        Si calcola poi la covarianza tra i valori numerici presenti nelle varie colonne.

            :param array_series: array contenente i nomi delle serie che si vogliono analizzare
            :type array_series: list
            :return: Grafico generato dalla libreria Seaborn
            :rtype: matplotlib.pyplot
        '''

        try:

            #creo dataset
            osservations={}
            for serie in array_series:
                dataset_full=self.dowloadObservationBySeries(serie)
                osservation_value=pd.to_numeric(dataset_full['value']).tolist()
                osservations[serie]=osservation_value

            dataset = pd.DataFrame(osservations)
            cov_matrix = dataset.cov()

            sns.heatmap(cov_matrix, annot=True, fmt='.2f', cmap='GnBu',
                        cbar_kws={"shrink": .8}, robust=True)


            plt.subplots_adjust(bottom=0.3,top=0.925, left=0.216, right=0.977, hspace=0.2, wspace=0.205)
            plt.yticks(rotation=45)
            plt.xticks(rotation=45)
            plt.title('Matrice varianza-covarianza')

            plt.gcf().set_size_inches(16, 9)

        except Exception as e:
            print(e)
            message = "\nErrore nel graficare la matrice delle correlazioni.Verrà restituita una grafico spoglio." \
                      "\nRiprovare o modificare il nome di una delle seri.Uno dei nomi specificato '{nome}' potrebbe non esistere."

            print(message.format(nome=array_series), file=sys.stderr)
            plt.plot()

        return plt

    def plotCorrelationMatrix(self,array_series):
        '''Questo metodo permette di graficare la matrice delle correlazioni delle osservazioni di un certo numero di serie passate come parametri. Il metodo accetta in ingresso un array contenente i nomi delle serie da analizzare.
        La matrice è realizzata in particolare usando la libreria Seaborn.
        Nello specifico il metodo vuole creare un dataset formato da tante colonne quanti sono i paramatri di input.
        Ogni colonna conterrà le osservazioni per quella serie.
        Se ad esempio i parametri di ingresso sono A B C allora il dataset ottenuto sarà:

                A    B    C\n
                num1 num2 num3\n
                num4 num5 num6\n
                ...

        Si calcola poi la correlazione tra i valori numerici presenti nelle varie colonne.

            :param array_series: array contenente i nomi delle serie che si vogliono analizzare
            :type array_series: list
            :return: Grafico generato dalla libreria Seaborn
            :rtype: matplotlib.pyplot
        '''

        try:
            #creo dataset
            osservations={}
            for serie in array_series:
                dataset_full=self.dowloadObservationBySeries(serie)
                osservation_value=pd.to_numeric(dataset_full['value']).tolist()
                osservations[serie]=osservation_value

            dataset_corr = pd.DataFrame(osservations)
            correlation_matrix = dataset_corr.corr()

            sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='GnBu',
                        cbar_kws={"shrink": .8}, robust=True)

            plt.subplots_adjust(bottom=0.3,top=0.925, left=0.216, right=0.977, hspace=0.2, wspace=0.205)
            plt.yticks(rotation=45)
            plt.xticks(rotation=45)
            plt.title('Matrice correlazione')

            plt.gcf().set_size_inches(16, 9)


        except Exception:
            message = "\nErrore nel graficare la matrice delle correlazioni.Verrà restituita una grafico spoglio." \
                      "\nRiprovare o modificare il nome di una delle seri.Uno dei nomi specificato '{nome}' potrebbe non esistere."

            print(message.format(nome=array_series), file=sys.stderr)
            plt.plot()


        return plt

    def plotLinearRegression(self, name_series):
        '''Questo metodo realizza il grafico della regressione lineare di una serie data.

             :param name_series: nome della serie di cui si vuole graficare la retta di regressione.
             :type name_series: str
             :return: grafico generato dalla libreria Matplotlib
             :rtype: matplotlib.pyplot

        '''

        dataset = self.dowloadObservationBySeries(name_series)

        # converto la data in secondi
        dateObs = dataset['date']
        dateSecond = [time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()) for date in dateObs]
        dateSecond = pd.to_numeric(dateSecond)

        # ricavo valori delle osservazioni
        valueObs = pd.to_numeric(dataset['value']).tolist()

        b0, b1, reg_line = self.linear_regression(dateSecond, valueObs)

        x = dateSecond
        y = b0 + b1 * x

        plt.figure(figsize=(16, 9))
        plt.subplots_adjust(bottom=0.25)
        plt.grid()

        step = int(len(dateSecond) / 15)

        plt.plot(dateSecond, valueObs)
        plt.plot(x, y)
        plt.xticks(dateSecond[::step], dateObs[::step], rotation=-45)
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.title("Regressione lineare della serie: {nome}\n{reg} ".format(nome=name_series, reg=reg_line))

        return plt



    def giveDataPlotOservationBySeries(self, name_series):
        '''Questo metodo restituisce due liste. In particolare vengono forniti i dati grezzi che descrivono le osservazioni
        di una serie e che devono poi essere rappresentati su un grafico.

            :param name_series: Nome della serie di cui si vogliono i dati grezzi.
            :type name_series: str
            :return: Il parametro x contiene i valori che devono essere graficati sull'asse x di un grafico. Si tratta della lista delle date in cui sono state effettuate le misurazioni delle osservazioni.Il parametro y è invece una lista che contiene tutti i valori delle osservazioni.
        '''
        x = []
        y = []

        try:
            dataset = self.dowloadObservationBySeries(name_series)
            x = dataset['date']
            ystr = dataset['value']
            y = pd.to_numeric(ystr)

        except Exception:
            message = "\nErrore nello scaricamento dei dati.Verranno resitituite due liste vuote." \
                      "\nRiprovare o modificare il nome della serie.Il nome '{nome}' potrebbe non esistere."

            print(message.format(nome=name_series), file=sys.stderr)

        return x, y

    def giveDataPlotMovingAVBySeries(self,name_series,n):
        '''Questo metodo restituisce quattro liste. In particolare vengono forniti i dati grezzi che possono essere utilizzati per graficare la media mobile delle osservazioni di una serie data.

             :param name_series: Nome della serie di cui si vogliono i dati grezzi.
             :type name_series: str
             :param n: parametro attraverso cui calcolare la media mobile. Si consiglia di scegliere un valore minore di 50.
             :type n: int
             :return: Il parametro 'xlbl' contiene i valori che devono essere graficati sull'asse x. Si tratta della lista delle date in cui sono state effettuate le misurazioni delle osservazioni.Il parametro 'average' è invece una lista che contiene le medie a 'n' periodi. Rappresenta quindi l'insieme di valori da inserire sull'asse y di un grafico.

        '''
        xlbl=[]
        average=[]
        x=[]
        yint=[]

        try:
            dataset = self.dowloadObservationBySeries(name_series)
            x = dataset['date']
            y = dataset['value']

            yint = pd.to_numeric(y).tolist()
            xlist = x.tolist()

            #Valori che andranno sull'asse delle x nel grafico. Prendo i valori della colonna 'date' ogni n elementi.Esempio: [a, b, c , d , e , f, g] -> [a,d,g] con n=3
            xlbl = [xlist[i] for i in range(0, len(yint), n)]

            #scompongo vettore in sottovettori di dimensione n. Esempio : [1 2 3 4 5 6] -> [[1,2],[3,4],[5,6]] con n=2
            output = [yint[i:i + n] for i in range(0, len(yint), n)]

            #calcolo la media come rapporto tra la somma dei valori dei sottovettori e la loro dimensione. Esempio con i dati precedenti :[1+2/2 ,3+4/2 , 5+6/2]
            average = [sum(output[i]) / len(output[i]) for i in range(0, len(output))]

        except Exception:
            message = "\nErrore nello scaricamento dei dati.Verranno resitituite due liste vuote." \
                      "\nRiprovare o modificare il nome della serie.Il nome '{nome}' potrebbe non esistere."

            print(message.format(nome=name_series), file=sys.stderr)


        return xlbl, average,x,yint


    def giveDataPrimeDifferenceSeries(self, name_series):
        '''Questo metodo fornisce i dati grezzi utili a graficare la serie delle differenze prima di una serie data. In particolare i dati grezzi
        consistono in una sola lista contenente i valori di tutte le differenze (𝑠𝑖+1−𝑠𝑖).

            :param name_series: nome della serie di cui si vogliono i dati grezzi.
            :type name_series: str
            :return: lista contenete tutti i valori della serie delle differenze prime.
            :rtype: list

        '''
        dataset_full = self.dowloadObservationBySeries(name_series)
        osservation_value = pd.to_numeric(dataset_full['value']).tolist()

        difference = [osservation_value[i + 1] - osservation_value[i] for i in range(0, len(osservation_value) - 1)]

        return difference

    def giveDataPrimeDifferencePercSeries(self, name_series):
        '''Questo metodo fornisce i dati grezzi utili a graficare la serie delle differenze prime percentuali di una serie data. In particolare i dati grezzi
        consistono in una sola lista contenente i valori di tutte le espressioni (𝑠𝑖+1−𝑠𝑖)/𝑠𝑖.

            :param name_series: nome della serie di cui si vogliono i dati grezzi.
            :type name_series: str
            :return: lista contenete tutti i valori della serie delle differenze prime percentuali.
            :rtype: list

        '''
        dataset_full = self.dowloadObservationBySeries(name_series)
        osservation_value = pd.to_numeric(dataset_full['value']).tolist()

        differencePerc = []
        for i in range(0, len(osservation_value) - 1):
            if (osservation_value[i] != 0):
                value = (osservation_value[i + 1] - osservation_value[i]) / osservation_value[i]
                differencePerc.append(value)

        return differencePerc

    def linear_regression(self,x, y):
        '''Questa funzione restituisce i parametri per realizzare la regressione lineare date due liste in ingresso. In particolare vengono
        restituiti i parametri B0,B1 che realizzano la formula : y=b0+b1X. Queste informazioni restituite dal metodo possono essere utilizzate
        per realizzare il grafico della regressione.

            :type x: list
            :type y: list
            :return: I parametri B0 e B1 utili per realizzare la retta di regressione. Viene restituita anche una stringa che mostra visivamente il formato della funzione.

        '''

        x=np.array(x)
        y=np.array(y)

        x_mean = sum(x)/len(x)
        y_mean = sum(y)/len(y)

        B1_num = sum(((x - x_mean) * (y - y_mean)))
        B1_den = sum(((x - x_mean) ** 2))
        B1 = B1_num / B1_den

        B0 = y_mean - (B1 * x_mean)

        reg_line = 'y = {} + {}β'.format(B0, B1)

        return (B0, B1, reg_line)
