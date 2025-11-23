import os
import ssl
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "invoice_processor.settings")

app = Celery("invoice_processor")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# SSL Configuration (only needed for CloudAMQP)
# app.conf.broker_use_ssl = True
# app.conf.broker_ssl_options = {
#     "cert_reqs": ssl.CERT_NONE,
#     "check_hostname": False,
# }
# app.conf.broker_transport_options = {
#     "ssl_cert_reqs": ssl.CERT_NONE,
#     "ssl_check_hostname": False,
# }

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
