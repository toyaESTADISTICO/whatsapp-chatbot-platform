# 🤖 WhatsApp Chatbot Platform

Bot de WhatsApp construido con FastAPI, OpenAI GPT-4o mini y desplegado en Google Cloud Run.

## Stack
- Python 3.11 + FastAPI
- OpenAI GPT-4o mini
- WhatsApp Business API (Meta)
- Google Cloud Run

## Variables de entorno necesarias
- WHATSAPP_TOKEN
- PHONE_NUMBER_ID
- OPENAI_API_KEY
- VERIFY_TOKEN

## Despliegue
```bash
gcloud run deploy bot-ingles --source . --region us-central1 --allow-unauthenticated
```
