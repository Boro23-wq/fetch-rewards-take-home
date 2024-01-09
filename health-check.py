import yaml


def load_sample_input():
    with open('config.yaml', 'r') as input_file:
        return yaml.safe_load(input_file)


input = load_sample_input()
print(input)
