# Resumen
------------
El **objetivo** :dart: del proyecto es exportar datos de determinados **tableros** de una instalación de **Wekan** a una plataforma o 
cluster de **ElasticSearch**.

![git_logo](_images/GitHub-Mark-32px.png ':size=2%') Este proyecto es un fork del proyecto original en Github: [wekan-logstash](https://github.com/wekan/wekan-logstash.git)

### Formato

Los datos para cada una de las tarjetas son exportados en formato _**JSON**_ (_Javascript object notation_). Los atributos incluídos 
correspondes a los campos comunes que observamos en todas las tarjetas de Wekan.

```json
{
  "storyPoint": 2.0,
  "nbComments": 1,
  "createdBy": "fmonthel",
  "labels": [
    "vert",
    "jaune"
  ],
  "members": [
    "fmonthel",
    "Olivier"
  ],
  "id": "7WfoXMKnmbtaEwTnn",
  "archivedAt": "2017-02-19T02:13:24.269Z",
  "createdAt": "2017-02-19T02:13:24.269Z",
  "lastModification": "2017-02-19T03:12:13.740Z",
  "list": "Done",
  "dailyEvents": 5,
  "board": "Test",
  "boardSlug": "test",
  "isArchived": true,
  "duedAt": "2017-02-19T02:13:24.269Z",
  "swimlaneTitle": "Swinline Title",
  "customfieldName1": "value",
  "customfieldName2": "value",
  "assignees": "fmonthel",
  "title": "Card title",
  "boardId": "eJPAgty3guECZf4hs",
  "cardUrl": "http://localhost/b/eJPAgty3guECZf4hs/test/7WfoXMKnmbtaEwTnn"
}
``` 
!> Una tarjeta puede o nó tener asociados varios campos **customizados**, estos son incluídos por su nombre dentro de la estructura 
del archivo JSON. </br>
El campo **cardUrl** es constuído a partir de una variable de entorno pasada al script. Detalles del proceso en [Customización](/customization) :link:
