FROM slack_builder
WORKDIR /
COPY . .

ENV SLACK_ENV "prod"
CMD ["python", "main.py"]