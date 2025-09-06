FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV PYTHONPATH=/app
EXPOSE 5001 8501
CMD ["bash","-lc","python scripts/generate_lms_data.py && python src/risk_engine/train.py && python src/risk_engine/predict.py && streamlit run src/dashboard/streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]