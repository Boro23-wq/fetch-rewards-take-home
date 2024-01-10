import requests
import time
import yaml
from collections import defaultdict


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def make_request(request_config):
    method = request_config.get('method', 'GET')
    name = request_config['name']
    url = request_config['url']
    headers = request_config.get('headers', {})
    body = request_config.get('body', None)

    start_time = time.time()

    try:
        if method == 'GET':
            if 'headers' in request_config:
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=body)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Convert to milliseconds
        response_time = (time.time() - start_time) * 1000

        if 200 <= response.status_code < 300 and response_time < 500:
            status = 'UP'
            # print(
            #     f"Endpoint with name {name} has HTTP response code 200 and response latency {response_time} ms => UP")
        else:
            status = 'DOWN'
            # print(
            #     f"Endpoint with name {name} has HTTP response code 500 and response latency {response_time} ms => DOWN")
    except Exception as e:
        status = 'DOWN'
        response_time = None

    return status


def calculate_availability(availability_count, total_count):
    # no requests have been made to the domain
    if total_count == 0:
        return 100.0
    # formula for calculating availability percentage
    return (availability_count / total_count) * 100.0


def main():
    config_path = 'config.yaml'
    config = load_config(config_path)

    availability_count = {}

    try:
        while True:
            print(availability_count)
            for request_config in config:
                status = make_request(request_config)
                domain = request_config['url'].split('//')[1].split('/')[0]

                if domain not in availability_count:
                    availability_count[domain] = {'up': 0, 'total': 0}

                # takes into account - how many requests to each domain?
                availability_count[domain]['total'] += 1

                if status == 'UP':
                    availability_count[domain]['up'] += 1

            for domain, stats in availability_count.items():
                domain_availability = calculate_availability(
                    stats['up'], stats['total'])
                rounded_availability = round(domain_availability)
                print(
                    f"{domain} has {rounded_availability}% availability percentage")

            time.sleep(15)

    except KeyboardInterrupt:
        print("Exiting the program.")


if __name__ == "__main__":
    main()
