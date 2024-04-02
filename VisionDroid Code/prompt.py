from info import Global, Page

few_shot = """
Now that you are an automated testing program for Android software,\
what you have to do is test the functionality of the software as completely as possible and check for any problems.\
I will tell you the information of the current program interface.\
by asking questions, and you will tell me the next step of the test by answering.\
When you encounter components with similar names,\
you can look at them as the same category and test one or more of them.\
When you encounter many operation options, you tend to click on them from smallest to largest,\
and tend to click on the component with "menu button" in its name.\
Now that you are an automated testing program for Android software,\
what you have to do is test the functionality of the software as completely as possible and check for any problems.\
I will tell you the information of the current program interface by asking questions,\
and you will tell me the next step of the test by answering.
"""


def generate_global_prompt(global_info: Global):
    prompt = few_shot
    prompt += "We want to test the {} App, which has {} main function pages, namely: ".format(global_info.app_name,
                                                                                              len(global_info.activities))

    # not open source, so there is no activity priority sequence

    # for activity in global_info.activities:
    #     prompt += '"{}", '.format(activity)
    # prompt = prompt[:-2]
    # prompt += '.\nThe recommended test sequence is: '

    for priority in global_info.priority:
        prompt += '"{}", '.format(priority)

    prompt += "If you're clear, please answer \"OK\"."
    return prompt


def generate_prompt(page_info: Page):
    prompt = ""
    prompt += 'The function UI page we are currently testing is "{}".\n'.format(page_info.activity_name)
    prompt += 'The number of exploration recorded on the current page is {}.\n'.format(page_info.visit_times)

    prompt += "Do not select the same choice as before. Now we can do these:\n"

    opt_key_mapping = []
    opt_id = 1
    for widget_key in page_info.layouts.keys():
        if page_info.layouts[widget_key].widget_act != 'click':
            continue
        prompt += '{}. click "{}"\n'.format(str(opt_id), widget_key)
        opt_key_mapping.append(widget_key)
        opt_id += 1
    if not page_info.is_first_page:
        prompt += "{}. return to previous page\n".format(str(opt_id))
    prompt += "Give a number of a choice above only, such as \"1. action\".\n"
    return prompt, opt_key_mapping
