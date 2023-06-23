# Shelly 3 EM Control

Questa documentazione illustra il funzionamento di un programma Python (<a href="./../src/ShellyEm_control.py">ShellyEm_control.py</a>) che sfrutta le API cloud di un dispositivo Shelly 3 EM per effettuare richieste cicliche e elaborare i dati misurati. Il programma memorizza i dati in un database PostgreSQL e include un'interfaccia grafica realizzata con Tkinter che consente di cercare lo Shelly ID e visualizzare i sensori attivati per la misurazione dei dati.

## Configurazione Iniziale

Prima di utilizzare il programma, è necessario effettuare alcune operazioni di configurazione iniziale del dispositivo Shelly 3 EM.
1. Connessione al dispositivo: Collegarsi alla rete Wi-Fi creata dal dispositivo Shelly 3 EM, che funge anche da access point.
2. Accesso all'interfaccia web: Aprire il browser e accedere all'indirizzo http://192.168.33.1/ per visualizzare l'interfaccia web del dispositivo Shelly 3 EM. Qui è possibile visualizzare i valori misurati dall'interfaccia predefinita.
<img alt="interfaccia base" src="./images/foto_interfaccia_base_shelly_3em.png">

## Modalità di Connessione al Dispositivo

Il dispositivo Shelly 3 EM offre due modalità di connessione: MQTT e Cloud. È possibile utilizzare una sola modalità alla volta.
### Modalità MQTT

Nella modalità MQTT, il dispositivo invia i dati misurati su specifici topic MQTT. Di seguito sono riportati i passaggi per configurare e testare la modalità MQTT:
1. Configurazione MQTT sul dispositivo: Utilizzando l'interfaccia web del dispositivo, configurare le impostazioni MQTT specificando il broker MQTT e i relativi parametri, come indirizzo IP e porta.
2. Installazione e configurazione del broker MQTT: Installare un broker MQTT sul proprio sistema. In questo esempio, è stato utilizzato il broker Mosquitto. Configurare il broker specificando le impostazioni desiderate, come ad esempio l'indirizzo IP e la porta.
3. Test della connessione MQTT: Utilizzare un client MQTT, come ad esempio MQTTX, per testare la connessione al broker MQTT e verificare se i dati vengono inviati correttamente sui topic specificati.
4. Tramite MQTT i dati vengono spediti sui topic ogni 30 secondi.
Attivazione di mqtt da shelly
![configurazione mqtt da shelly](./images/FireShot%20Capture%20011%20-%20ShellyEM3%20-%20192.168.18.211.png)
![broker 1](./images/Screenshot%202023-06-14%20141107.png)
![broker 2](./images/Screenshot%202023-06-14%20141131.png)
![client 2](images/Screenshot%202023-06-14%20141220.png)
![client 2](images/Screenshot%202023-06-14%20141238.png)

### Modalità Cloud

Nella modalità Cloud, il dispositivo Shelly 3 EM invia i dati misurati a un server cloud tramite le API cloud fornite dal produttore. Di seguito sono riportati i passaggi per utilizzare la modalità Cloud:
1. Registrazione del dispositivo sul server cloud: Creare un account sul server cloud del produttore e seguire le istruzioni per registrare il dispositivo Shelly 3 EM. Durante la registrazione, sarà necessario creare una stanza e specificare le informazioni del dispositivo.
2. Accesso ai dati e al controllo del dispositivo: Dopo aver registrato il dispositivo, sarà possibile accedere alle informazioni e al controllo del dispositivo tramite l'interfaccia web o l'app mobile fornita dal produttore.

![foto cloud](images/FireShot%20Capture%20012%20-%20Shelly%20Home%20-%20home.shelly.cloud.png)
prova utilizzo api cloud
```
auth key: your_auth_key
server uri: your_server_uri
device id: your_device_id
uri post prova: curl -X POST server_uri -d "id=device id&auth_key=auth key"
```

![risposta api cloud](images/Screenshot%202023-06-14%20143337.png)

Dopo aver provato a fare la richiesta da riga di comando, ho realizzato un programma python per fare la richiesta e salvare la risposta in un file json.

Il dispositivo può scegliere se utilizzare o mqtt o cloud, entrambe le funzioni non possono essere utilizzate contemporaneamente.

## Minutaggio dei dati
Scaricando il file csv del retain dei voltaggi in locale (vm_data.csv) si può vedere che vengono salvati i dati ogni minuto.
Da MQTT si poteva vedere che i dati venivano spediti ogni 30 secondi.
Analizzando il json restituito da postman si può vedere che i dati vengono aggiornati ogni 10 minuti infatti il parametro time varia di 10 minuti e se viene spedita una richesta nell'arco di quei 10 minuti ritornerà lo stessa la precedente.
[foto db](images/Screenshot%202023-06-15%20174510.png)
![](images/Screenshot%202023-06-15%20103448.png)
![](images/Screenshot%202023-06-16%20092026.png)
![](images/Screenshot%202023-06-16%20093555.png)

