import requests
import time
import yaml


#  load config.yaml file that has the HTTP endpoints
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def make_request(request_config):
    # retrieve necessary values for HTTP request. eg method = POST, url = https://fetch.com etc.
    method = request_config.get('method', 'GET')
    name = request_config['name']
    url = request_config['url']
    headers = request_config.get('headers', {})
    body = request_config.get('body', None)

    start_time = time.time()

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=body)
        else:
            # raise an error if incorrect method - eg. PST instead of POST
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Convert to milliseconds
        response_time = round((time.time() - start_time) * 1000)

        # calculate status code and response time to determine UP or DOWN outcome
        if 200 <= response.status_code < 300 and response_time < 500:
            status = 'UP'
            print(
                f"Endpoint with name {name} has HTTP response code 200 and response latency {response_time} ms => UP")
        else:
            status = 'DOWN'
            print(
                f"Endpoint with name {name} has HTTP response code 500 and response latency {response_time} ms => DOWN")
    except Exception as e:
        # print the error we raised earlier
        print(e)
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
    cycle = 1

    try:
        # loop through indefinitely until user manually exits
        while True:
            # print(availability_count)
            print(f"\n --- Test cycle #{cycle} begins --- \n")
            for request_config in config:
                status = make_request(request_config)
                # just retrive domain - https://fetch.com/careers -> fetch.com
                domain = request_config['url'].split('//')[1].split('/')[0]

                # initial setup - for each new domain add to the empty dict
                if domain not in availability_count:
                    availability_count[domain] = {'up': 0, 'total': 0}

                # takes into account - how many requests to each domain?
                availability_count[domain]['total'] += 1

                # how many ups for each domain
                if status == 'UP':
                    availability_count[domain]['up'] += 1

            print(f"\n --- Test cycle #{cycle} ends --- \n")

            # print(availability_count.items()) - eg. dict_items([('fetch.com', {'up': 0, 'total': 0}), ('www.fetchrewards.com', {'up': 0, 'total': 0})])

            print(f" Result:\n")
            for domain, stats in availability_count.items():
                # calculate availability
                domain_availability = calculate_availability(
                    stats['up'], stats['total'])
                rounded_availability = round(domain_availability)
                print(
                    f"{domain} has {rounded_availability}% availability percentage")

            cycle += 1
            # run test cycle every 15s
            time.sleep(15)

    except KeyboardInterrupt:
        print("Exiting the program...")


if __name__ == "__main__":
    main()
