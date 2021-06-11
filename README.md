# wekan-logstash

To format data for logstash and ELK (Kibana) - Format below :

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
  "boardSlug": "test",
  "description": "A subtask description",
  "startAt": "2021-06-07T20:47:00.000Z",
  "endAt": "2021-06-09T20:47:00.000Z",
  "requestedBy": "LR",
  "assignedBy": "MM",
  "receivedAt": "2021-06-07T20:36:00.000Z",
  "archivedAt": "2017-02-19T02:13:24.269Z",
  "createdAt": "2017-02-19T02:13:24.269Z",
  "lastModification": "2017-02-19T03:12:13.740Z",
  "list": "Done",
  "dailyEvents": 5,
  "board": "Test",
  "isArchived": true,
  "dueAt": "2017-02-19T02:13:24.269Z",
  "swimlaneTitle": "Swinline Title",
  "customfieldName1": "value",
  "customfieldName2": "value",
  "assignees": "fmonthel",
  "title": "Card title",
  "boardId": "eJPAgty3guECZf4hs",
  "cardUrl": "http://localhost/b/xxQ4HBqsmCuP5mYkb/semanal-te/WufsAmiKmmiSmXr9m"
}
``` 

Goal is to export data into Json format that we can be used as input for Logstash and ElastisSearch / Kibana (ELK)

Import in logstash should be done daily basic (as we have field daily event)
