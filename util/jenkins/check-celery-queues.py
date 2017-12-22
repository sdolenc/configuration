import json
import redis
import click
import boto3
# TODO: Add backoff/retry


@click.command()
@click.option('--host', '-h', default='localhost',
              help='Hostname of redis server')
@click.option('--port', '-p', default=6379, help='Port of redis server')
@click.option('--environment', '-e', required=True)
@click.option('--deploy', '-d', required=True,
              help="Deployment (i.e. edx or edge)")
@click.option('--max-metrics', default=30,
              help='Maximum number of CloudWatch metrics to publish')
def check_queues(host, port, environment, deploy, max_metrics):
    namespace = "celery/{}-{}".format(environment, deploy)
    r = redis.StrictRedis(host=host, port=port)
    cw = boto3.client('cloudwatch')
    metric_name = 'queue_length'
    dimension = 'queue'
    response = cw.list_metrics(Namespace=namespace, MetricName=metric_name,
                               Dimensions=[{'Name': dimension}])
    print(json.dumps(response["Metrics"], indent=2, sort_keys=True))
    existing_queues = []
    for m in response["Metrics"]:
        existing_queues.extend(
            [d['Value'] for d in m["Dimensions"] if d['Name'] == dimension])
    print("existing {}".format(existing_queues))

    redis_queues = set([k.decode() for k in r.keys() if r.type(k) == b'list'])

    all_queues = existing_queues + list(
        set(redis_queues).difference(existing_queues)
    )
    print("rq {}".format(redis_queues))
    print("eq {}".format(existing_queues))
    print("aq {}".format(all_queues))

    if len(all_queues) > max_metrics:
        # TODO: Use proper logging framework
        print("Warning! Too many metrics, refusing to publish more than {}".format(max_metrics))

    # Take first max_metrics number of queues from all_queues and remove
    # queues that aren't in redis
    queues = [ q for q in all_queues[:max_metrics] if q in redis_queues ]

    metric_data = []
    for queue in queues:
        metric_data.append({
            'MetricName': metric_name,
            'Dimensions': [{
                "Name": dimension,
                "Value": queue
            }],
            'Value': r.llen(queue)
        })

    print(metric_data)
    response = cw.put_metric_data(Namespace=namespace, MetricData=metric_data)


if __name__ == '__main__':
    check_queues()
