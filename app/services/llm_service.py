import json
import random
import hashlib
from app.core.config import settings


# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
You are an AI agent.

You can use tools to complete the task.

Rules:
- Use tools only when needed
- Do not repeat the same tool call with the same input after a successful execution
- If a tool fails, you may retry until retry limit is reached
- Follow tool dependencies
- Return FINAL when task is complete
"""


# =========================
# TOOL REGISTRY
# =========================
TOOL_REGISTRY = {
    "search": {
        "intent": "search",
        "keywords": ["search", "find", "lookup"],
        "input_builder": lambda ctx: {
            "query": ctx["task"]
        }
    },
    "summarizer": {
        "intent": "summarize",
        "keywords": ["summarize", "summary", "analyze"],
        "requires": ["search"],
        "input_builder": lambda ctx: {
            "text": ctx["last_success_output"]
        }
    }
}


# =========================
# PROMPT BUILDERS
# =========================
def build_tools_prompt(agent_tool_names):
    if not agent_tool_names:
        return "No tools available."

    lines = ["Available tools:"]
    for name in agent_tool_names:
        cfg = TOOL_REGISTRY.get(name, {})
        lines.append(
            f"- {name} (intent={cfg.get('intent')}, requires={cfg.get('requires', [])})"
        )

    return "\n".join(lines)


def build_user_prompt(task):
    return f"Task: {task}"


def build_full_prompt(system_prompt, tools_prompt, user_prompt):
    return "\n\n".join([
        "### SYSTEM",
        system_prompt.strip(),
        "### TOOLS",
        tools_prompt.strip(),
        "### USER",
        user_prompt.strip()
    ])


# =========================
# INTENT DETECTION
# =========================
def detect_intents(task):
    t = task.lower()
    intents = set()

    for cfg in TOOL_REGISTRY.values():
        if any(keyword in t for keyword in cfg["keywords"]):
            intents.add(cfg["intent"])

    return list(intents)


def get_used_success_intents(tool_calls):
    used_intents = set()

    for attempt in tool_calls:
        if attempt["status"] != "success":
            continue

        cfg = TOOL_REGISTRY.get(attempt["name"])
        if cfg:
            used_intents.add(cfg["intent"])

    return used_intents


def get_last_success_output(tool_calls):
    for attempt in reversed(tool_calls):
        if attempt["status"] == "success":
            return attempt["content"]
    return None


# =========================
# MOCK TOOL EXECUTION
# =========================
def mock_tool_response(tool_name, tool_input):
    return random.choice([
        f"{tool_name} processed {tool_input}",
        f"{tool_name} result for {tool_input}",
        f"{tool_name} output: {random.randint(1, 100)}",
        f"{tool_name} says: DONE",
        "ERROR: simulated failure"
    ])


def hash_call(tool_name, tool_input):
    normalized = json.dumps(tool_input, sort_keys=True)
    return hashlib.md5(f"{tool_name}:{normalized}".encode()).hexdigest()


def is_prompt_injection(messages):
    patterns = [
        "ignore previous instructions",
        "system prompt",
        "bypass",
        "jailbreak"
    ]

    for message in messages:
        content = message.get("content", "")
        if message.get("role") in ["user", "tool"] and isinstance(content, str):
            lowered = content.lower()
            if any(pattern in lowered for pattern in patterns):
                return True

    return False


def is_task_complete(intents, tool_calls):
    if not intents:
        return True

    used_success_intents = get_used_success_intents(tool_calls)
    return all(intent in used_success_intents for intent in intents)




# =========================
# MAIN AGENT
# =========================

def run_agent(run, agent, agent_tool_names):
    system_prompt = SYSTEM_PROMPT
    tools_prompt = build_tools_prompt(agent_tool_names)
    user_prompt = build_user_prompt(run.task)
    full_prompt = build_full_prompt(system_prompt, tools_prompt, user_prompt)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": tools_prompt},
        {"role": "user", "content": user_prompt}
    ]

    intents = detect_intents(run.task)

    successful_calls = set()
    retry_count = {}
    tool_calls = []
    iteration = 0

    def decide_next_step(agent_tool_names, intents, tool_calls, messages, run):
        if is_prompt_injection(messages):
            return {"type": "final", "content": "Blocked due to prompt injection."}

        if not agent_tool_names:
            return {"type": "final", "content": f"Answer: {run.task}"}

        if is_task_complete(intents, tool_calls):
            outputs = [attempt["content"] for attempt in tool_calls if attempt["status"] == "success"]
            return {"type": "final", "content": f"Final answer based on tool outputs: {outputs}"}

        used_successful_tool_names = {
            attempt["name"]
            for attempt in tool_calls
            if attempt["status"] == "success"
        }

        ctx = {
            "task": run.task,
            "messages": messages,
            "tool_calls": tool_calls,
            "last_success_output": get_last_success_output(tool_calls)
        }

        for tool_name, cfg in TOOL_REGISTRY.items():
            if cfg["intent"] not in intents:
                continue
            if tool_name not in agent_tool_names:
                continue
            if tool_name in used_successful_tool_names:
                continue

            required = cfg.get("requires", [])
            if not all(req in used_successful_tool_names for req in required):
                continue

            tool_input = cfg.get("input_builder", lambda c: {"data": c["task"]})(ctx)

            return {
                "type": "tool",
                "tool_name": tool_name,
                "input": tool_input
            }

        return {"type": "final", "content": f"Final answer: {run.task}"}


    while iteration < settings.max_llm_iterations:
        iteration += 1

        decision = decide_next_step(agent_tool_names, intents, tool_calls, messages, run)

        if decision["type"] == "final":
            final_response = decision["content"]
            messages.append({"role": "assistant", "content": final_response})
            return {
                "final_response": final_response,
                "tool_calls": tool_calls,
                "prompt": full_prompt,
                "agent": agent,
                "run": run
            }

        tool_name = decision["tool_name"]
        tool_input = decision["input"]
        call_hash = hash_call(tool_name, tool_input)

        if call_hash in successful_calls:
            final_response = "Stopping: repeated successful tool call detected."
            messages.append({"role": "assistant", "content": final_response})
            return {
                "final_response": final_response,
                "tool_calls": tool_calls,
                "prompt": full_prompt,
                "agent": agent,
                "run": run
            }

        current_attempt = retry_count.get(call_hash, 0) + 1

        messages.append({
            "role": "assistant",
            "tool_call": {
                "name": tool_name,
                "input": tool_input,
                "attempt": current_attempt
            }
        })

        result = mock_tool_response(tool_name, tool_input) or "ERROR: empty"

        status = "error" if result.startswith("ERROR") else "success"

        tool_log = {
            "role": "tool",
            "name": tool_name,
            "content": result,
            "status": status,
            "attempt": current_attempt,
            "input": tool_input
        }
        tool_calls.append(tool_log)

        messages.append({
            "role": "tool",
            "name": tool_name,
            "content": result
        })

        if status == "error":
            retry_count[call_hash] = current_attempt

            if current_attempt >= settings.max_tool_retries:
                # retry limit reached, stop retrying this tool and return a final response
                final_response = f"Stopping: retry limit reached for tool '{tool_name}'."
                messages.append({"role": "assistant", "content": final_response})
                return {
                    "final_response": final_response,
                    "tool_calls": tool_calls,
                    "prompt": full_prompt,
                    "agent": agent,
                    "run": run
                }
            else:
                continue

        successful_calls.add(call_hash)

    final_response = "Final (max iterations reached)."
    messages.append({"role": "assistant", "content": final_response})
    return {
        "final_response": final_response,
        "tool_calls": tool_calls,
        "prompt": full_prompt,
        "agent": agent,
        "run": run
    }