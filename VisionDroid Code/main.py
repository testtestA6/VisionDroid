from SparkModel import Spark
from GptModel import GptModel
from action import click, back
from prompt import generate_prompt, generate_global_prompt
import info
import time
from graph import save_screenshot, save_path, save_page_hierarchy, clear_directories

# Use Spark
# s = Spark()

s = GptModel()

if __name__ == '__main__':
    global_info = info.get_global_info(opensource=False)
    prompt_global = generate_global_prompt(global_info)
    status = s.chat(prompt_global)
    page_info = None
    action_cnt = 0
    clear_directories()
    while True:
        page_info = info.get_page_info(global_info, page_info)
        save_page_hierarchy(str(action_cnt + 1))
        prompt, opt_key_mapping = generate_prompt(info.page_db_fetch(page_info))
        print(prompt)
        output = s.chat(prompt)
        print("============")
        print(output)
        print("============")
        #  Action: 1
        output = output.lower().replace("action:", "").strip()
        choice = int(output.split(".")[0]) - 1

        print(choice)
        print("============")
        if choice == len(opt_key_mapping):
            save_screenshot(str(action_cnt + 1), None)
            save_path(page_info, str(action_cnt))
            back()
        else:
            save_screenshot(str(action_cnt + 1), page_info.layouts[opt_key_mapping[choice]])
            save_path(page_info, str(action_cnt), page_info.layouts[opt_key_mapping[choice]])
            click(page_info.layouts[opt_key_mapping[choice]])
        time.sleep(2.0)
        action_cnt += 1

