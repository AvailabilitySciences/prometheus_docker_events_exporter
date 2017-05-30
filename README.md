This project intends to export metrics from the Docker Events stream / Engine api. It allows for monitoring containers life cycle.

To run the project:
docker run --rm -p 8000:8000 -it -v /var/run/docker.sock:/var/run/docker.sock optimalq/prometheus_docker_events_exporter

Another example for an exporter that users statsd , scout and Ruby can be found at:  http://blog.scoutapp.com/articles/2015/06/05/monitoring-docker-events
