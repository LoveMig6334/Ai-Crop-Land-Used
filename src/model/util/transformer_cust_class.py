import math

import torch
from torch import nn
from torch.utils.data import Dataset


class SeqDataset(Dataset):
    def __init__(self, data, seq_len=12, pred_len=12):
        self.data = data
        self.seq_len = seq_len
        self.pred_len = pred_len

    def __len__(self):
        return len(self.data) - self.seq_len - self.pred_len + 1

    def __getitem__(self, idx):
        x = self.data[idx : idx + self.seq_len]
        y = self.data[idx + self.seq_len : idx + self.seq_len + self.pred_len]
        return torch.from_numpy(x).unsqueeze(-1), torch.from_numpy(y)


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        x = x + self.pe[:, : x.size(1)]
        return x


class TransformerRegressor(nn.Module):
    def __init__(
        self, d_model=64, nhead=8, num_layers=2, dim_feedforward=128, PRED_LEN=12
    ):
        super().__init__()
        self.input_proj = nn.Linear(1, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.decoder = nn.Linear(d_model, PRED_LEN)

    def forward(self, x):
        x = self.input_proj(x)
        x = self.pos_encoder(x)
        enc_out = self.encoder(x)
        out = self.decoder(enc_out[:, -1, :])
        return out
