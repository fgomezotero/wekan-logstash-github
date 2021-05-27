# Arquitectura
------------
La arquitectura de referencia se refleja en el siguiente diagrama :bar_chart:

![architecture](_images/architecture.png ':size=80%')

!> La ingesta hacía logstash debería de realizarse diariamente, dado que hay campos con eventos diarios.

## Despliegue en Openshift

Partiendo de la base que nuestra aplicación **Wekan** está desplegada en **Openshift**, incluyendo la base de datos
**MongoDB**, fue necesario asegurar la ejecución diaria del script a través de un artefacto propio de Openshift (**_cronjobs_**)

> En nuestro caso la ejecución del script **_logstash.py_** se ejecuta diariamente a las :alarm_clock: 23:00, cómo se puede apreciar 
en la propia definición del cronjobs.

```yaml
apiVersion: batch/v2alpha1
kind: CronJob
metadata:
  name: python-wekan-logs
spec:
  concurrencyPolicy: Forbid
  failedJobsHistoryLimit: 1
  jobTemplate:
    metadata:
      creationTimestamp: null
    spec:
      template:
        metadata:
          creationTimestamp: null
        spec:
          containers:
          - command:
            - bash
            - -eo
            - pipefail
            - -c
            - |
              echo "Ejecutando el script!!!"; ./logstash.py
            env:
            - name: MONGODB_USER
              valueFrom:
                secretKeyRef:
                  key: database-user
                  name: mongodb
            - name: MONGODB_PWD
              valueFrom:
                secretKeyRef:
                  key: database-password
                  name: mongodb
            - name: MONGODB_HOST
              value: mongodb
            - name: MONGODB_PORT
              value: "27017"
            - name: MONGODB_DB
              valueFrom:
                secretKeyRef:
                  key: database-name
                  name: mongodb
            - name: TZ
              value: America/Montevideo
            - name: APP_FILE
              value: logstash.py
            - name: LOGSTASH_SERVER
              value: http://localhost:5044
            - name: BASEURL
              value: https://localhost
            image: python-wekan-logs:latest
            imagePullPolicy: Always
            name: python-wekan-logs
            resources: {}
            terminationMessagePath: /dev/termination-log
            terminationMessagePolicy: File
          dnsPolicy: ClusterFirst
          restartPolicy: Never
          schedulerName: default-scheduler
          securityContext: {}
          serviceAccount: wekan
          serviceAccountName: wekan
          terminationGracePeriodSeconds: 30
  schedule: 0 23 * * *
  successfulJobsHistoryLimit: 3
  suspend: false
```

!> Tener en cuenta sustituir los valores de las variables de entorno por los valores que se adapten a tu ambiente.
:warning: Aclarar que la imagen que se utiliza para levantar el contenedor se obtiene cómo resultado de realizar S2I con 
la imagen base de python.

## Pipeline en logstash

Para completar el proceso de ingesta definimos en logstash el pipeline siguiente:

```
input {
   http {
      host => "0.0.0.0"
      port => "5044"
   }
}

output {
   elasticsearch {
       index => "wekan-daily-full-%{[boardSlug]}-%{[boardId]}"
       document_id => "%{[id]}-%{+YYYY.MM.dd}"
       hosts => ["localhost:9200"]
   } 
}
```
!> Se utiliza el plugins de entrada :link: [HTTP](https://www.elastic.co/guide/en/logstash/current/plugins-inputs-http.html).
Lo que permite a logstash recibir eventos sobre http(s) y a las aplicaciones poder enviar una petición http(s) al mismo.

:rotating_light: &nbsp; La definición del índice:  `index => "wekan-daily-full-%{[boardSlug]}-%{[boardId]}"` crea índices diferentes para cada
tablero declarado en el fichero _white-list-board.txt_, mientras que `document_id => "%{[id]}-%{+YYYY.MM.dd}"` crea un documento
por día para las tarjetas que pertenecen a los tableros almacenados en el fichero _white-list-boards.txt_. </br>

:exclamation: Por tanto, si el script es ejecutado más de una vez al día, actualizará los documentos creados, pero en ningún caso creará nuevos documentos a no ser que se añadan 
nuevas tarjetas a los tableros declarados.



