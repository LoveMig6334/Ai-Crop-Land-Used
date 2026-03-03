import torch.nn as nn


class LSTMRegressor(nn.Module):
    def __init__(self, hidden=32, layers=2, pred_len=12):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=1, hidden_size=hidden, num_layers=layers, batch_first=True
        )
        self.fc = nn.Linear(hidden, pred_len)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])  # (batch, pred_len)
