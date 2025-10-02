import torch
import torch.nn as nn
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
        x = torch.tensor(x, dtype=torch.float32).unsqueeze(-1)
        y = torch.tensor(y, dtype=torch.float32)
        return x, y


class LSTMRegressor(nn.Module):
    def __init__(self, hidden=32, layers=2, pred_len=12):
        super().__init__()
        self.pred_len = pred_len
        self.lstm = nn.LSTM(
            input_size=1, hidden_size=hidden, num_layers=layers, batch_first=True
        )
        self.fc = nn.Linear(hidden, pred_len)  # <--- เปลี่ยนจาก 1 เป็น pred_len

    def forward(self, x):
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        pred = self.fc(last)  # (batch, pred_len)  <-- พยากรณ์ 12 เดือนทีเดียว
        return pred
