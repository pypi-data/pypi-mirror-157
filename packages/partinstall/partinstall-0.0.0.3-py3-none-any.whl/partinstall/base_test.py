import os

def test_function(input_str):
    print("Hello :) this is base_test")
    print("your input string is {}".format(input_str))
    print("Bye~~")

model_path = 't3q_folder/model_path'

T3QAI_TRAIN_OUTPUT_PATH = os.path.join(model_path,'t3qai_output')
T3QAI_TRAIN_MODEL_PATH = model_path