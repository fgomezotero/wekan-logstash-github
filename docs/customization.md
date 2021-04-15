# Customización
-------------
Con esta sección pretendemos explicar los cambios realizados respecto al proyecto original 
[wekan-logstash](https://github.com/wekan/wekan-logstash.git)

- Adición de nuevos campos
- Inclusión de variables de entornos
- Cambio de lógica del fichero white-list-boards.txt
- Funcionalidad de petición HTTP contra el losgtash

### Nuevos campos

Se adicionaron nuevos campos al documento JSON dando seguimiento a la evolución del producto **Wekan**. 
A continuación una lista de los mismos:

- [x] **BoardId**: Id del tablero al que pertenece la tarjeta
- [x] **BoardSlug**: Título del tablero modificado normalizado para utilizarse cómo parte de la url de las tarjetas
- [x] **CardUrl**: Url completa de la tarjeta

### Variables de entornos

Dado el requerimiento de ejecutar el script en Openshift y con la premisa de no incluir en el mismo valores sensibles 
cómo contraseñas, usuarios y urls. Se definió modificar el script para que permitiera inyectar esos valores necesarios
para su correcto funcionamiento a través de variables de entornos como podemos ver en el recorte siguiente:

```python
# Parameters
mongo_user = os.getenv('MONGODB_USER', '')
mongo_password = os.getenv('MONGODB_PWD', '')
mongo_server = os.getenv('MONGODB_HOST', 'localhost')
mongo_port = os.getenv('MONGODB_PORT', '27017')
mongo_database = os.getenv('MONGODB_DB', 'wekan')
baseURL = os.getenv('BASEURL', 'http://localhost')
logstashEndpoint = os.getenv('LOGSTASH_SERVER', 'http://localhost:5044')
```

### Fichero white-list-boards.txt

Originalmente la razón del ser del fichero _white-list-board.txt_ era almacenar tableros que se comportaban como 
públicos. Agregando el campo **title** de la tarjeta sí el tablero al cual pertenecía era público o estaba almacenado 
en este fichero.

!> :loudspeaker: En nuestro proyecto definimos que solamente exportamos a JSON los datos de las tarjetas pertenecientes 
a los tableros almacenados en el fichero _white-list-boards.txt_.

Por lo tanto el recorrido de todas las tarjetas está condicionado a las que pertenezcan a los tableros listados en dicho fichero:

```python
# select cards for boards in whitelist file
for card in cards.find({'boardId': {'$in': whitelistboards}}):
```

### Petición HTTP contra el losgtash

Añadimos además al script una función para haciendo uso del módulo _request_ de Python realizar las peticiones http(s) al
servicio en escucha de logstash.

```python
def calllogstashpipeline(card):
    """Make a request to logstash endpoint services

    :param card: A single card
    :return: Response status code
    """
    r = requests.post(logstashEndpoint, data=card, headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
    return r.status_code
```