import redis
import click
import boto3
import json

host = 'localhost'

@click.command()
@click.option('--host', '-h', default='localhost', help='Hostname of redis servre')
@click.option('--port', '-p', default=6379, help='Port of redis server')
@click.option('--environment', '-e', required=True)
@click.option('--deploy', '-d', help="Deployment (i.e. edx or edge)", required=True)
@click.option('--max-metrics', default=30, help='Maximum number of CloudWatch metrics to publish')
def check_queues(host, port, environment, deploy, max_metrics):

    namespace="celery/{}-{}".format(environment,deploy)
#    namespace="AWS/EC2"

    r = redis.StrictRedis(host=host, port=port)
    cw = boto3.client('cloudwatch')
    
#    response = cw.list_metrics()
#    print(json.dumps(response["Metrics"], indent=2, sort_keys=True))
#    existing_metrics=set([metric["MetricName"] for metric in response["Metrics"]])
#    print(existing_metrics)

    queues = [ k for k in r.keys() if r.type(k) == b'list' ]

    # Prevent generating too many clouwatch metrics
    if len(queues) > max_metrics:
        sys.exit(1)
   
    queue_length = {}
    for queue in queues:
        queue_length[queue.decode()] = r.llen(queue)

    for queue, length in queue_length.items():

        print("{}: {}".format(queue, length))
        response = cw.put_metric_data(
            Namespace=namespace,
            MetricData=[{
                'MetricName': 'queue_length',
                'Dimensions': [
                    {
                        'Name': 'queue_name',
                        'Value': queue
                    }
                ],
                'Value': length
            }]
        )

if __name__ == '__main__':
    check_queues()
