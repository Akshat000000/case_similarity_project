from datasets import load_dataset

def load_cjpe(split="single_train", limit=None):
    """
    Loads CJPE dataset from Hugging Face.

    Args:
        split (str): train / test
        limit (int): number of samples to load (for testing)

    Returns:
        dataset: HuggingFace Dataset object
    """
    dataset = load_dataset("Exploration-Lab/IL-TUR", "cjpe", split=split)

    if limit:
        real_limit = min(limit, len(dataset))
        dataset = dataset.select(range(real_limit))

    return dataset
