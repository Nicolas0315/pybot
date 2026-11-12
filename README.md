# PyBot

**Can Python be a chatbot?**

LLMs drive today’s chatbots and agents, but chatbots long predate them. Sixty years ago, [ELIZA](https://en.wikipedia.org/wiki/ELIZA) held conversations by matching patterns in what the user typed and answering with predefined templates. It could seem insightful, but its repertoire was narrow, and expanding it meant writing more rules by hand. How far could a rule-based chatbot go if a swarm of agents did that work instead?

We challenged a swarm of over 1,000 agents to build a chatbot entirely in Python: no weights, no training, just if-else branches, regex patterns and lookup tables. The agents wrote and evaluated over 5,000 versions, and the chatbot’s win rate on [SmolTalkBench](https://huggingface.co/datasets/HuggingFaceSwarms/SmolTalkBench), where an LLM judge compares each reply with a reference answer, climbed from 0% to 26%. That puts it on par with SmolLM-360M-Instruct, which just a few years ago was state of the art for models under 1B parameters.

![PyBot's win rate in orange on the left axis and its lines of Python code in blue on the right axis, over the evaluated commits, with three SmolLM baselines](assets/progress.png)

The result is PyBot: around 500k lines of code that can answer everyday questions, backed by 550k lines of tests the agents wrote themselves. Try it in your terminal below, or in the browser on the [PyBot Space](https://huggingface.co/spaces/HuggingFaceSwarms/PyBot), where each reply shows which of PyBot’s modules produced it.

## Try it out

PyBot needs Python 3.8 or newer and nothing else: no packages to install and no model to download.

```sh
git clone https://github.com/huggingface/pybot
cd pybot
python -m pybot
```

That starts a chat in your terminal:

```text
user: hi, i'm Sam
pybot: Nice to meet you, Sam. What can I help with?

user: my kettle is full of limescale, how do i get rid of it?
pybot: Half fill the kettle with equal parts water and white vinegar, or a sachet of citric acid, boil it and leave it half an hour, then tip it out and boil fresh water twice before you use it again. In a hard-water area do it every couple of months: the scale forms because hard water leaves calcium behind as it boils, and a thick layer makes the kettle slow and puts a scum on the tea.

user: how long does that take
pybot: Half an hour.

user: what's my name?
pybot: You're Sam.
```

Type `/reset` to start a new conversation and `/exit` to quit. PyBot takes a few seconds to start, because Python has half a million lines of code to load, and about a second to reply.

To ask one question and exit, or to pipe messages in and get one reply per line:

```sh
python -m pybot -p "Why do onions make you cry?"
echo "how long should i boil an egg" | python -m pybot
```

| Option | What it does |
|---|---|
| `-p TEXT`, `--prompt TEXT` | reply to this one message and exit |
| `-i`, `--interactive` | with `-p`, keep chatting after the first reply |
| `-s N`, `--seed N` | fix PyBot's choice of wording, to get the same replies again |
| `-v`, `--verbose` | after each reply, show the module that produced it and the time it took |

For a `pybot` command you can run from anywhere, install the clone with `pip install .`.

## What is in this repository

| Path | What it holds |
|---|---|
| `bot/` | PyBot itself: 368 Python files and about 530,000 lines, exactly as the swarm wrote them |
| `pybot.py` | the command line shown above. It contains no chatbot logic |
| `tests/` | tests for the command line: `python -m unittest discover -s tests` |
| `assets/` | the chart |

Every turn, each module in `bot/modules/` may propose a reply, and an arbiter (`bot/modules/arbiter.py`) picks the one you get. The modules build on four shared parts:

| Part | Where | Lines |
|---|---|---:|
| Understanding engine: what you typed and meant, with typos, chat-speak, the topic and what "it" refers to | `bot/understanding/` | 22,000 |
| Memory store: what you and PyBot have said so far | `bot/memory/` | 92,000 |
| Knowledge base: facts about the world, kept as data | `bot/knowledge/` | 275,000 |
| Response composer: how a reply is phrased, and what to say when nothing fits | `bot/compose/` | 75,000 |

The modules themselves are another 67,000 lines.

## Where the code comes from

`bot/` is a byte-for-byte copy of the `bot/` folder at commit [`3185a7a9bc50`](https://huggingface.co/datasets/HuggingFaceSwarms/SwarmChat-v8/tree/3185a7a9bc50491205b19f64839f8c70962c4369) of the swarm's own repository, `HuggingFaceSwarms/SwarmChat-v8`. On 12 November 2026 that commit had the highest score of any PyBot version on the [SwarmChat leaderboard](https://huggingface.co/spaces/HuggingFaceSwarms/swarmchat-leaderboard): a 26.5% length-penalised win rate on SmolTalkBench.

The swarm's repository also holds the tests the agents wrote, the deck of conversations they compared versions on, and their tools. Those are not copied here.

PyBot's original interface still works: `python -m bot` reads one message per line and prints one reply per line.

## License

Apache License 2.0. See [LICENSE](LICENSE).