---

## Documentazione del programma Python per l'interazione con le API di Shelly 3EM e l'utilizzo di un database PostgreSQL tramite Python

Il seguente codice Python è progettato per interagire con le API cloud di un dispositivo Shelly 3EM, effettuare richieste cicliche per ottenere i dati dei sensori e salvare tali dati in un database PostgreSQL. Il programma include anche un'interfaccia grafica realizzata con Tkinter per cercare lo Shelly ID e visualizzare i sensori attivati per la misurazione dei dati.

### Dipendenze
Il programma richiede l'installazione dei seguenti moduli Python:
- `requests`: Per effettuare richieste HTTP alle API di Shelly.
- `schedule`: Per pianificare e eseguire ciclicamente le richieste verso le API.
- `json`: Per la manipolazione dei dati in formato JSON.
- `psycopg2`: Per la connessione al database PostgreSQL.
- `config`: Modulo personalizzato per la configurazione dei parametri di connessione al database.
- `tkinter`: Modulo per la creazione dell'interfaccia grafica.
- `threading`: Per avviare il cron job in un thread separato.
- `classes.Em` e `classes.Sensor`: Moduli personalizzati che definiscono le classi `Em` e `Sensor` utilizzate nel programma.

### Configurazione
Prima di eseguire il programma, è necessario effettuare alcune configurazioni:
- Modificare l'URL delle API di Shelly 3EM all'interno della variabile `url` nel codice.
- Impostare correttamente i valori della variabile `body_data` per autenticarsi e identificare il dispositivo Shelly corretto.
- Configurare i parametri di connessione al database PostgreSQL, per questo bisognerà creare un file `database.ini` nella directory `Shelly_3em` al suo interno andranno messi i seguenti campi:
```
[postgresql]
host=localhost
database=db_name
user=username
password=password
```

### Funzionamento del programma
Il programma si divide in diverse funzioni per gestire le diverse fasi dell'interazione con le API di Shelly e la gestione dei dati nel database. Ecco una panoramica delle principali funzioni e del loro scopo:

1. `connect()`: Funzione per connettersi al database PostgreSQL utilizzando i parametri di connessione configurati. Crea un oggetto `conn` per la connessione e un oggetto `cur` per il cursore del database.
2. `disconnect()`: Funzione per disconnettersi dal database. Chiude il cursore e la connessione al database.
3. `create_tables()`: Funzione per creare le tabelle `measurements` e `sensor` nel database se non esistono già. Queste tabelle vengono utilizzate per archiviare i dati dei sensori e le informazioni sui sensori attivati per ogni Shelly ID e fase.
4. `insert_lists()`: Funzione per inserire i dati dei sensori e delle misurazioni nel database. Utilizza le liste `sensor_list` e `measurement_list` per ottenere i dati da inserire. Controlla anche se i sensori esistono già nel database prima di eseguire l'inserimento.
5. `send_request()`: Funzione per inviare una richiesta alle API di Shelly per ottenere i dati dei sensori. Utilizza la libreria `requests` per inviare una richiesta POST all'URL specificato nella variabile `url` con i parametri di autenticazione e identificazione del dispositivo Shelly. La risposta viene quindi convertita in formato JSON e analizzata per estrarre i dati dei sensori e le relative misurazioni.

6. `tkinter_init()`: Funzione per inizializzare l'interfaccia grafica utilizzando la libreria Tkinter. Crea una finestra principale e aggiunge etichette, campi di input e pulsanti per l'interazione dell'utente.

7. `search()`: Funzione per cercare un dispositivo Shelly nel database utilizzando l'ID specificato dall'utente nell'interfaccia grafica. Esegue una query per verificare se l'ID esiste nel database e mostra una finestra di dialogo con il risultato della ricerca.

8. `open_sensor_table_window()`: Funzione per aprire una finestra separata che visualizza la tabella dei sensori per un determinato dispositivo Shelly. Recupera i dati dei sensori dal database e crea caselle di controllo corrispondenti ai sensori nella finestra. Permette all'utente di modificare lo stato delle caselle di controllo e applicare o annullare le modifiche.

9. `run_cron_job()`: Funzione che viene eseguita ciclicamente ogni 5 secondi grazie all'utilizzo della libreria `schedule`. Richiama la funzione `send_request()` per ottenere i dati dei sensori dalle API di Shelly.

10. `main()`: Funzione principale del programma. Si occupa di avviare la connessione al database, creare le tabelle, inizializzare l'interfaccia grafica, avviare il cron job in un thread separato e gestire la chiusura del programma.

Queste sono le principali funzioni che compongono il programma e svolgono le diverse operazioni come la gestione del database, l'interazione con le API di Shelly e la gestione dell'interfaccia grafica.
Questa è una panoramica, ovviamente è possibile estendere o modificare il codice per adattarlo alle proprie esigenze specifiche.
