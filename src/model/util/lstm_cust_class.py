import torch
from torch import nn
from torch.utils.data import Dataset


class SeqDataset(Dataset):
    def __init__(self, data, seq_len, pred_len):
        self.data = data
        self.seq_len = seq_len
        self.pred_len = pred_len

    def __len__(self):
        return len(self.data) - self.seq_len - self.pred_len + 1

    def __getitem__(self, idx):
        seq = self.data[idx : idx + self.seq_len]
        targ = self.data[idx + self.seq_len : idx + self.seq_len + self.pred_len]
        return torch.from_numpy(seq).unsqueeze(-1), torch.from_numpy(targ)


class LSTMRegressor(nn.Module):
    def __init__(self, hidden=32, layers=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=1, hidden_size=hidden, num_layers=layers, batch_first=True
        )
        self.fc = nn.Linear(hidden, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out
