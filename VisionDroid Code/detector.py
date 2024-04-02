import requests, time
import base64, os
import fire

def getPrompt():
    prompt = ("The common categories of inter-page no-crash bugs include: data operation failure, media control not responding, numerical calculation errors, setting and configuration failures, navigation and linking errors. We provide the example of inter-page bug descriptions: (1) The personal income addition function has failed to add, and the a bug path is as follows: \n"
              + "1) Please be a tester to test the [XXX] App. It has the following activities, including [XX, XXX]. The operable components on the image have been marked with red boxes. \n"
              + "2) The image shows a test sequence arranged in order from left to right and from top to bottom. Each screenshot is labeled with a different colored bounding box indicating the action of the operation (red as click, blue as input,...). Below the screenshot is the corresponding function name. I have numbered each operable component in order from top to bottom and left to right. The number corresponding to the first component of each row is marked in the upper left corner of the row, and the other numbers in the row can be deduced in sequence.\n"
              + "Output Example:\n"
              + "1) Does the current page meet expectations? No. If not, the component number that does not meet expectations: (xx). \nIs there a bug on the page? Yes If yes, the component number with the bug: xx.\n"
              + "2) Component number requiring next step operation: xx; Text of the component in the screenshot: xx; Operation status: Click; Current page: xxx; Operation expectation: After clicking xx, it is expected to enter the xx page.\n"
              + "3) Component number: xx; Text of the component in the screenshot: xx; Operation status: Input; Input content: xx; Current page: xxx; Operation expectation: After clicking xx, it is expected to enter the xx page.\n"
              + "Please analyze each step in the test sequence in the image based on the description and examples of the bugs, predict whether the page that transits after each step meets your expectation, use this to determine whether there are any bugs, and point out the bug page."
    )

    return prompt


def get_response_from_lm(images):
    api_key = "xxxxx"

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = getPrompt()
    msg = [{
                "type": "text",
                "text": prompt
            }]
    for image in images:
        image_path = image
        base64_image = encode_image(image_path)
        msg_cur = {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        msg.append(msg_cur)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-xxxx",
        "messages": [
        {
            "role": "user",
            "content": msg
        }
        ],
        "max_tokens": 3000
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    outputs = response.json()['choices'][0]['message']['content'].strip()
    # print(response.json())
    if 'choices' not in response.json():
        print('Sleep!')
        time.sleep(15 * 60)
    # print('Model Output: ', outputs)

    return outputs

def postprocess(content):
    import re
    c_list = content.split('\n\n')
    res_dict = dict()
    for item in c_list:
        item = item.strip()
        if item.startswith('1)'):
            if 'yes' in item.lower():
                res_dict['bug'] = -1
            else:
                numbers = re.findall(r'\d+', item)
                bug_num = numbers[-1]
                res_dict['bug'] = bug_num
        elif item.startswith('2)'):
            numbers = re.findall(r'\d+', item)
            action_num = numbers[-1]
            res_dict['action'] = action_num
        elif item.startswith('3)'):
            numbers = re.findall(r'\d+', item)
            action_num = numbers[-1]
            res_dict['next_page'] = action_num
    
    return res_dict

def filter(actions, end_num, start_num=1):
    new_actions = []
    for item in actions:
        if item[1] >= start_num and item[1] <= end_num:
            new_actions.append(item)

    return new_actions

def community(nodes, edges):
    import networkx as nx
    import community 
    G = nx.Graph()
    sub_dict = dict()

    G.add_nodes_from([1, 2, 3, 4, 5])
    G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5)])
    partition = community.best_partition(G)
    for k in partition.keys():
        v = partition[k]
        if v not in sub_dict.keys():
            sub_dict[v] = [k]
        else:
            sub_dict[v].append(k)

    return sub_dict

# dir = 'Scene_1/annotated_image'
# for image in os.listdir(dir):

def run():
     
    dir_path = 'Scene_1/annotated_image'

    memory = []
    memory_action = []
    images = []
    num = 1
    for image in os.listdir(dir_path):
        image = os.path.join(dir_path, image)
        print('Image: ', image)
        memory.append(num)
        images.append(image)
        num += 1

        file_path = image

        output = ''
        times = 0
        while '\n' not in output and times < 5:
            output = get_response_from_lm([file_path])
            times += 1
        # print(output)

        res_dict = postprocess(output)
        if 'next_page' in res_dict.keys():
            next = int(res_dict['next_page'])
            memory_action.append((num, next))

        print(res_dict)
    print('Memory: ', memory)
    memory_action = filter(memory_action, num-1)
    print('Action: ', memory_action)
    sub_dict = community(memory, memory_action)
    for k in sub_dict.keys():
        sub_list = sub_dict[k]
        sub_img = []
        for num in sub_list:
            img_path = images[num-1]
            sub_img.append(img_path)

        output = ''
        times = 0
        while '\n' not in output and times < 5:
            output = get_response_from_lm(sub_img)
            times += 1
        # print(output)

        res_dict = postprocess(output)
        if 'next_page' in res_dict.keys():
            next = int(res_dict['next_page'])
            memory_action.append((num, next))

        print(res_dict)


if __name__ == '__main__':
    fire.Fire(run)    
