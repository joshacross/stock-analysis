from dotenv import load_dotenv
from pydantic import BaseModel

import uvicorn
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

import yfinance as yf

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


model = ChatOpenAI(
    model = 'c1/openai/gpt-5/v-20250930',
    base_url = 'https://api.thesys.dev/v1/embed/'
)

checkpointer = InMemorySaver()


def _normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def _price_lookup_message(ticker: str) -> str:
    return f'No recent market price was found for ticker "{ticker}". Verify the ticker symbol and try again.'


def _get_last_close(stock: yf.Ticker):
    history = stock.history(period='1d', interval='1m')
    if history.empty or 'Close' not in history:
        return None

    close_prices = history['Close'].dropna()
    if close_prices.empty:
        return None

    return float(close_prices.iloc[-1])


def _get_fallback_price(stock: yf.Ticker):
    fast_info = getattr(stock, 'fast_info', None)
    if fast_info is not None:
        last_price = fast_info.get('lastPrice')
        if last_price is not None:
            return float(last_price)

    info = getattr(stock, 'info', None)
    if info is not None:
        for field in ('currentPrice', 'regularMarketPrice', 'previousClose'):
            price = info.get(field)
            if price is not None:
                return float(price)

    return None


def _serialize_frame(frame: pd.DataFrame) -> dict:
    serialized = frame.copy()
    if isinstance(serialized.index, pd.DatetimeIndex):
        serialized.index = serialized.index.astype(str)

    return serialized.to_dict()


@tool('get_stock_price', description='A function that returns the current stock price based on a ticker symbol.')
def get_stock_price(ticker: str):
    print('get_stock_price tool is being used')
    normalized_ticker = _normalize_ticker(ticker)
    stock = yf.Ticker(normalized_ticker)

    price = _get_last_close(stock)
    if price is None:
        price = _get_fallback_price(stock)

    if price is None:
        return _price_lookup_message(normalized_ticker)

    return price


@tool('get_historical_stock_price', description='A function that returns the current stock price over time based on a ticker symbol and a start and end date.')
def get_historical_stock_price(ticker: str, start_date: str, end_date: str):
    print('get_historical_stock_price tool is being used')
    normalized_ticker = _normalize_ticker(ticker)
    stock = yf.Ticker(normalized_ticker)
    history = stock.history(start=start_date, end=end_date)

    if history.empty:
        return {
            'ticker': normalized_ticker,
            'start_date': start_date,
            'end_date': end_date,
            'message': 'No historical price data was found for the requested date range.',
        }

    return _serialize_frame(history)


@tool('get_balance_sheet', description='A function that returns the balance sheet based on a ticker symbol.')
def get_balance_sheet(ticker: str):
    print('get_balance_sheet tool is being used')
    stock = yf.Ticker(ticker)
    return stock.balance_sheet


@tool('get_stock_news', description='A function that returns news based on a ticker symbol.')
def get_stock_news(ticker: str):
    print('get_stock_news tool is being used')
    stock = yf.Ticker(ticker)
    return stock.news



agent = create_agent(
    model = model,
    checkpointer = checkpointer,
    tools = [get_stock_price, get_historical_stock_price, get_balance_sheet, get_stock_news]
)


class PromptObject(BaseModel):
    content: str
    id: str
    role: str


class RequestObject(BaseModel):
    prompt: PromptObject
    threadId: str
    responseId: str


@app.post('/api/chat')
async def chat(request: RequestObject):
    config = {'configurable': {'thread_id': request.threadId}}

    def generate():
        for token, _ in agent.stream(
            {'messages': [
                SystemMessage('You are a stock analysis assistant. You have the ability to get real-time stock prices, historical stock prices (given a date range), news and balance sheet data for a given ticker symbol.'),
                HumanMessage(request.prompt.content)
            ]},
            stream_mode='messages',
            config=config
        ):
            yield token.content

    return StreamingResponse(generate(), media_type='text/event-stream',
                             headers={
                                 'Cache-Control': 'no-cache, no-transform',
                                 'Connection': 'keep-alive',
                             })

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)