import datetime as dt
import random

class Password:
    special_char_dict = {'e':'3', 'o':'0', 'a':'@', 's':'$'}
    
    def __init__(self, min_length, sentence, has_upper_case = True, has_special_char = True) -> str:
        self.min_length = min_length
        self.sentence = sentence
        self.has_upper_case = has_upper_case
        self.has_special_char = has_special_char
        self.today = dt.date.today()

    def generate_password(self) -> str:
        """
        TODO: docstring test and documentation
        """
        new_sentence = self.sentence
        if self.has_special_char:
            for letter in new_sentence:
                if letter.lower() in self.special_char_dict:
                    if random.randrange(0,2) == 0:
                        new_sentence = str.replace(new_sentence, letter, self.special_char_dict[letter.lower()])
        word_list = new_sentence.split(" ")
        if self.has_upper_case:
            word_list = [word.capitalize() for word in word_list]
        new_sentence = "".join(word_list) + str(self.today.day) + str(self.today.month)
        return new_sentence

if __name__ == '__main__':
    pw = Password(8, "Sad Autumn Girl")
    print(pw.generate_password())