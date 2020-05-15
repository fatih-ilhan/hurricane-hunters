from dataset import HurrDataset
from torch.utils.data import DataLoader


class BatchGenerator:
    def __init__(self, hurricane_list, **params):
        self.hurricane_list = hurricane_list
        self.params = params

        self.input_dim = params['input_dim']
        self.output_dim = params['output_dim']
        self.batch_size = params['batch_size']
        self.test_ratio = params['test_ratio']
        self.val_ratio = params['val_ratio']
        self.shuffle = params['shuffle']
        self.num_works = params.get('num_works', 1)

        self.data_dict = self._split_data()
        self.dataset_dict, self.data_loader_dict = self._create_sets()

    def _split_data(self):
        data_len = len(self.hurricane_list)

        test_count = int(data_len * self.test_ratio)
        val_count = int(data_len * self.val_ratio)

        data_dict = {
            'test': self.hurricane_list[:test_count],
            'validation': self.hurricane_list[test_count:test_count+val_count],
            'train': self.hurricane_list[test_count+val_count:]
        }

        return data_dict

    def _create_sets(self):
        hurricane_dataset = {}
        for i in ['test', 'validation', 'train']:
            hurricane_dataset[i] = HurrDataset(hurricane_list=self.data_dict[i],
                                          **self.params)

        hurricane_loader = {}
        for i in ['test', 'validation', 'train']:
            hurricane_loader[i] = DataLoader(hurricane_dataset[i],
                                             batch_size=self.batch_size,
                                             shuffle=self.shuffle,
                                             drop_last=False)

        return hurricane_dataset, hurricane_loader

    def generate(self, dataset_type):
        selected_loader = self.data_loader_dict[dataset_type]
        yield from selected_loader


if __name__ == '__main__':
    from data_creator import DataCreator

    params = {
        'batch_size': 4,
        'test_ratio': 0.1,
        'val_ratio': 0.1,
        'shuffle': True,
        'num_works': 0,
        'window_len': 10,
        'output_dim': [0, 1]
    }

    data_creator = DataCreator(hurricane_path='data/ibtracs.NA.list.v04r00.csv', season_range=(1994, 2020))
    batch_generator = BatchGenerator(hurricane_list=data_creator.hurricane_list, **params)

    for x, y in batch_generator.generate('train'):
        print(x.shape, y.shape)
