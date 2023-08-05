import argparse
import json

from dkdisc.utils.experiment import ExperimentConfig

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="append")
    args = parser.parse_args()
    for experiment_config_loc in args.config:
        with open(experiment_config_loc, "r") as experiment_config_file:
            experiment_config_json = json.load(experiment_config_file)
            experiment_config = ExperimentConfig.from_json(experiment_config_json)
            experiment_config.run_experiments()

if __name__ == '__main__': 
    main()
