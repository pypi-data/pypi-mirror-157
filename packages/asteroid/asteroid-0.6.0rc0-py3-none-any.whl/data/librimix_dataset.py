import numpy as np
import pandas as pd
import soundfile as sf
import torch
from torch.utils.data.dataset import Dataset
import random as random
import os


class LibriMix(Dataset):
    """" Dataset class for Librimix source separation tasks.

    Args:
        csv_dir (str): The path to the metatdata file
        task (str): One of ``'enh_single'``, ``'enh_both'``, ``'sep_clean'`` or
            ``'sep_noisy'``.

            * ``'enh_single'`` for single speaker speech enhancement.
            * ``'enh_both'`` for multi speaker speech enhancement.
            * ``'sep_clean'`` for two-speaker clean source separation.
            * ``'sep_noisy'`` for two-speaker noisy source separation.

        sample_rate (int) : The sample rate of the sources and mixtures
        n_src (int) : The number of sources in the mixture
        segment (int) : The desired sources and mixtures length in s
    """

    def __init__(self, csv_dir, task, sample_rate=16000,
                 n_src=2, segment=4):
        self.csv_dir = csv_dir
        self.task = task
        # Get the csv corresponding to the task
        if task == 'enh_single':
            md_file = [f for f in os.listdir(csv_dir) if 'single' in f][0]
            self.csv_path = os.path.join(self.csv_dir, md_file)
        elif task == 'enh_both':
            md_file = [f for f in os.listdir(csv_dir) if 'both' in f][0]
            self.csv_path = os.path.join(self.csv_dir, md_file)
            md_clean_file = [f for f in os.listdir(csv_dir) if 'clean' in f][0]
            self.df_clean = pd.read_csv(os.path.join(csv_dir, md_clean_file))
        elif task == 'sep_clean':
            md_file = [f for f in os.listdir(csv_dir) if 'clean' in f][0]
            self.csv_path = os.path.join(self.csv_dir, md_file)
        elif task == 'sep_noisy':
            md_file = [f for f in os.listdir(csv_dir) if 'both' in f][0]
            self.csv_path = os.path.join(self.csv_dir, md_file)
        self.segment = segment
        self.sample_rate = sample_rate
        # Open csv file
        self.df = pd.read_csv(self.csv_path)
        # Get rid of the utterances too short
        if self.segment is not None:
            max_len = len(self.df)
            self.seg_len = int(self.segment * self.sample_rate)
            # Ignore the file shorter than the desired_length
            self.df = self.df[self.df['length'] >= self.seg_len]
            print(f"Drop {max_len - len(self.df)} utterances from {max_len} "
                  f"(shorter than {segment} seconds)")
        else:
            self.seg_len = None
        self.n_src = n_src

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # Get the row in dataframe
        row = self.df.iloc[idx]
        # Get mixture path
        self.mixture_path = row['mixture_path']
        sources_list = []
        # If there is a seg start point is set randomly
        if self.seg_len is not None:
            start = random.randint(0, row['length'] - self.seg_len)
            stop = start + self.seg_len
        else:
            start = 0
            stop = None
        # If task is enh_both then the source is the clean mixture
        if 'enh_both' in self.task:
            mix_clean_path = self.df_clean.iloc[idx]['mixture_path']
            s, _ = sf.read(mix_clean_path, dtype='float32', start=start,
                           stop=stop)
            sources_list.append(s)

        else:
            # Read sources
            for i in range(self.n_src):
                source_path = row[f'source_{i + 1}_path']
                s, _ = sf.read(source_path, dtype='float32', start=start,
                               stop=stop)
                sources_list.append(s)
        # Read the mixture
        mixture, _ = sf.read(self.mixture_path, dtype='float32', start=start,
                             stop=stop)
        # Convert to torch tensor
        mixture = torch.from_numpy(mixture)
        # Stack sources
        sources = np.vstack(sources_list)
        # Convert sources to tensor
        sources = torch.from_numpy(sources)
        return mixture, sources
