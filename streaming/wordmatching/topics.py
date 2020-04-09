from streaming.app import app

# Topic containing decoded certificates
cert_topic = app.topic('ct-certs-decoded')

# Topic containing certificates matching keywords
matched_topic = app.topic('wordmatching-hits')

# Topic containing certificates manually confirmed
confirmed_topic = app.topic('matching-confirmed')
 
# Tables
matching_table = app.Table('matching_table', default=list)
