import os
import pickle


def save_model(PATH, model, model_id:int, target_id:int):
    initial_dir = PATH
    check = os.path.join(initial_dir, 'models')
    if not os.path.exists(check):
        os.makedirs(check)

    final_directory = os.path.join(initial_dir, 'models', f'{model_id}')

    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    file_name = os.path.join(final_directory, f"{model_id}_{target_id}.pkl")

    with open(file_name, 'wb') as f:
        pickle.dump(model, f)

    return file_name


def get_models(PATH, model_id:int):

    model_dir = os.path.join(PATH, 'models', f'{model_id}')

    model_names = os.listdir(model_dir)

    models = {}
    for name in model_names:
        file_path = os.path.join(model_dir, f'{name}')
        with open(file_path, 'rb') as file:
            model = pickle.load(file)
            models[model.target] = model

    return models

if __name__=='__main__':
    PATH = 'C:/'
    try:
        models = get_models(PATH, 55)
    except FileNotFoundError as err:
        print(err)

