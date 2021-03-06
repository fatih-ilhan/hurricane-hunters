import torch
import numpy as np


class HurrDataset:
    def __init__(self, hurricane_list, weather_list, **params):
        self.hurricane_list = hurricane_list
        self.weather_list = weather_list

        self.data_len = len(self.hurricane_list)
        # I've assumed input and output window_len are equal
        self.batch_size = params['batch_size']
        self.window_len = params['window_len']
        # self.stride = params['stride']
        self.phase_shift = params['phase_shift']
        self.cut_start = params['cut_start']
        self.return_mode = params['return_mode']
        if self.return_mode == 'weather':
            self.weather_input_dim = params['weather_input_dim']
        elif self.return_mode == 'hurricane':
            self.hur_input_dim = params['hur_input_dim']
        else:
            raise KeyError("return mode: {}".format(self.return_mode))
        self.hur_output_dim = params['hur_output_dim']
        self.vector_mode = params['vector_mode']
        self.vec_freq = params['vector_freq']
        self.atm_levels = params['atm_levels']

        self.__count = 0

    def next(self):
        skip_count = 0
        for idx in range(self.data_len):
            self.__count = idx
            hur_path = self.hurricane_list[idx]
            weather_path = self.weather_list[idx]

            # load hurricane sample
            hur_name = hur_path.split('_')[-1].split('.')[0]
            hur_data = np.load(hur_path, allow_pickle=True)

            if self.vector_mode:
                hur_data = self._create_vectors(data=hur_data)

            # check whether we can create enough batches from it
            t_dim = hur_data.shape[0]
            if t_dim < (self.window_len * self.batch_size):
                skip_count += 1
                continue

            if self.return_mode == 'weather':
                # load weather sample and format
                weather_data = np.load(weather_path, allow_pickle=True)
                weather_data = weather_data[..., self.weather_input_dim]

                # reshape weather sample
                weather_data = weather_data[:, self.atm_levels]
                t, l, m, n, d = weather_data.shape
                weather_data = np.transpose(weather_data, (0, 2, 3, 1, 4))
                weather_data = weather_data.reshape((t, m, n, d*l))

                # generate batch
                x_buff = self._create_buffer(data=weather_data)
                y_buff = self._create_buffer(data=hur_data,
                                             chosen_dims=self.hur_output_dim,
                                             phase_shift=self.phase_shift)

            else:
                # generate batch
                x_buff = self._create_buffer(data=hur_data, chosen_dims=self.hur_input_dim)
                y_buff = self._create_buffer(data=hur_data,
                                             chosen_dims=self.hur_output_dim,
                                             phase_shift=self.phase_shift)

            if len(y_buff) == 0 or len(x_buff) == 0:
                skip_count += 1
                continue

            # return batches
            for i in range(len(y_buff)):

                # convert to tensor
                x = torch.tensor(x_buff[i], dtype=torch.float32)
                y = torch.tensor(y_buff[i], dtype=torch.float32)

                yield x, y

        print('Skipped {} hurricanes\n'.format(skip_count))

    def _create_vectors(self, data):
        y_list = []
        for i in range(len(data)):
            if i + self.vec_freq < len(data):
                delta = data[i + self.vec_freq, :2] - data[i, :2]
                y_list.append(delta)

        y_arr = np.array(y_list)
        return y_arr

    def _create_buffer(self, data, chosen_dims=None, phase_shift=0):
        data = self._configure_data(data=data, phase_shift=phase_shift)
        total_frame = data.shape[1]

        stacked_data = []
        for i in range(0, total_frame, self.window_len):
            batch = data[:, i:i+self.window_len]
            if chosen_dims is not None:
                batch = batch[..., chosen_dims]
            stacked_data.append(batch)

        return stacked_data

    def _configure_data(self, data, phase_shift):
        data = data[phase_shift:]
        t_dim = data.shape[0]
        other_dims = data.shape[1:]

        # Keep only enough time steps to make full batches
        n_batches = t_dim // (self.batch_size * self.window_len)
        if self.cut_start:
            start_time_step = t_dim - (n_batches * self.batch_size * self.window_len)
            data = data[start_time_step:]
        else:
            end_time_step = n_batches * self.batch_size * self.window_len
            data = data[:end_time_step]

        # Reshape into batch_size rows
        data = data.reshape((self.batch_size, -1, *other_dims))

        return data

    def __len__(self):
        return self.data_len

    @property
    def count(self):
        return self.__count
