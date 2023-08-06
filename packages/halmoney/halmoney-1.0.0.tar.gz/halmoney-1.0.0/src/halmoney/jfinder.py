# -*- coding: utf-8 -*-
import re

class jfinder:
    def __init__(self):
        pass

    def manual(self):
        result = """
            이것을 만든 이유는 정규표현식이 업무에 사용하기 편한것인데
            일반적인 사람들이 읽고 사용하기가 어려워
            쉽게 사용할수있도록 만들어 본것이다
            그래서 일부 형식은 기존 정규표현식을 따라간것들도 있다
            단, 너무 복잡한 표현식은 
    
            전반적인 설정을 할때는 괄호를 사용해서 나타내었다 ==> (대소문자무시)(여러줄)(개행문자포함)(최소찾기)
                가능한한 설정은 제일 앞부분에 나타내기를 바란다
                (최소찾기) ==> 최소단어찾기를 위한 설정
                (대소문자무시) ==> re.IGNORECASE 대소문자 무시
                (여러줄)  ==> re.MULITILINE 여러줄도 실행
                (개행문자포함)  ==> # re.DOTALL 개행문자도 포함
            or는 |로 사용
                "(010|016|019)-[숫자:3~4]-[숫자:3~4]" ==> 또는 을 사용할때는 가급적 괄호를 사용하는것을 추천한다
            갯수를 지정할때는 1~3과같이 물결무늬를 이용해서 나타내었다 ==> 숫자가 0개~3개일때 ==> [숫자:0~3] 
                대괄호를 사용하여 구분 한다, 갯수는 ~를 사용한다,
                보통사용하는 re구문을 그대로 사용하여도 적용된다. 단 너무 복잡한것은 오류가 날 가능성도 있다
                일반적인 사용법 => "[맨앞][한글:3~3][영어:0~2]"
            문자하나가 아니고 단어자체가 반복을 하는 경우를 찾아야하는경우도 이ㅆ다 이렬경우는
                단어를 반복할때는 : [단어(abc):3~4]  => (abc){3,4}
            문자의 앞뒤에 조건이 붙는 경우
                (앞에있음:문자)
            특수문자나 일반 문자를 대괄호에 그대로 사용하여도 된다
                특수문자(".^ $ *+ ? {}[] \ | ()")의 사용법 => [.$:3~4]
            일본어나 중국어등의 문자열등을 추가하고 싶을때는 위의 리스트를 변경하면 된다
            """
        return result

    def ezre (self, input_data):
        result = input_data.replace(" ", "")

        setup_list = [
            ["(대소문자무시)", "(?!)"], #re.IGNORECASE 대소문자 무시
            ["(여러줄)", "(?m)"], # re.MULITILINE 여러줄도 실행
            ["(개행문자포함)", "(?s)"], # re.DOTALL 개행문자도 포함
            ]

        for one in setup_list:
            result = result.replace(one[0], one[1])

        basic_list = [
            [":(\d+)[~](\d*)[\]]",             "]{\\1,\\2}"], # :3~4] ==> ]{3,4}
            ["[\[](\d+)[~](\d*)[\]]",          "{\\1,\\2}"], # [3~4] ==> {3,4}

            ["\(뒤에있음:(.*)\)",                "(?=\\1)" ], #(뒤에있음:(abc)) => (?=abc)
            ["\(뒤에없음:(.*)\)",                "(?!\\1)" ], #(뒤에없음:(abc)) => (?!abc)
            ["\(앞에있음:(.*)\)",                "(?<=\\1)"], #(앞에있음:(abc)) => (?<=abc)
            ["\(앞에없음:(.*)\)",                "(?<!\\1)"], #(앞에없음:(abc)) => (?<!abc)

            ["([\[]?)한글모음[&]?([\]]?)",       "\\1ㅏ-ㅣ\\2"], #[ㅏ-ㅣ]
            ["([\[]?)한글[&]?([\]]?)",          "\\1ㄱ-ㅎ|ㅏ-ㅣ|가-힣\\2"],
            ["([\[]?)숫자[&]?([\]]?)",          "\\1 0-9 \\2"],
            ["([\[]?)영어대문자[&]?([\]]?)",     "\\1A-Z\\2"],
            ["([\[]?)영어소문자[&]?([\]]?)",     "\\1a-z\\2"],
            ["([\[]?)영어[&]?([\]]?)",          "\\1a-zA-Z\\2"],
            ["([\[]?)일본어[&]?([\]]?)",        "\\1ぁ-ゔ|ァ-ヴー|々〆〤\\2"],
            ["([\[]?)한자[&]?([\]]?)",          "\\1一-龥\\2"],
            ["([\[]?)특수문자[&]?([\]]?)",       "\\1 @#$&-_ \\2"],
            ["([\[]?)문자[&]?([\]]?)",          "."],
            ["([\[]?)공백[&]?([\]]?)",          "\\1\\\s\\2"],

            ["[\[]단어([(].*?[)])([\]]?)",      "\\1"],
            ["[\[]또는([(].*?[)])([\]]?)",      "\\1|"],
            ["[\(]이름<(.+?)>(.+?)[\)]",        "?P<\\1>\\2"], #[이름<abc>표현식]
            ]

        for one in basic_list:
            result = re.sub(one[0], one[1], result)
            result = result.replace(" ", "")

        simple_list = [
            ['[처음]', '^'], ['[맨앞]', '^'], ['[시작]', '^'],
            ['[맨뒤]', '$'], ['[맨끝]', '$'], ['[끝]', '$'],
            ['[또는]', '|'], ['또는', '|'],['or', '|'],
            ['not', '^'],
            ]

        for one in simple_list:
            result = result.replace(one[0], one[1])

        #최대탐색을 할것인지 최소탐색을 할것인지 설정하는 것이다
        if "(최소찾기)" in result:
            result = result.replace("[1,]","+")
            result = result.replace("[1,]","*")

            result = result.replace("+","+?")
            result = result.replace("*","*?")
            result = result.replace("(최소찾기)","")


        #이단계를 지워도 실행되는데는 문제 없으며, 실행 시키지 않았을때가 약간 더 읽기는 편하다
        high_list = [
            ['[^a-zA-Z0-9]', '\W'],
            ['[^0-9a-zA-Z]', '\W'],
            ['[a-zA-Z0-9]', '\w'],
            ['[0-9a-zA-Z]', '\w'],
            ['[^0-9]', '\D'],
            ['[0-9]', '\d'],
            ['{0,}', '*'],
            ['{1,}', '+'],
            ]

        for one in high_list:
            result = result.replace(one[0], one[1])



        return result

    def run_search (self, re_sql, source_text):
        #조건에 맞는것을 찾아서 여러개가 있을경우 리수트로 돌려주는 것이다
        re_compiled = re.compile(re_sql)
        result = re_compiled.findall(source_text)
        return result

    def run_replace (self, re_sql, source_text, replace_word):
        #조건에 맞는 것을 변경하는 것이다
        re_compiled = re.compile(re_sql)
        result = re_compiled.sub(replace_word, source_text)
        return result

    def run (self, ezre_sql, source_text):
        #결과값을 얻는것이 여러조건들이 있어서 이것을 하나로 만듦
        # [[결과값, 시작순서, 끝순서, [그룹1, 그룹2...], match결과].....]
        re_sql = self.ezre(ezre_sql)
        re_com = re.compile(re_sql)
        result_match = re_com.match(source_text)
        result_finditer = re_com.finditer(source_text)

        final_result = []
        num=0
        for one_iter in result_finditer:
            temp=[]
            #찾은 결과값과 시작과 끝의 번호를 넣는다
            temp.append(one_iter.group())
            temp.append(one_iter.start())
            temp.append(one_iter.end())

            #그룹으로 된것을 넣는것이다
            temp_sub = []
            if len(one_iter.group()):
                for one in one_iter.groups():
                    temp_sub.append(one)
                temp.append(temp_sub)
            else:
                temp.append(temp_sub)

            #제일 첫번째 결과값에 match랑 같은 결과인지 넣는것
            if num == 0: temp.append(result_match)
            final_result.append(temp)
            num+=1
        return final_result