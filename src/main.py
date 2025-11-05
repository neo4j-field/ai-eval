import sys
import os
import argparse
from datetime import datetime
from evaluator import Evaluator
from dotenv import load_dotenv

process_dir = os.getcwd()
env_file = os.path.join(process_dir, ".env")
load_dotenv(dotenv_path=env_file, override=True)

def main():
    parser = argparse.ArgumentParser(description="Run evaluation with config files.")
    parser.add_argument("-q", "--questions", required=True, help="Path to questions JSON file")
    parser.add_argument("-k", "--kg_config", required=True, help="Path to KG config JSON file")
    parser.add_argument("-t", "--test_config", required=True, help="Path to test config JSON file")
    parser.add_argument("-c", "--config_dir", required=True, help="Directory where config files are located")
    parser.add_argument("-o", "--output_dir", required=True, help="Directory where output files are stored")
    parser.add_argument("-p", "--output_prefix", required=True, help="Prefix for an output file")

    args = parser.parse_args()

    questions_json = args.questions
    kg_config_json = args.kg_config
    test_config_json = args.test_config
    config_dir = args.config_dir
    output_dir = args.output_dir
    output_prefix = args.output_prefix

    # Get current date/time stamp in the format yyyyMMdd_HHmmss
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    questions_json = os.path.join(config_dir, questions_json)
    kg_config_json = os.path.join(config_dir, kg_config_json)
    test_config_json = os.path.join(config_dir, test_config_json)
    # Compose the output file name
    output_report_path = os.path.join(
        output_dir, f"{output_prefix}_{timestamp}.json"
    )            

    # Prepare config dictionary for Evaluator.get_evaluator
    config = {
        "questions_json_path": questions_json,
        "kg_config_json_path": kg_config_json,
        "test_config_json_path": test_config_json,
        "output_report_path": output_report_path
    }
    print(config)

    evaluator = Evaluator.get_evaluator(config)
    # print("Evaluator instance created successfully.")
    all_results = evaluator.run_evaluation()
    # print(f"All results: {all_results}")
    print(f"Results have been written to: {output_report_path}")

if __name__ == "__main__":
    main()