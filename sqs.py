import datetime
from pymongo import MongoClient
import boto.sqs
import ast
import datetime
import time
import configSQS as cf
try:
    # Nos conectamos
    connection = MongoClient(cf.dbm)
    db = connection.SQS
except:
    pass


conn = boto.sqs.connect_to_region("us-west-2", aws_access_key_id = cf.aws_access_key_id,
                                  aws_secret_access_key = cf.aws_secret_access_key)

# Nos conectamosa la cola SQS
q = conn.get_queue('sqs_mail')
# Contador para Debug
a = 0
while True:
    try:
        rs = q.get_messages()

        m = rs[0]

        respuesta = m.get_body()

        respuesta = ast.literal_eval(respuesta)
        respuesta = ast.literal_eval(respuesta['Message'])
        list_domains = []
        for domain in respuesta['mail']['destination']:
            div = domain.split("@")
            list_domains.append(div[1])
        domains = {"domains": list_domains} 
        try:
            respuesta['delivery']['timestamp'] = datetime.datetime.\
                strptime(respuesta['delivery']['timestamp'],
                         "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            pass
        try:
            respuesta['bounce']['timestamp'] = datetime.datetime.\
                strptime(respuesta['bounce']['timestamp'],
                         "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            pass
        try:
            respuesta['complaint']['timestamp'] = datetime.datetime.\
                strptime(respuesta['bounce']['timestamp'],
                         "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            pass
        notificacion = {}
        # extraccion de nested JSON a JSON simple
        complaint = {}
        delivery = {}
        bounce = {}
        try:
            delivery = respuesta["delivery"]
        except:
            pass
        try:
            bounce = respuesta["bounce"]
        except:
            pass
        try:
            complaint = respuesta["complaint"]
        except:
            pass
        mail = respuesta["mail"]
        # Obtenemos si es Delivery o Bounce
        del respuesta["mail"]
        try:
            del respuesta["delivery"]
        except:  
            pass
        try:
            del respuesta["complaint"]
        except:  
            pass
        try:
            del respuesta["bounce"]
        except:  
            pass
        # Concatenamos JSON
        notificacion.update(delivery)
        notificacion.update(bounce)
        notificacion.update(complaint)
        notificacion.update(mail)
        notificacion.update(respuesta)
        notificacion.update(domains)
        # Guardamos en la BD
        db.status.insert(notificacion)
        # Borramos cola
        q.delete_message(m)
    except Exception, e:
        if "list index out of range" in str(e):
            print "FIN"
            exit()
        print str(e) + "--------------------------------" + str(respuesta)

