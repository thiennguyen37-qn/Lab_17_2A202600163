import os
import json
from openai import OpenAI
from agent_graph import agent_app, memory_manager, MODEL_NAME

# ===== Load scenarios từ JSON =====
def load_scenarios(path="data/scenarios.json"):
    with open(path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    # Fix dynamic content (scenario 9)
    for sc in scenarios:
        if sc["id"] == 9:
            sc["turns"][0] = "Đây là một đoạn text rất dài: " + ("spam " * 500)

    return scenarios


# ===== Init client =====
client = OpenAI(
    api_key=os.environ.get("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)


def run_no_memory_baseline(turns):
    messages = [{"role": "system", "content": "Bạn là AI. Hãy trả lời ngắn gọn."}]
    
    for t in turns[:-1]:
        messages.append({"role": "user", "content": t})
        messages.append({"role": "assistant", "content": "Vâng, tôi hiểu."})
    
    messages.append({"role": "user", "content": turns[-1]})
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.0,
        max_tokens=500
    )

    content = response.choices[0].message.content
    if content is None:
        content = "Lỗi: API trả về rỗng."

    return content.replace('\n', ' ').strip()


def run_with_memory_agent(turns):
    final_response = ""

    for t in turns:
        result = agent_app.invoke({
            "user_input": t,
            "memory_budget": 4000
        })
        final_response = result['response']

    return final_response.replace('\n', ' ').strip()


if __name__ == "__main__":
    print("Bắt đầu chạy benchmark...")

    SCENARIOS = load_scenarios()

    # preload knowledge
    memory_manager.save_factual_knowledge(
        "Công thức tính diện tích hình chữ nhật là Chiều Dài nhân Chiều Rộng.",
        "math_01"
    )
    memory_manager.save_factual_knowledge(
        "Thủ đô của nước Pháp là Paris.",
        "geo_01"
    )

    markdown_content = "# BÁO CÁO BENCHMARK\n\n"
    markdown_content += "| # | Scenario | Group | No-memory | With-memory | Pass |\n"
    markdown_content += "|---|---|---|---|---|---|\n"

    for sc in SCENARIOS:
        print(f"Running {sc['id']} - {sc['name']}")

        memory_manager.short_term.clear()

        ans_no_mem = run_no_memory_baseline(sc['turns'])
        ans_with_mem = run_with_memory_agent(sc['turns'])

        passed = "✅ Pass" if sc['eval_hint'].lower() in ans_with_mem.lower() else "❌ Fail"

        ans_no_mem_short = (ans_no_mem[:60] + '...') if len(ans_no_mem) > 60 else ans_no_mem
        ans_with_mem_short = (ans_with_mem[:60] + '...') if len(ans_with_mem) > 60 else ans_with_mem

        markdown_content += (
            f"| {sc['id']} | {sc['name']} | {sc['group']} | "
            f"{ans_no_mem_short} | {ans_with_mem_short} | {passed} |\n"
        )

    with open("BENCHMARK.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print("Done! Output: BENCHMARK.md")