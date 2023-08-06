
def get_result_model_json(class_name: str, instance_dict: dict) -> dict:
    return {
        'model_name': class_name,
        class_name: instance_dict,
    }
