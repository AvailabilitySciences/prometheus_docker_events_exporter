import time
import logging
import docker
from optparse import OptionParser
from prometheus_client import start_http_server, Summary, Counter, Gauge, Histogram

parser = OptionParser()
# parser.add_option("-f", "--file", dest="filename",
#                   help="write report to FILE", metavar="FILE")
# parser.add_option("-q", "--quiet",
#                   action="store_false", dest="verbose", default=True,
#                   help="don't print status messages to stdout")

(options, args) = parser.parse_args()

summary_containers_stop = Summary("container_stop_summary","Stopped Containers summary",["container_name","container_id","container_image"])
summary_containers_start = Summary("container_start_summary","Started Containers summary",["container_name","container_id","container_image"])
summary_containers_death = Summary("container_death_summary","Died Containers summary",["container_name","container_id","container_image"])
summary_containers_create = Summary("container_create_summary","Created Containers summary",["container_image"])
summary_containers_removed = Summary("container_removed_summary","Removed Containers summary",["container_image"])

if __name__ == "__main__":
    # Connect to docker
    client = docker.from_env()
    try:
        # Test for docker socket connection
        client.info()

        # Setting up Prometheus server
        start_http_server(8000)

        # Streaming events, parsing , and increment proper metrics
        eventStreamer = client.events(decode=True)
        for event in eventStreamer:
            eventAction = event['Action']
            eventInfo = event['Actor']['Attributes']
            containerImage = eventInfo['image'] if 'image' in eventInfo else None
            containerName = eventInfo['name'] if 'name' in eventInfo else None
            containerID = event['id'] if 'id' in event else None

            if eventAction == "die":
                summary_containers_death.labels(container_name=containerName,container_image=containerImage,container_id=containerID).observe(1)
            elif eventAction == "stop":
                summary_containers_stop.labels(container_name=containerName, container_image=containerImage,
                                                container_id=containerID).observe(1)
            elif eventAction == "start":
                summary_containers_start.labels(container_name=containerName, container_image=containerImage,
                                                container_id=containerID).observe(1)
            elif eventAction == "create":
                summary_containers_create.labels(container_image=containerImage).observe(1)
            elif eventAction == "destroy":
                summary_containers_removed.labels(container_image=containerImage).observe(1)
            else:
                # TODO: handle connect, disconnect, attach , resize
                logging.info("Unhandled event: {}".format(event))

    except Exception as e:
        logging.exception("Failure in connecting to Docker Socket")

