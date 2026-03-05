import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer
import logging
import warnings

warnings.filterwarnings('ignore')

# --- Placeholders for Advanced Deep Learning Models (Future Upgrade) ---

class SequenceTaggingBiLSTM(nn.Module):
    """
    Bi-LSTM Architecture for sequence tagging (e.g., highly accurate
    skill sequence extraction from chaotic free-text).
    """
    def __init__(self, vocab_size, embedding_dim, hidden_dim, target_size):
        super(SequenceTaggingBiLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, bidirectional=True, batch_first=True)
        self.hidden2tag = nn.Linear(hidden_dim * 2, target_size)

    def forward(self, sentence):
        embeds = self.embedding(sentence)
        lstm_out, _ = self.lstm(embeds)
        tag_space = self.hidden2tag(lstm_out)
        tag_scores = torch.log_softmax(tag_space, dim=2)
        return tag_scores


class ResumeJobClassifierBERT(nn.Module):
    """
    Fine-tuned BERT for binary classification: Match vs No-Match
    or Multi-class classification for Job Categories.
    """
    def __init__(self, num_classes=2):
        super(ResumeJobClassifierBERT, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits

class AttentionRankingModel(nn.Module):
    """
    Attention-based custom ranking architecture to weigh different sections
    of the resume differently based on the JD.
    """
    def __init__(self, hidden_dim):
        super(AttentionRankingModel, self).__init__()
        self.attention = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=4, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1) # Single rank score output

    def forward(self, resume_features, jd_features):
        # Queries from JD, Keys/Values from Resume
        attn_output, _ = self.attention(query=jd_features, key=resume_features, value=resume_features)
        
        # Aggregate and score
        pooled = torch.mean(attn_output, dim=1)
        score = torch.sigmoid(self.fc(pooled))
        return score * 100.0 # Scale 0-100
