#!/bin/bash
cd /home/kavia/workspace/code-generation/autonomous-trading-bot-with-news-sentiment-analysis-217592-217603/trading_bot_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

