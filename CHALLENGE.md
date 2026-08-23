# Crypto Portfolio Agent Challenge

Source: `/Users/rafaellopez/Documents/AI Engineer/ai-workspace/live-coding/instructions.md`

## Objective

Build an **AI agent** that helps users construct a basic cryptocurrency portfolio tailored to their **budget**, **risk level**, and **preferences**.

The agent should intelligently suggest how to allocate the budget across a curated selection of cryptocurrencies using live data.

## Environment Setup

1. Set up a Python development environment.
2. Choose a framework for building agentic applications, such as:
   - `LangChain`
   - `LangGraph`
   - `Autogen`
   - `Pydantic-AI`
3. Sign up at [Groq Console](https://console.groq.com/) or run a local model using tools such as:
   - Ollama
   - LM Studio
4. Get an API key from [CoinMarketCap](https://coinmarketcap.com/api/) or another crypto market data provider.

## CoinMarketCap Notes

Sample CoinMarketCap request to get a BTC quote in USD:

```text
https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?symbol=BTC&convert=USD
```

HTTP auth header:

```text
X-CMC_PRO_API_KEY
```

Price extraction from the v2 API:

```python
data["data"]["BTC"][0]["quote"]["USD"]["price"]
```

Alternative v1 API extraction:

```python
data = response
price = list(
    filter(lambda x: x["symbol"] == ticker, data["data"])
)[0]["quote"][currency]["price"]
```

## Requirements

### Core Functionality

Build an AI agent that understands the following user inputs:

- **Budget**, for example: `$1000`
- **Risk level**:
  - `low`
  - `medium`
  - `high`
- **Optional coin preferences**, for example:
  - `prefer BTC`
  - `exclude meme coins`

The agent must fetch current market data:

- Current price for each ticker.
- Nice to have:
  - Top trending coins.
  - Market caps.

The agent must determine a list of coins appropriate for the selected risk profile.

The agent must allocate the budget across **3 to 5 cryptocurrencies**.

The final output must include:

- Coin name and ticker.
- Amount to invest.
- Price at time of suggestion.
- Quantity to acquire.
- Brief description of the coin.

Descriptions may come from:

- Wikipedia.
- CoinMarketCap.
- LLM-generated summaries.
- Another reliable source.

## Sample Input

```text
I want to invest $1000 in low risk cryptocurrencies and prefer BTC.
```

## Expected Output Example

```text
Here's a suggested portfolio based on your preferences:

1. BTC (Bitcoin)
   - Invest: $500
   - Price: $80,000
   - Quantity: 0.00625
   - About: Bitcoin is the first and most widely recognized cryptocurrency...

2. ETH (Ethereum)
   - Invest: $300
   - Price: $1,600
   - Quantity: 0.1875
   - About: Ethereum is a blockchain platform that supports smart contracts...

3. PAXG (Paxos Gold)
   - Invest: $200
   - Price: $3,400
   - Quantity: 0.0588
   - About: Paxos Gold is a gold-backed digital asset...
```

## Suggested Implementation Steps

1. **Agent Setup**
   - Build the main agent.
   - Verify it can parse and respond to basic queries.

2. **Tools**
   - Add a tool that fetches live crypto prices.
   - Add a separate tool or sub-agent to classify coins by risk level.

3. **Allocation Logic**
   - Implement logic to split the budget based on coin weights.
   - Apply coin preference constraints, such as excluding meme coins.

4. **Serving the Agent**
   - Build an API endpoint to serve the agent.
   - Suggested frameworks:
     - FastAPI
     - Flask
     - Starlette

## Bonus Features

### Chat History / Multi-Turn Dialog

Maintain session context to allow follow-up questions, for example:

```text
Can I swap ETH for SOL?
```

### Knowledge Retrieval

Summarize coin descriptions using:

- LLMs.
- Wikipedia.
- CoinMarketCap.
- External sources.

Optionally store and retrieve this data from a vector database:

- Chroma.
- FAISS.

### Prompt Engineering

Use prompt engineering techniques to improve agent behavior.

Reference: [Prompt Engineering Guide](https://www.promptingguide.ai/)

Consider using a consistent style or template for different types of prompts.
