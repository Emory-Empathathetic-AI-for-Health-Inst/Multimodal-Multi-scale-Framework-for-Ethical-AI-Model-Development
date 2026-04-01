import torch
from transformers import AutoModel

class BioLinkBERTClass(torch.nn.Module):
    def __init__(self, model_dir, dropout=0.3, num_classes=11):
        super(BioLinkBERTClass, self).__init__()
        self.bert_model = AutoModel.from_pretrained(model_dir)  # BioLinkBERT-large
        self.dropout = torch.nn.Dropout(dropout)
        self.linear = torch.nn.Linear(1024, num_classes)   # hidden_size (number of neurons in the last layer) is 1024 for BioLinkBERT model

    def forward(self, input_ids, attn_mask):
        output = self.bert_model(
            input_ids, 
            attention_mask=attn_mask
        )
        output_dropout = self.dropout(output.last_hidden_state[:, 0, :])
        output = self.linear(output_dropout)
        return output