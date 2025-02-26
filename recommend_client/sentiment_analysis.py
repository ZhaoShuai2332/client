from transformers import BertTokenizer, BertForSequenceClassification
import torch


def bert_sentiment_analysis(text):
    bert_path = './bert_model/sentiment_model/'

    tokenizer = BertTokenizer.from_pretrained(bert_path)
    bert_model = BertForSequenceClassification.from_pretrained(bert_path, num_labels=5, ignore_mismatched_sizes=True)

    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = bert_model(**inputs)

    probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
    predicted_score = torch.argmax(probabilities, dim=1).item()

    return predicted_score
