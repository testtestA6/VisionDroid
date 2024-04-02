import SparkApi

appid = "XXXX" 
api_secret = "XXXXX"  
api_key = "XXXXX" 

domain = "XXX"
Spark_url = "XXXXX"


class Spark:
    def __init__(self):
        self.text = []

    def _add_to_text(self, role, content):
        json_con = {"role": role, "content": content}
        self.text.append(json_con)
        return self.text

    @staticmethod
    def _get_length(text):
        length = 0
        for content in text:
            temp = content["content"]
            temp_len = len(temp)
            length += temp_len
        return length

    @staticmethod
    def _check_len(text):
        while Spark._get_length(text) > 8000:
            del text[0]
        return text

    def chat(self, in_text):
        question = Spark._check_len(self._add_to_text("user", in_text))
        SparkApi.answer = ""
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        self._add_to_text("assistant", SparkApi.answer)
        return SparkApi.answer


if __name__ == '__main__':
    s = Spark()
    while True:
        in_text = input("\n" + "XXX:")
        print("XXX:", end="")
        out = s.chat(in_text)
