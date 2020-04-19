import torch
import numpy as np

from torch.utils.data import Dataset


class HurrDataset(Dataset):
    def __init__(self, hurricane_list, **params):
        self.hurricane_list = hurricane_list
        # TODO: I've assumed input and output window_len are equal
        self.window_len_input = params['window_len_input']
        self.window_len_output = params['window_len_output']
        self.stride = params['stride']
        self.input_dim = params['input_dim']
        self.output_dim = params['output_dim']
        self.data, self.label = self._create_buffer()

    def _create_buffer(self):
        x_buffer = []
        y_buffer = []
        for hurricane in self.hurricane_list:
            for n in range(0, hurricane.shape[0] - (self.window_len_input + self.window_len_output), self.stride):
                x = hurricane[n:n+self.window_len_input, :]
                y = np.zeros_like(x)
                try:
                    # targets shifted by one
                    y[:-1], y[-1] = x[1:], hurricane[n+self.window_len_output]
                except IndexError:
                    continue

                x_buffer.append(x)
                y_buffer.append(y)

        # target and data are in shape of (N, window_len, D)
        x_buffer = np.stack(x_buffer, axis=0)
        y_buffer = np.stack(y_buffer, axis=0)

        x_buffer = torch.Tensor(x_buffer)
        y_buffer = torch.Tensor(y_buffer)

        return x_buffer, y_buffer

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, idx):
        return self.data[idx, :, self.input_dim], self.label[idx, :, self.output_dim]
