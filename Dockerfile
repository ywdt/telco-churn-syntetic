FROM python:3.11-slim

WORKDIR /app

# Копіюємо тільки необхідне (краще для кешу)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/          
COPY .gitignore .               

# Запуск розширеного скрипта через Hydra за замовчуванням
CMD ["python", "src/generate_dataset_ext.py", "generation.samples=50000", "generation.conv_samples=7500"]