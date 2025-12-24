import json
from setfit import SetFitModel, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd

# 1. Загружаем якоря
with open("../config/anchors.json", "r", encoding="utf-8") as f:
    anchors = json.load(f)

# 2. Готовим данные для обучения
# Превращаем JSON в таблицу: [текст, метка]
data = []
for label, examples in anchors.items():
    for text in examples:
        data.append({"text": text, "label": label})

df = pd.read_json(json.dumps(data))

# Создаем Dataset
dataset = Dataset.from_pandas(df)

# Кодируем метки (REJECTION -> 0, OFFER -> 1 и т.д.)
labels_list = list(anchors.keys())
label2id = {label: i for i, label in enumerate(labels_list)}
id2label = {i: label for i, label in enumerate(labels_list)}

def encode_labels(record):
    return {"label": label2id[record["label"]]}

dataset = dataset.map(encode_labels)

# 3. Инициализируем модель (берем маленькую и быструю)
# paraphrase-multilingual-MiniLM-L12-v2
model = SetFitModel.from_pretrained("paraphrase-multilingual-MiniLM-L12-v2")

# 4. Настраиваем Тренера
args = TrainingArguments(
    batch_size=16,
    num_epochs=1, # Одного прохода обычно достаточно для якорей
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset,
    eval_dataset=dataset, # Для простоты валидируем на том же, данных мало
    column_mapping={"text": "text", "label": "label"}
)

# 5. ЗАПУСК ОБУЧЕНИЯ
print("Training model...")
trainer.train()

# 6. Сохраняем готовую модель
model.save_pretrained("../training_data/my_email_classifier")
print("Model saved to training_data/my_email_classifier")

# Сохраняем маппинг меток, чтобы сервис знал, что 0 - это REJECTION
with open("my_email_classifier/labels_map.json", "w") as f:
    json.dump(id2label, f)